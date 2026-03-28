"""Gradebook URL patterns."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "gradebook"

router = DefaultRouter()
router.register(r"scales", views.GradeScaleViewSet, basename="grade-scale")
router.register(r"gradebooks", views.GradeBookViewSet, basename="gradebook")
router.register(r"entries", views.GradeEntryViewSet, basename="grade-entry")

urlpatterns = [
    path("", include(router.urls)),
    # Nested entries for a specific gradebook
    path(
        "gradebooks/<uuid:gradebook_pk>/entries/",
        views.GradeEntryViewSet.as_view({"get": "list", "post": "create"}),
        name="gradebook-entries",
    ),
    path(
        "gradebooks/<uuid:gradebook_pk>/entries/<uuid:pk>/",
        views.GradeEntryViewSet.as_view({
            "get": "retrieve", "put": "update",
            "patch": "partial_update", "delete": "destroy",
        }),
        name="gradebook-entry-detail",
    ),
]
