"""Course URL patterns with nested routing for sections and lessons."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from . import views

app_name = "courses"

router = DefaultRouter()
router.register(r"categories", views.CourseCategoryViewSet, basename="category")
router.register(r"enrollments", views.EnrollmentViewSet, basename="enrollment")
router.register(r"", views.CourseViewSet, basename="course")

# Nested routes: /courses/{course_pk}/sections/
course_router = nested_routers.NestedDefaultRouter(router, r"", lookup="course")
course_router.register(r"sections", views.SectionViewSet, basename="course-section")

# Nested routes: /courses/{course_pk}/sections/{section_pk}/lessons/
section_router = nested_routers.NestedDefaultRouter(course_router, r"sections", lookup="section")
section_router.register(r"lessons", views.LessonViewSet, basename="section-lesson")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(course_router.urls)),
    path("", include(section_router.urls)),
]
