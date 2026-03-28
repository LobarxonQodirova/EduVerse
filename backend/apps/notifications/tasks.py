"""Celery tasks for notification delivery and deadline reminders."""
import logging
from datetime import timedelta
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def send_deadline_reminders():
    """Send reminder notifications for upcoming deadlines (next 24 hours)."""
    from apps.calendar.models import Deadline
    from apps.courses.models import Enrollment
    from .services import NotificationService

    now = timezone.now()
    tomorrow = now + timedelta(hours=24)

    deadlines = Deadline.objects.filter(
        due_date__gte=now,
        due_date__lte=tomorrow,
        reminder_sent=False,
    ).select_related("course")

    sent_count = 0
    for deadline in deadlines:
        enrollments = Enrollment.objects.filter(
            course=deadline.course, is_active=True
        ).select_related("student")

        for enrollment in enrollments:
            NotificationService.notify_deadline_reminder(
                student=enrollment.student,
                deadline=deadline,
            )
            sent_count += 1

        deadline.reminder_sent = True
        deadline.save(update_fields=["reminder_sent"])

    logger.info("Sent %d deadline reminder notifications.", sent_count)


@shared_task
def send_weekly_progress_digest():
    """Send a weekly progress digest email to all active students."""
    from apps.accounts.models import User
    from apps.progress.models import StudentProgress
    from django.core.mail import send_mail
    from django.conf import settings

    students = User.objects.filter(role="student", is_active=True)
    sent_count = 0

    for student in students.iterator():
        active_courses = StudentProgress.objects.filter(
            student=student, progress_percent__lt=100
        ).select_related("course")[:5]

        if not active_courses:
            continue

        lines = []
        for progress in active_courses:
            lines.append(
                f"  - {progress.course.title}: {progress.progress_percent}% complete"
            )

        body = (
            f"Hi {student.first_name},\n\n"
            f"Here's your weekly learning progress:\n\n"
            + "\n".join(lines)
            + "\n\nKeep up the great work!\nThe EduVerse Team"
        )

        try:
            send_mail(
                subject="Your Weekly Learning Progress - EduVerse",
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[student.email],
                fail_silently=True,
            )
            sent_count += 1
        except Exception as exc:
            logger.error("Failed to send digest to %s: %s", student.email, exc)

    logger.info("Sent weekly progress digest to %d students.", sent_count)


@shared_task
def cleanup_old_notifications(days_old=90):
    """Delete read notifications older than the specified number of days."""
    from .models import Notification

    cutoff = timezone.now() - timedelta(days=days_old)
    count, _ = Notification.objects.filter(
        is_read=True, created_at__lt=cutoff
    ).delete()
    logger.info("Cleaned up %d old read notifications.", count)


@shared_task(bind=True, max_retries=3)
def send_email_notification_async(self, notification_id):
    """Asynchronously send an email for a notification."""
    from .models import Notification
    from .services import NotificationService

    try:
        notification = Notification.objects.get(pk=notification_id)
        if not notification.is_email_sent:
            NotificationService._send_email_notification(notification)
    except Notification.DoesNotExist:
        logger.warning("Notification %s not found.", notification_id)
    except Exception as exc:
        logger.error("Error sending email for notification %s: %s", notification_id, exc)
        self.retry(exc=exc, countdown=120)
