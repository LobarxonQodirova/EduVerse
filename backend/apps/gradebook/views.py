"""Gradebook views: view and manage grades for courses."""
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsInstructor, IsInstructorOrAdmin
from .models import GradeBook, GradeEntry, GradeScale
from .serializers import (
    GradeBookSerializer,
    GradeBookSummarySerializer,
    GradeEntrySerializer,
    GradeScaleSerializer,
)


class GradeScaleViewSet(viewsets.ModelViewSet):
    """Manage grading scales."""

    serializer_class = GradeScaleSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]
    queryset = GradeScale.objects.all()


class GradeBookViewSet(viewsets.ModelViewSet):
    """View and manage gradebooks. Students see their own; instructors see course students."""

    permission_classes = [IsAuthenticated]
    filterset_fields = ["course", "student"]

    def get_queryset(self):
        user = self.request.user
        qs = GradeBook.objects.select_related("student", "course", "grade_scale")
        if user.role == "student":
            qs = qs.filter(student=user)
        elif user.role == "instructor":
            qs = qs.filter(course__instructor=user)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return GradeBookSummarySerializer
        return GradeBookSerializer

    @action(detail=True, methods=["post"])
    def recalculate(self, request, pk=None):
        """Recalculate the overall grade for a gradebook."""
        gradebook = self.get_object()
        gradebook.recalculate()
        return Response(GradeBookSerializer(gradebook).data)

    @action(detail=False, methods=["get"])
    def my_grades(self, request):
        """Get the authenticated student's gradebooks across all courses."""
        gradebooks = GradeBook.objects.filter(
            student=request.user
        ).select_related("course", "grade_scale")
        serializer = GradeBookSummarySerializer(gradebooks, many=True)
        return Response(serializer.data)


class GradeEntryViewSet(viewsets.ModelViewSet):
    """Manage individual grade entries within a gradebook."""

    serializer_class = GradeEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = GradeEntry.objects.select_related("gradebook__student", "gradebook__course")
        if user.role == "student":
            qs = qs.filter(gradebook__student=user)
        elif user.role == "instructor":
            qs = qs.filter(gradebook__course__instructor=user)
        if "gradebook_pk" in self.kwargs:
            qs = qs.filter(gradebook_id=self.kwargs["gradebook_pk"])
        return qs

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsInstructor()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        entry = serializer.save()
        entry.gradebook.recalculate()

    def perform_update(self, serializer):
        entry = serializer.save()
        entry.gradebook.recalculate()
