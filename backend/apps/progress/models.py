"""StudentProgress, CompletionRecord, and Certificate models."""
import uuid
from django.conf import settings
from django.db import models


class StudentProgress(models.Model):
    """Tracks a student's overall progress within a course."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="progress_records"
    )
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="student_progress"
    )
    completed_lessons = models.PositiveIntegerField(default=0)
    total_lessons = models.PositiveIntegerField(default=0)
    progress_percent = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Overall completion percentage"
    )
    total_time_spent = models.DurationField(
        null=True, blank=True, help_text="Total time spent on this course"
    )
    last_lesson = models.ForeignKey(
        "courses.Lesson", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="+", help_text="Last lesson accessed"
    )
    last_accessed = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-last_accessed"]
        verbose_name = "Student Progress"
        verbose_name_plural = "Student Progress"

    def __str__(self):
        return f"{self.student.email} - {self.course.title}: {self.progress_percent}%"

    @property
    def is_completed(self):
        return self.progress_percent >= 100


class CompletionRecord(models.Model):
    """Records completion of individual lessons within a course."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="completions"
    )
    lesson = models.ForeignKey(
        "courses.Lesson", on_delete=models.CASCADE, related_name="completions"
    )
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="lesson_completions"
    )
    time_spent = models.DurationField(
        null=True, blank=True, help_text="Time spent on this lesson"
    )
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "lesson")
        ordering = ["-completed_at"]
        verbose_name = "Completion Record"

    def __str__(self):
        return f"{self.student.email} completed {self.lesson.title}"


class Certificate(models.Model):
    """Certificate issued to a student upon course completion."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certificates"
    )
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="certificates"
    )
    certificate_number = models.CharField(
        max_length=50, unique=True, help_text="Unique certificate identifier"
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(
        upload_to="certificates/%Y/%m/", blank=True, null=True
    )
    verification_url = models.URLField(blank=True)
    final_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Final grade percentage at time of completion"
    )

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-issued_at"]
        verbose_name = "Certificate"

    def __str__(self):
        return f"Certificate {self.certificate_number} - {self.student.email}"
