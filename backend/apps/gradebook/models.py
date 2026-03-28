"""GradeBook, GradeEntry, and GradeScale models."""
import uuid
from django.conf import settings
from django.db import models


class GradeScale(models.Model):
    """Configurable grading scale for a course (e.g., A/B/C or Pass/Fail)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="e.g., Standard Letter Grade")
    description = models.TextField(blank=True)
    scale_data = models.JSONField(
        default=list,
        help_text=(
            'List of {letter, min_percent, max_percent} objects, e.g. '
            '[{"letter": "A", "min_percent": 93, "max_percent": 100}]'
        ),
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Grade Scale"

    def __str__(self):
        return self.name

    def get_letter_grade(self, percentage):
        """Return the letter grade for a given percentage based on scale_data."""
        for entry in sorted(self.scale_data, key=lambda e: e.get("min_percent", 0), reverse=True):
            if percentage >= entry.get("min_percent", 0):
                return entry.get("letter", "")
        return "F"


class GradeBook(models.Model):
    """Aggregated grade book for a student in a specific course."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="gradebooks"
    )
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="gradebooks"
    )
    grade_scale = models.ForeignKey(
        GradeScale, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="gradebooks",
    )
    overall_score = models.DecimalField(
        max_digits=6, decimal_places=2, default=0,
        help_text="Weighted overall score"
    )
    overall_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    letter_grade = models.CharField(max_length=5, blank=True)
    total_assignments = models.PositiveIntegerField(default=0)
    graded_assignments = models.PositiveIntegerField(default=0)
    total_quizzes = models.PositiveIntegerField(default=0)
    graded_quizzes = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-updated_at"]
        verbose_name = "Grade Book"

    def __str__(self):
        return f"{self.student.email} - {self.course.title}: {self.letter_grade}"

    def recalculate(self):
        """Recalculate overall score from all grade entries."""
        entries = self.entries.all()
        if not entries.exists():
            return

        total_weighted = sum(e.score * (e.weight / 100) for e in entries if e.score is not None)
        total_weight = sum(e.weight for e in entries if e.score is not None)
        max_weighted = sum(e.max_score * (e.weight / 100) for e in entries if e.score is not None)

        self.overall_score = round(total_weighted, 2)
        self.overall_percentage = round(
            (total_weighted / max_weighted) * 100, 2
        ) if max_weighted > 0 else 0
        self.graded_assignments = entries.filter(
            entry_type="assignment", score__isnull=False
        ).count()
        self.graded_quizzes = entries.filter(
            entry_type="quiz", score__isnull=False
        ).count()

        if self.grade_scale:
            self.letter_grade = self.grade_scale.get_letter_grade(float(self.overall_percentage))
        self.save()


class GradeEntry(models.Model):
    """Individual grade entry in a gradebook (for an assignment or quiz)."""

    class EntryType(models.TextChoices):
        ASSIGNMENT = "assignment", "Assignment"
        QUIZ = "quiz", "Quiz"
        PARTICIPATION = "participation", "Participation"
        EXTRA_CREDIT = "extra_credit", "Extra Credit"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gradebook = models.ForeignKey(
        GradeBook, on_delete=models.CASCADE, related_name="entries"
    )
    entry_type = models.CharField(
        max_length=20, choices=EntryType.choices, default=EntryType.ASSIGNMENT
    )
    title = models.CharField(max_length=255)
    score = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True
    )
    max_score = models.PositiveIntegerField(default=100)
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, default=100,
        help_text="Weight percentage for this entry in the overall grade"
    )
    assignment = models.ForeignKey(
        "assignments.Assignment", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="grade_entries",
    )
    quiz = models.ForeignKey(
        "quizzes.Quiz", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="grade_entries",
    )
    notes = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Grade Entry"
        verbose_name_plural = "Grade Entries"

    def __str__(self):
        score_display = f"{self.score}/{self.max_score}" if self.score is not None else "ungraded"
        return f"{self.title}: {score_display}"

    @property
    def percentage(self):
        if self.score is not None and self.max_score > 0:
            return round((float(self.score) / self.max_score) * 100, 2)
        return None
