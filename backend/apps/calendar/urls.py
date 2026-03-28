"""Calendar URL patterns."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "calendar"

router = DefaultRouter()
router.register(r"events", views.EventViewSet, basename="event")
router.register(r"deadlines", views.DeadlineViewSet, basename="deadline")
router.register(r"schedules", views.ScheduleViewSet, basename="schedule")

urlpatterns = [
    path("", include(router.urls)),
]
