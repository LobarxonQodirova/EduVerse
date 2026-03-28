"""Notification service for creating and dispatching notifications."""
import logging
from django.conf import settings as django_settings
from django.core.mail import send_mail

from .models import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """Centralized service for creating and sending notifications."""

    @staticmethod
    def create_notification(
        recipient,
        title,
        message,
        notification_type=Notification.NotificationType.SYSTEM,
        link="",
        related_course=None,
        metadata=None,
        send_email=False,
    ):
        """Create an in-app notification and optionally send an email."""
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            related_course=related_course,
            metadata=metadata or {},
        )

        if send_email:
            NotificationService._send_email_notification(notification)

        logger.info(
            "Notification created: [%s] %s -> %s",
            notification_type, title, recipient.email,
        )
        return notification

    @staticmethod
    def _send_email_notification(notification):
        """Send an email for a notification."""
        try:
            send_mail(
                subject=notification.title,
                message=notification.message,
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.recipient.email],
                fail_silently=False,
            )
            notification.is_email_sent = True
            notification.save(update_fields=["is_email_sent"])
        except Exception as exc:
            logger.error(
                "Failed to send email notification %s: %s",
                notification.id, exc,
            )

    @staticmethod
    def notify_enrollment(student, course):
        """Notify a student about successful enrollment."""
        return NotificationService.create_notification(
            recipient=student,
            title=f"Enrolled in {course.title}",
            message=f"You have been successfully enrolled in \"{course.title}\". Start learning now!",
            notification_type=Notification.NotificationType.ENROLLMENT,
            link=f"/courses/{course.id}",
            related_course=course,
            send_email=True,
        )

    @staticmethod
    def notify_assignment_graded(student, assignment, grade):
        """Notify a student that their assignment has been graded."""
        return NotificationService.create_notification(
            recipient=student,
            title=f"Assignment Graded: {assignment.title}",
            message=(
                f"Your submission for \"{assignment.title}\" has been graded. "
                f"Score: {grade.score}/{grade.max_score} ({grade.letter_grade})"
            ),
            notification_type=Notification.NotificationType.GRADE,
            link=f"/assignments/{assignment.id}",
            related_course=assignment.course,
            metadata={"assignment_id": str(assignment.id), "grade_id": str(grade.id)},
            send_email=True,
        )

    @staticmethod
    def notify_new_discussion_reply(thread, reply):
        """Notify the thread author about a new reply."""
        if reply.author == thread.author:
            return None
        return NotificationService.create_notification(
            recipient=thread.author,
            title=f"New reply on: {thread.title}",
            message=f"{reply.author.full_name} replied to your discussion thread.",
            notification_type=Notification.NotificationType.DISCUSSION,
            link=f"/discussions/threads/{thread.id}",
            related_course=thread.forum.course,
            metadata={"thread_id": str(thread.id), "reply_id": str(reply.id)},
        )

    @staticmethod
    def notify_deadline_reminder(student, deadline):
        """Send a deadline reminder notification."""
        return NotificationService.create_notification(
            recipient=student,
            title=f"Upcoming Deadline: {deadline.title}",
            message=(
                f"Reminder: \"{deadline.title}\" is due on "
                f"{deadline.due_date.strftime('%B %d, %Y at %I:%M %p')}."
            ),
            notification_type=Notification.NotificationType.DEADLINE,
            link=f"/calendar",
            related_course=deadline.course,
            metadata={"deadline_id": str(deadline.id)},
            send_email=True,
        )

    @staticmethod
    def notify_certificate_issued(student, certificate):
        """Notify a student that their certificate has been issued."""
        return NotificationService.create_notification(
            recipient=student,
            title=f"Certificate Earned: {certificate.course.title}",
            message=(
                f"Congratulations! You have earned a certificate for completing "
                f"\"{certificate.course.title}\". Certificate #: {certificate.certificate_number}"
            ),
            notification_type=Notification.NotificationType.CERTIFICATE,
            link=f"/certificates/{certificate.id}",
            related_course=certificate.course,
            metadata={"certificate_id": str(certificate.id)},
            send_email=True,
        )

    @staticmethod
    def mark_all_read(user):
        """Mark all notifications as read for a user."""
        count = Notification.objects.filter(
            recipient=user, is_read=False
        ).update(is_read=True)
        return count

    @staticmethod
    def get_unread_count(user):
        """Get the count of unread notifications for a user."""
        return Notification.objects.filter(
            recipient=user, is_read=False
        ).count()
