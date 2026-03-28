"""Celery tasks for the courses app."""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def recalculate_course_stats_task(self, course_id):
    """Recalculate statistics for a single course (lessons, duration, enrollments)."""
    from .models import Course
    from .services import CourseService

    try:
        course = Course.objects.get(pk=course_id)
        CourseService.recalculate_course_stats(course)
        logger.info("Recalculated stats for course: %s", course.title)
    except Course.DoesNotExist:
        logger.warning("Course %s not found for stats recalculation.", course_id)
    except Exception as exc:
        logger.error("Error recalculating course %s stats: %s", course_id, exc)
        self.retry(exc=exc, countdown=60)


@shared_task
def recalculate_all_course_stats():
    """Periodic task to recalculate stats for all published courses."""
    from .models import Course
    from .services import CourseService

    courses = Course.objects.filter(status="published")
    count = 0
    for course in courses.iterator():
        try:
            CourseService.recalculate_course_stats(course)
            count += 1
        except Exception as exc:
            logger.error("Failed to recalculate stats for course %s: %s", course.id, exc)
    logger.info("Recalculated stats for %d published courses.", count)


@shared_task
def send_enrollment_confirmation(enrollment_id):
    """Send an enrollment confirmation email to the student."""
    from .models import Enrollment
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        enrollment = Enrollment.objects.select_related("student", "course").get(pk=enrollment_id)
        student = enrollment.student
        course = enrollment.course

        send_mail(
            subject=f"Enrollment Confirmed: {course.title}",
            message=(
                f"Hi {student.first_name},\n\n"
                f"You have been successfully enrolled in \"{course.title}\".\n"
                f"Start learning now at your dashboard.\n\n"
                f"Happy learning!\nThe EduVerse Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[student.email],
            fail_silently=False,
        )
        logger.info("Enrollment confirmation sent to %s for course %s", student.email, course.title)
    except Enrollment.DoesNotExist:
        logger.warning("Enrollment %s not found for confirmation email.", enrollment_id)


@shared_task
def archive_stale_draft_courses(days_old=180):
    """Archive draft courses that have not been updated for a long time."""
    from .models import Course

    cutoff = timezone.now() - timezone.timedelta(days=days_old)
    stale = Course.objects.filter(status="draft", updated_at__lt=cutoff)
    count = stale.update(status="archived")
    logger.info("Archived %d stale draft courses older than %d days.", count, days_old)
