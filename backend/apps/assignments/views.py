"""Assignment views: CRUD for assignments, submissions, grades, and feedback."""
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsInstructor, IsInstructorOrAdmin
from .models import Assignment, Submission, Rubric, Grade, Feedback
from .serializers import (
    AssignmentListSerializer,
    AssignmentDetailSerializer,
    AssignmentCreateSerializer,
    SubmissionSerializer,
    RubricSerializer,
    GradeSerializer,
    FeedbackSerializer,
)


class AssignmentViewSet(viewsets.ModelViewSet):
    """CRUD for assignments. Instructors create; students view published ones."""

    permission_classes = [IsAuthenticated]
    filterset_fields = ["course", "assignment_type", "is_published"]
    search_fields = ["title", "description"]
    ordering_fields = ["due_date", "created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = Assignment.objects.select_related("course", "lesson")
        if user.role == "student":
            qs = qs.filter(
                is_published=True,
                course__enrollments__student=user,
                course__enrollments__is_active=True,
            )
        elif user.role == "instructor":
            qs = qs.filter(course__instructor=user)
        return qs.distinct()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return AssignmentCreateSerializer
        if self.action == "retrieve":
            return AssignmentDetailSerializer
        return AssignmentListSerializer

    @action(detail=True, methods=["get"])
    def submissions(self, request, pk=None):
        """List all submissions for an assignment (instructor view)."""
        assignment = self.get_object()
        subs = assignment.submissions.select_related("student").all()
        serializer = SubmissionSerializer(subs, many=True, context={"request": request})
        return Response(serializer.data)


class SubmissionViewSet(viewsets.ModelViewSet):
    """Manage student submissions."""

    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "instructor":
            return Submission.objects.filter(
                assignment__course__instructor=user
            ).select_related("student", "assignment", "grade")
        return Submission.objects.filter(student=user).select_related(
            "assignment", "grade"
        )


class RubricViewSet(viewsets.ModelViewSet):
    """Manage rubric criteria for assignments."""

    serializer_class = RubricSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrAdmin]

    def get_queryset(self):
        return Rubric.objects.filter(
            assignment_id=self.kwargs.get("assignment_pk")
        )

    def perform_create(self, serializer):
        serializer.save(assignment_id=self.kwargs["assignment_pk"])


class GradeCreateView(generics.CreateAPIView):
    """Instructor grades a submission."""

    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated, IsInstructor]
    queryset = Grade.objects.all()

    def perform_create(self, serializer):
        submission = Submission.objects.get(pk=self.kwargs["submission_pk"])
        submission.status = Submission.Status.GRADED
        submission.save(update_fields=["status"])
        serializer.save(
            grader=self.request.user,
            submission=submission,
            max_score=submission.assignment.max_score,
        )


class FeedbackViewSet(viewsets.ModelViewSet):
    """Manage feedback on submissions."""

    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        qs = Feedback.objects.filter(
            submission_id=self.kwargs.get("submission_pk")
        ).select_related("author")
        if self.request.user.role == "student":
            qs = qs.filter(is_private=False)
        return qs

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            submission_id=self.kwargs["submission_pk"],
        )
