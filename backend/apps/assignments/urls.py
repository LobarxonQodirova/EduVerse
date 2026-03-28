"""Assignment URL patterns."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "assignments"

router = DefaultRouter()
router.register(r"assignments", views.AssignmentViewSet, basename="assignment")
router.register(r"submissions", views.SubmissionViewSet, basename="submission")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "submissions/<uuid:submission_pk>/grade/",
        views.GradeCreateView.as_view(),
        name="submission-grade",
    ),
    path(
        "submissions/<uuid:submission_pk>/feedback/",
        views.FeedbackViewSet.as_view({"get": "list", "post": "create"}),
        name="submission-feedback-list",
    ),
    path(
        "submissions/<uuid:submission_pk>/feedback/<uuid:pk>/",
        views.FeedbackViewSet.as_view({"patch": "partial_update", "delete": "destroy"}),
        name="submission-feedback-detail",
    ),
]
