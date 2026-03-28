"""Assignment, Submission, Rubric, Grade, and Feedback models."""
import uuid
from django.conf import settings
from django.db import models


class Assignment(models.Model):
    """An assignment attached to a course lesson or module."""

    class AssignmentType(models.TextChoices):
        FILE_UPLOAD = "file_upload", "File Upload"
        TEXT_ENTRY = "text_entry", "Text Entry"
        URL_SUBMISSION = "url_submission", "URL Submission"
        CODE = "code", "Code Submission"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="assignments"
    )
    lesson = models.ForeignKey(
        "courses.Lesson", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assignments",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    assignment_type = models.CharField(
        max_length=20, choices=AssignmentType.choices, default=AssignmentType.FILE_UPLOAD
    )
    max_score = models.PositiveIntegerField(default=100)
    due_date = models.DateTimeField(null=True, blank=True)
    allow_late_submission = models.BooleanField(default=False)
    late_penalty_percent = models.PositiveIntegerField(
        default=10, help_text="Percentage deducted per day late"
    )
    max_attempts = models.PositiveIntegerField(default=1)
    attachment = models.FileField(
        upload_to="assignments/instructions/%Y/%m/", blank=True, null=True
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["due_date", "title"]
        verbose_name = "Assignment"

    def __str__(self):
        return f"{self.title} ({self.course.title})"

    @property
    def is_past_due(self):
        from django.utils import timezone
        if self.due_date:
            return timezone.now() > self.due_date
        return False


class Rubric(models.Model):
    """Grading rubric for an assignment, consisting of criteria rows."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="rubrics"
    )
    criterion = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    max_points = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "Rubric Criterion"
        verbose_name_plural = "Rubric Criteria"

    def __str__(self):
        return f"{self.criterion} ({self.max_points} pts)"


class Submission(models.Model):
    """A student's submission for an assignment."""

    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        GRADED = "graded", "Graded"
        RETURNED = "returned", "Returned for Revision"
        LATE = "late", "Late Submission"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submissions"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    text_content = models.TextField(blank=True)
    file_upload = models.FileField(
        upload_to="assignments/submissions/%Y/%m/", blank=True, null=True
    )
    url_link = models.URLField(blank=True)
    attempt_number = models.PositiveIntegerField(default=1)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = "Submission"

    def __str__(self):
        return f"{self.student.email} - {self.assignment.title} (Attempt {self.attempt_number})"

    @property
    def is_late(self):
        if self.assignment.due_date:
            return self.submitted_at > self.assignment.due_date
        return False


class Grade(models.Model):
    """Grade assigned to a submission, optionally broken down by rubric criteria."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.OneToOneField(
        Submission, on_delete=models.CASCADE, related_name="grade"
    )
    grader = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name="grades_given",
    )
    score = models.DecimalField(max_digits=6, decimal_places=2)
    max_score = models.PositiveIntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    letter_grade = models.CharField(max_length=5, blank=True)
    rubric_scores = models.JSONField(
        default=dict, blank=True,
        help_text='Mapping of rubric criterion ID to score: {"<uuid>": 8}'
    )
    graded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Grade"

    def __str__(self):
        return f"{self.submission.student.email}: {self.score}/{self.max_score}"

    def save(self, *args, **kwargs):
        if self.max_score and self.max_score > 0:
            self.percentage = (self.score / self.max_score) * 100
            self.letter_grade = self._calculate_letter_grade(float(self.percentage))
        super().save(*args, **kwargs)

    @staticmethod
    def _calculate_letter_grade(pct):
        if pct >= 93:
            return "A"
        elif pct >= 90:
            return "A-"
        elif pct >= 87:
            return "B+"
        elif pct >= 83:
            return "B"
        elif pct >= 80:
            return "B-"
        elif pct >= 77:
            return "C+"
        elif pct >= 73:
            return "C"
        elif pct >= 70:
            return "C-"
        elif pct >= 67:
            return "D+"
        elif pct >= 60:
            return "D"
        return "F"


class Feedback(models.Model):
    """Instructor feedback on a submission."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="feedbacks"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feedbacks_given"
    )
    comment = models.TextField()
    attachment = models.FileField(
        upload_to="assignments/feedback/%Y/%m/", blank=True, null=True
    )
    is_private = models.BooleanField(
        default=False, help_text="Private notes visible only to instructors"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    def __str__(self):
        return f"Feedback by {self.author.email} on {self.submission}"
