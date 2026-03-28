"""Notification model for in-app and email notifications."""
import uuid
from django.conf import settings
from django.db import models


class Notification(models.Model):
    """In-app notification for a user."""

    class NotificationType(models.TextChoices):
        ENROLLMENT = "enrollment", "Enrollment"
        ASSIGNMENT = "assignment", "Assignment"
        GRADE = "grade", "Grade"
        QUIZ = "quiz", "Quiz"
        DISCUSSION = "discussion", "Discussion"
        DEADLINE = "deadline", "Deadline Reminder"
        CERTIFICATE = "certificate", "Certificate"
        ANNOUNCEMENT = "announcement", "Announcement"
        SYSTEM = "system", "System"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(
        max_length=20, choices=NotificationType.choices, default=NotificationType.SYSTEM
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(
        max_length=500, blank=True,
        help_text="Frontend route or URL to navigate to"
    )
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    related_course = models.ForeignKey(
        "courses.Course", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="notifications",
    )
    metadata = models.JSONField(
        default=dict, blank=True,
        help_text="Additional data (e.g., assignment_id, quiz_id)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        indexes = [
            models.Index(fields=["recipient", "-created_at"]),
            models.Index(fields=["recipient", "is_read"]),
        ]

    def __str__(self):
        status = "read" if self.is_read else "unread"
        return f"[{status}] {self.title} -> {self.recipient.email}"
