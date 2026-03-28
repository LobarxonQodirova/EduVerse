"""Analytics views: instructor dashboard, course analytics, and platform stats."""
from rest_framework import views, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsInstructor, IsInstructorOrAdmin, IsAdminUser
from apps.courses.models import Course
from .models import CourseAnalytics, PlatformAnalytics
from .services import AnalyticsService


class InstructorDashboardView(views.APIView):
    """Aggregated dashboard stats for an instructor."""

    permission_classes = [IsAuthenticated, IsInstructor]

    def get(self, request):
        stats = AnalyticsService.get_instructor_dashboard(request.user)
        return Response(stats)


class CourseAnalyticsView(views.APIView):
    """Detailed analytics for a specific course."""

    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]

    def get(self, request, course_pk):
        try:
            course = Course.objects.get(pk=course_pk, instructor=request.user)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=404)

        summary = AnalyticsService.get_course_analytics_summary(course)
        return Response(summary)


class CourseAnalyticsTimelineView(views.APIView):
    """Daily analytics timeline for a course."""

    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]

    def get(self, request, course_pk):
        try:
            course = Course.objects.get(pk=course_pk, instructor=request.user)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=404)

        days = int(request.query_params.get("days", 30))
        records = CourseAnalytics.objects.filter(
            course=course
        ).order_by("-date")[:days]

        data = [
            {
                "date": r.date.isoformat(),
                "views": r.views,
                "unique_visitors": r.unique_visitors,
                "new_enrollments": r.new_enrollments,
                "completions": r.completions,
                "avg_progress": float(r.avg_progress),
                "total_watch_time_minutes": r.total_watch_time_minutes,
            }
            for r in records
        ]
        return Response(data)


class PlatformAnalyticsView(views.APIView):
    """Platform-wide analytics (admin only)."""

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        records = PlatformAnalytics.objects.order_by("-date")[:days]

        data = [
            {
                "date": r.date.isoformat(),
                "total_users": r.total_users,
                "new_users": r.new_users,
                "active_users": r.active_users,
                "total_courses": r.total_courses,
                "new_courses": r.new_courses,
                "total_enrollments": r.total_enrollments,
                "new_enrollments": r.new_enrollments,
                "total_completions": r.total_completions,
                "total_revenue": float(r.total_revenue),
            }
            for r in records
        ]
        return Response(data)


class StudentAnalyticsView(views.APIView):
    """Analytics dashboard for a student (their own stats)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.progress.services import ProgressService
        stats = ProgressService.get_student_dashboard_stats(request.user)
        return Response(stats)
