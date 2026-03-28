"""Course serializers for CRUD and nested representations."""
from rest_framework import serializers
from apps.accounts.serializers import UserSerializer
from .models import Course, Section, Lesson, LessonContent, CourseCategory, Enrollment


class CourseCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseCategory
        fields = ["id", "name", "slug", "description", "icon", "parent", "is_active", "order", "children", "course_count"]

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CourseCategorySerializer(children, many=True).data

    def get_course_count(self, obj):
        return obj.courses.filter(status="published").count()


class LessonContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonContent
        fields = [
            "id", "video_url", "video_file", "article_body",
            "attachment", "attachment_name", "external_resources",
        ]


class LessonSerializer(serializers.ModelSerializer):
    content = LessonContentSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id", "section", "title", "description", "content_type",
            "order", "duration", "is_preview", "is_published", "content",
        ]
        read_only_fields = ["id"]


class LessonListSerializer(serializers.ModelSerializer):
    """Lightweight lesson serializer without full content (for section listings)."""

    class Meta:
        model = Lesson
        fields = [
            "id", "title", "content_type", "order", "duration",
            "is_preview", "is_published",
        ]


class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = Section
        fields = [
            "id", "course", "title", "description", "order",
            "is_published", "lessons", "lesson_count",
        ]
        read_only_fields = ["id"]

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class CourseListSerializer(serializers.ModelSerializer):
    """Serializer used in course list views."""

    instructor_name = serializers.CharField(source="instructor.full_name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, default=None)

    class Meta:
        model = Course
        fields = [
            "id", "title", "slug", "subtitle", "thumbnail",
            "price", "is_free", "level", "status",
            "instructor", "instructor_name",
            "category", "category_name",
            "average_rating", "total_reviews",
            "total_enrollments", "total_lessons",
            "total_duration", "published_at", "created_at",
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    """Full course detail with sections and instructor info."""

    instructor_detail = UserSerializer(source="instructor", read_only=True)
    category_detail = CourseCategorySerializer(source="category", read_only=True)
    sections = SectionSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id", "title", "slug", "subtitle", "description",
            "requirements", "what_you_will_learn", "target_audience",
            "language", "level", "status", "thumbnail", "promo_video_url",
            "price", "is_free", "total_duration", "total_lessons",
            "total_enrollments", "average_rating", "total_reviews",
            "is_featured", "published_at", "created_at", "updated_at",
            "instructor", "instructor_detail",
            "category", "category_detail",
            "sections", "is_enrolled",
        ]
        read_only_fields = [
            "id", "slug", "total_duration", "total_lessons",
            "total_enrollments", "average_rating", "total_reviews",
        ]

    def get_is_enrolled(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                student=request.user, course=obj, is_active=True
            ).exists()
        return False


class CourseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating / updating courses."""

    class Meta:
        model = Course
        fields = [
            "title", "subtitle", "description", "requirements",
            "what_you_will_learn", "target_audience", "language",
            "level", "category", "thumbnail", "promo_video_url",
            "price", "status",
        ]

    def create(self, validated_data):
        validated_data["instructor"] = self.context["request"].user
        return super().create(validated_data)


class EnrollmentSerializer(serializers.ModelSerializer):
    course_detail = CourseListSerializer(source="course", read_only=True)
    student_name = serializers.CharField(source="student.full_name", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "id", "student", "course", "enrolled_at", "is_active",
            "completed_at", "last_accessed", "course_detail", "student_name",
        ]
        read_only_fields = ["id", "student", "enrolled_at", "completed_at", "last_accessed"]

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)
