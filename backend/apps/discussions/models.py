"""DiscussionForum, Thread, and Reply models."""
import uuid
from django.conf import settings
from django.db import models


class DiscussionForum(models.Model):
    """A discussion forum associated with a course."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.OneToOneField(
        "courses.Course", on_delete=models.CASCADE, related_name="forum"
    )
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(
        blank=True, help_text="Guidelines for the discussion forum"
    )
    is_locked = models.BooleanField(
        default=False, help_text="Prevent new threads when locked"
    )
    allow_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Discussion Forum"

    def __str__(self):
        return self.title or f"Forum: {self.course.title}"

    @property
    def thread_count(self):
        return self.threads.count()

    @property
    def reply_count(self):
        return Reply.objects.filter(thread__forum=self).count()


class Thread(models.Model):
    """A discussion thread within a forum."""

    class ThreadType(models.TextChoices):
        QUESTION = "question", "Question"
        DISCUSSION = "discussion", "Discussion"
        ANNOUNCEMENT = "announcement", "Announcement"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    forum = models.ForeignKey(
        DiscussionForum, on_delete=models.CASCADE, related_name="threads"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="threads"
    )
    title = models.CharField(max_length=300)
    body = models.TextField()
    thread_type = models.CharField(
        max_length=20, choices=ThreadType.choices, default=ThreadType.DISCUSSION
    )
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_resolved = models.BooleanField(
        default=False, help_text="Mark question threads as resolved"
    )
    view_count = models.PositiveIntegerField(default=0)
    upvotes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_pinned", "-created_at"]
        verbose_name = "Thread"

    def __str__(self):
        return self.title

    @property
    def reply_count(self):
        return self.replies.count()


class Reply(models.Model):
    """A reply to a discussion thread."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    thread = models.ForeignKey(
        Thread, on_delete=models.CASCADE, related_name="replies"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="replies"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True,
        related_name="children", help_text="Parent reply for nested replies"
    )
    body = models.TextField()
    is_accepted_answer = models.BooleanField(
        default=False, help_text="Marked as the accepted answer for a question thread"
    )
    upvotes = models.PositiveIntegerField(default=0)
    is_edited = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_accepted_answer", "created_at"]
        verbose_name = "Reply"
        verbose_name_plural = "Replies"

    def __str__(self):
        return f"Reply by {self.author.email} on {self.thread.title[:40]}"

    def save(self, *args, **kwargs):
        if self.pk:
            self.is_edited = True
        super().save(*args, **kwargs)
