"""Event, Deadline, and Schedule models for course calendars."""
import uuid
from django.conf import settings
from django.db import models


class Event(models.Model):
    """A calendar event (lecture, office hours, webinar, etc.)."""

    class EventType(models.TextChoices):
        LECTURE = "lecture", "Lecture"
        OFFICE_HOURS = "office_hours", "Office Hours"
        WEBINAR = "webinar", "Webinar"
        WORKSHOP = "workshop", "Workshop"
        EXAM = "exam", "Exam"
        OTHER = "other", "Other"

    class RecurrenceType(models.TextChoices):
        NONE = "none", "None"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Bi-Weekly"
        MONTHLY = "monthly", "Monthly"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="events",
        null=True, blank=True, help_text="Leave blank for personal events"
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_events"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_type = models.CharField(
        max_length=20, choices=EventType.choices, default=EventType.LECTURE
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(
        max_length=300, blank=True, help_text="Physical location or online meeting URL"
    )
    meeting_url = models.URLField(blank=True, help_text="Zoom/Meet/Teams link")
    is_all_day = models.BooleanField(default=False)
    recurrence = models.CharField(
        max_length=20, choices=RecurrenceType.choices, default=RecurrenceType.NONE
    )
    recurrence_end_date = models.DateField(null=True, blank=True)
    color = models.CharField(
        max_length=7, default="#3B82F6", help_text="Hex color for calendar display"
    )
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]
        verbose_name = "Event"

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"

    @property
    def duration(self):
        return self.end_time - self.start_time


class Deadline(models.Model):
    """Tracks deadlines for assignments, quizzes, and other items."""

    class DeadlineType(models.TextChoices):
        ASSIGNMENT = "assignment", "Assignment Due"
        QUIZ = "quiz", "Quiz Due"
        PROJECT = "project", "Project Due"
        ENROLLMENT = "enrollment", "Enrollment Deadline"
        CUSTOM = "custom", "Custom"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="deadlines"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline_type = models.CharField(
        max_length=20, choices=DeadlineType.choices, default=DeadlineType.ASSIGNMENT
    )
    due_date = models.DateTimeField()
    priority = models.CharField(
        max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    assignment = models.ForeignKey(
        "assignments.Assignment", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="deadlines",
    )
    quiz = models.ForeignKey(
        "quizzes.Quiz", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="deadlines",
    )
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date"]
        verbose_name = "Deadline"

    def __str__(self):
        return f"{self.title} - Due: {self.due_date.strftime('%Y-%m-%d %H:%M')}"

    @property
    def is_past_due(self):
        from django.utils import timezone
        return timezone.now() > self.due_date


class Schedule(models.Model):
    """Recurring weekly schedule for a course (e.g., lecture slots)."""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="schedules"
    )
    title = models.CharField(max_length=255, help_text="e.g., 'Weekly Lecture'")
    day_of_week = models.IntegerField(choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=300, blank=True)
    meeting_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    effective_from = models.DateField(help_text="When this schedule starts")
    effective_until = models.DateField(
        null=True, blank=True, help_text="When this schedule ends"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]
        verbose_name = "Schedule"

    def __str__(self):
        day = self.get_day_of_week_display()
        return f"{self.title}: {day} {self.start_time}-{self.end_time}"
