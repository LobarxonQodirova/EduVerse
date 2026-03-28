"""Course views: CRUD for courses, sections, lessons, enrollments, and categories."""
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.accounts.permissions import IsInstructor, IsInstructorOrAdmin, IsCourseInstructor
from .models import Course, Section, Lesson, LessonContent, CourseCategory, Enrollment
from .serializers import (
    CourseListSerializer,
    CourseDetailSerializer,
    CourseCreateSerializer,
    SectionSerializer,
    LessonSerializer,
    LessonContentSerializer,
    CourseCategorySerializer,
    EnrollmentSerializer,
)
from .services import CourseService


class CourseCategoryViewSet(viewsets.ModelViewSet):
    """CRUD for course categories."""

    queryset = CourseCategory.objects.filter(is_active=True, parent__isnull=True)
    serializer_class = CourseCategorySerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsInstructorOrAdmin()]


class CourseViewSet(viewsets.ModelViewSet):
    """Full CRUD for courses with filtering, search, and ordering."""

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "level", "status", "is_free", "language"]
    search_fields = ["title", "subtitle", "description"]
    ordering_fields = ["created_at", "price", "average_rating", "total_enrollments"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = Course.objects.select_related("instructor", "category")
        if self.action == "list":
            if not self.request.user.is_authenticated or self.request.user.role == "student":
                qs = qs.filter(status="published")
            elif self.request.user.role == "instructor":
                qs = qs.filter(instructor=self.request.user)
        return qs

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CourseCreateSerializer
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseListSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action == "create":
            return [IsAuthenticated(), IsInstructor()]
        return [IsAuthenticated(), IsCourseInstructor()]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsInstructor])
    def publish(self, request, pk=None):
        """Validate and publish a course."""
        course = self.get_object()
        try:
            CourseService.publish_course(course)
            return Response({"message": "Course published successfully."})
        except ValueError as exc:
            return Response({"errors": exc.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsInstructor])
    def duplicate(self, request, pk=None):
        """Duplicate a course as a new draft."""
        course = self.get_object()
        new_course = CourseService.duplicate_course(course, new_instructor=request.user)
        return Response(
            CourseDetailSerializer(new_course, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"])
    def students(self, request, pk=None):
        """List enrolled students for a course."""
        course = self.get_object()
        enrollments = Enrollment.objects.filter(course=course, is_active=True).select_related("student")
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)


class SectionViewSet(viewsets.ModelViewSet):
    """Manage sections within a course."""

    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Section.objects.filter(
            course_id=self.kwargs["course_pk"]
        ).prefetch_related("lessons")

    def perform_create(self, serializer):
        course = Course.objects.get(pk=self.kwargs["course_pk"])
        serializer.save(course=course)


class LessonViewSet(viewsets.ModelViewSet):
    """Manage lessons within a section."""

    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Lesson.objects.filter(
            section_id=self.kwargs["section_pk"],
            section__course_id=self.kwargs["course_pk"],
        ).select_related("content")

    def perform_create(self, serializer):
        section = Section.objects.get(
            pk=self.kwargs["section_pk"],
            course_id=self.kwargs["course_pk"],
        )
        serializer.save(section=section)


class LessonContentView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the content of a specific lesson."""

    serializer_class = LessonContentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        content, _ = LessonContent.objects.get_or_create(
            lesson_id=self.kwargs["lesson_pk"]
        )
        return content


class EnrollmentViewSet(viewsets.ModelViewSet):
    """Manage student enrollments."""

    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        user = self.request.user
        if user.role == "instructor":
            return Enrollment.objects.filter(
                course__instructor=user
            ).select_related("student", "course")
        return Enrollment.objects.filter(student=user).select_related("course")

    def create(self, request, *args, **kwargs):
        course_id = request.data.get("course")
        try:
            course = Course.objects.get(pk=course_id)
            enrollment = CourseService.enroll_student(request.user, course)
            return Response(
                EnrollmentSerializer(enrollment).data,
                status=status.HTTP_201_CREATED,
            )
        except (Course.DoesNotExist, ValueError) as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
