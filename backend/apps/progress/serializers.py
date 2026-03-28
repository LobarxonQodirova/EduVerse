"""Serializers for progress tracking, completions, and certificates."""
from rest_framework import serializers
from .models import StudentProgress, CompletionRecord, Certificate


class CompletionRecordSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = CompletionRecord
        fields = [
            "id", "student", "lesson", "lesson_title", "course",
            "time_spent", "completed_at",
        ]
        read_only_fields = ["id", "student", "completed_at"]

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)


class StudentProgressSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    last_lesson_title = serializers.CharField(
        source="last_lesson.title", read_only=True, default=None
    )

    class Meta:
        model = StudentProgress
        fields = [
            "id", "student", "course", "course_title",
            "completed_lessons", "total_lessons", "progress_percent",
            "total_time_spent", "last_lesson", "last_lesson_title",
            "last_accessed", "started_at", "completed_at", "is_completed",
        ]
        read_only_fields = [
            "id", "student", "completed_lessons", "total_lessons",
            "progress_percent", "total_time_spent", "last_accessed",
            "started_at", "completed_at",
        ]


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Certificate
        fields = [
            "id", "student", "student_name", "course", "course_title",
            "certificate_number", "issued_at", "pdf_file",
            "verification_url", "final_grade",
        ]
        read_only_fields = [
            "id", "student", "certificate_number", "issued_at",
            "pdf_file", "verification_url",
        ]
