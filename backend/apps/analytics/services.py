"""Analytics service layer for generating reports and aggregating data."""
import logging
from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone

from apps.accounts.models import User
from apps.courses.models import Course, Enrollment
from apps.progress.models import StudentProgress, CompletionRecord
from apps.quizzes.models import QuizResult
from apps.assignments.models import Grade
from .models import CourseAnalytics, PlatformAnalytics

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for computing and caching analytics data."""

    @staticmethod
    def get_instructor_dashboard(instructor):
        """Aggregate dashboard stats for an instructor."""
        courses = Course.objects.filter(instructor=instructor)
        course_ids = courses.values_list("id", flat=True)

        total_courses = courses.count()
        published_courses = courses.filter(status="published").count()
        total_students = Enrollment.objects.filter(
            course_id__in=course_ids, is_active=True
        ).values("student").distinct().count()
        total_enrollments = Enrollment.objects.filter(
            course_id__in=course_ids, is_active=True
        ).count()

        avg_rating = courses.aggregate(avg=Avg("average_rating"))["avg"] or 0
        avg_completion = StudentProgress.objects.filter(
            course_id__in=course_ids
        ).aggregate(avg=Avg("progress_percent"))["avg"] or 0

        return {
            "total_courses": total_courses,
            "published_courses": published_courses,
            "total_students": total_students,
            "total_enrollments": total_enrollments,
            "average_rating": round(float(avg_rating), 2),
            "average_completion_rate": round(float(avg_completion), 1),
        }

    @staticmethod
    def get_course_analytics_summary(course):
        """Get a summary of analytics for a specific course."""
        enrollments = Enrollment.objects.filter(course=course, is_active=True)
        progress_records = StudentProgress.objects.filter(course=course)

        total_enrolled = enrollments.count()
        completed = progress_records.filter(progress_percent__gte=100).count()
        avg_progress = progress_records.aggregate(
            avg=Avg("progress_percent")
        )["avg"] or 0

        # Quiz performance
        quiz_results = QuizResult.objects.filter(attempt__quiz__course=course)
        avg_quiz_score = quiz_results.aggregate(
            avg=Avg("percentage")
        )["avg"] or 0
        quiz_pass_rate = 0
        if quiz_results.exists():
            passed = quiz_results.filter(passed=True).count()
            quiz_pass_rate = round((passed / quiz_results.count()) * 100, 1)

        # Assignment performance
        grades = Grade.objects.filter(submission__assignment__course=course)
        avg_assignment_score = grades.aggregate(
            avg=Avg("percentage")
        )["avg"] or 0

        # Engagement: recent 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_completions = CompletionRecord.objects.filter(
            course=course, completed_at__gte=thirty_days_ago
        ).count()

        return {
            "total_enrolled": total_enrolled,
            "total_completed": completed,
            "completion_rate": round((completed / total_enrolled) * 100, 1) if total_enrolled > 0 else 0,
            "average_progress": round(float(avg_progress), 1),
            "average_quiz_score": round(float(avg_quiz_score), 1),
            "quiz_pass_rate": quiz_pass_rate,
            "average_assignment_score": round(float(avg_assignment_score), 1),
            "recent_lesson_completions_30d": recent_completions,
        }

    @staticmethod
    def generate_daily_course_analytics(date=None):
        """Generate daily analytics snapshots for all published courses."""
        if date is None:
            date = timezone.now().date() - timedelta(days=1)

        courses = Course.objects.filter(status="published")
        created_count = 0

        for course in courses.iterator():
            new_enrollments = Enrollment.objects.filter(
                course=course, enrolled_at__date=date
            ).count()
            completions = StudentProgress.objects.filter(
                course=course, completed_at__date=date
            ).count()
            avg_prog = StudentProgress.objects.filter(
                course=course
            ).aggregate(avg=Avg("progress_percent"))["avg"] or 0

            CourseAnalytics.objects.update_or_create(
                course=course,
                date=date,
                defaults={
                    "new_enrollments": new_enrollments,
                    "completions": completions,
                    "avg_progress": round(float(avg_prog), 2),
                },
            )
            created_count += 1

        logger.info("Generated daily analytics for %d courses on %s", created_count, date)

    @staticmethod
    def generate_daily_platform_analytics(date=None):
        """Generate a daily platform-wide analytics snapshot."""
        if date is None:
            date = timezone.now().date() - timedelta(days=1)

        total_users = User.objects.filter(is_active=True).count()
        new_users = User.objects.filter(created_at__date=date).count()
        active_users = User.objects.filter(last_login__date=date).count()
        total_courses = Course.objects.filter(status="published").count()
        new_courses = Course.objects.filter(published_at__date=date).count()
        total_enrollments = Enrollment.objects.filter(is_active=True).count()
        new_enrollments = Enrollment.objects.filter(enrolled_at__date=date).count()
        total_completions = StudentProgress.objects.filter(
            progress_percent__gte=100
        ).count()

        PlatformAnalytics.objects.update_or_create(
            date=date,
            defaults={
                "total_users": total_users,
                "new_users": new_users,
                "active_users": active_users,
                "total_courses": total_courses,
                "new_courses": new_courses,
                "total_enrollments": total_enrollments,
                "new_enrollments": new_enrollments,
                "total_completions": total_completions,
            },
        )
        logger.info("Generated platform analytics for %s", date)
