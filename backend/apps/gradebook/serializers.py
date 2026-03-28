"""Serializers for gradebook, grade entries, and grade scales."""
from rest_framework import serializers
from .models import GradeBook, GradeEntry, GradeScale


class GradeScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeScale
        fields = ["id", "name", "description", "scale_data", "is_default", "created_at"]
        read_only_fields = ["id", "created_at"]


class GradeEntrySerializer(serializers.ModelSerializer):
    percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )

    class Meta:
        model = GradeEntry
        fields = [
            "id", "gradebook", "entry_type", "title", "score",
            "max_score", "weight", "assignment", "quiz",
            "notes", "percentage", "graded_at", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class GradeBookSerializer(serializers.ModelSerializer):
    entries = GradeEntrySerializer(many=True, read_only=True)
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    grade_scale_name = serializers.CharField(source="grade_scale.name", read_only=True, default=None)

    class Meta:
        model = GradeBook
        fields = [
            "id", "student", "student_name", "course", "course_title",
            "grade_scale", "grade_scale_name",
            "overall_score", "overall_percentage", "letter_grade",
            "total_assignments", "graded_assignments",
            "total_quizzes", "graded_quizzes",
            "entries", "updated_at",
        ]
        read_only_fields = [
            "id", "overall_score", "overall_percentage", "letter_grade",
            "graded_assignments", "graded_quizzes", "updated_at",
        ]


class GradeBookSummarySerializer(serializers.ModelSerializer):
    """Lightweight gradebook without entries for list views."""

    student_name = serializers.CharField(source="student.full_name", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = GradeBook
        fields = [
            "id", "student", "student_name", "course", "course_title",
            "overall_percentage", "letter_grade",
            "graded_assignments", "graded_quizzes", "updated_at",
        ]
