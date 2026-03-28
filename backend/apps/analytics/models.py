"""Analytics models for tracking platform-wide and per-course metrics."""
import uuid
from django.conf import settings
from django.db import models


class CourseAnalytics(models.Model):
    """Daily aggregated analytics snapshot for a course."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="analytics"
    )
    date = models.DateField()
    views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    new_enrollments = models.PositiveIntegerField(default=0)
    completions = models.PositiveIntegerField(default=0)
    avg_progress = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Average progress percentage across enrolled students"
    )
    total_watch_time_minutes = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ("course", "date")
        ordering = ["-date"]
        verbose_name = "Course Analytics"
        verbose_name_plural = "Course Analytics"

    def __str__(self):
        return f"{self.course.title} - {self.date}"


class PlatformAnalytics(models.Model):
    """Daily platform-wide analytics snapshot."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    total_users = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    total_courses = models.PositiveIntegerField(default=0)
    new_courses = models.PositiveIntegerField(default=0)
    total_enrollments = models.PositiveIntegerField(default=0)
    new_enrollments = models.PositiveIntegerField(default=0)
    total_completions = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Platform Analytics"
        verbose_name_plural = "Platform Analytics"

    def __str__(self):
        return f"Platform Analytics - {self.date}"
