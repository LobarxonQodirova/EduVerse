"""Analytics URL patterns."""
from django.urls import path
from . import views

app_name = "analytics"

urlpatterns = [
    path(
        "instructor/dashboard/",
        views.InstructorDashboardView.as_view(),
        name="instructor-dashboard",
    ),
    path(
        "courses/<uuid:course_pk>/",
        views.CourseAnalyticsView.as_view(),
        name="course-analytics",
    ),
    path(
        "courses/<uuid:course_pk>/timeline/",
        views.CourseAnalyticsTimelineView.as_view(),
        name="course-analytics-timeline",
    ),
    path(
        "platform/",
        views.PlatformAnalyticsView.as_view(),
        name="platform-analytics",
    ),
    path(
        "student/dashboard/",
        views.StudentAnalyticsView.as_view(),
        name="student-dashboard",
    ),
]
