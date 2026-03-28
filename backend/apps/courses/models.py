"""Course, Section, Lesson, LessonContent, CourseCategory, and Enrollment models."""
import uuid
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class CourseCategory(models.Model):
    """Top-level and sub-level course categories."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class name")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Course Category"
        verbose_name_plural = "Course Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Course(models.Model):
    """Main course model."""

    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"
        ALL_LEVELS = "all_levels", "All Levels"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        REVIEW = "review", "In Review"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses_created"
    )
    category = models.ForeignKey(
        CourseCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="courses"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    requirements = models.JSONField(default=list, blank=True, help_text="List of prerequisite strings")
    what_you_will_learn = models.JSONField(default=list, blank=True, help_text="List of learning outcomes")
    target_audience = models.JSONField(default=list, blank=True)
    language = models.CharField(max_length=10, default="en")
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.ALL_LEVELS)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    thumbnail = models.ImageField(upload_to="courses/thumbnails/%Y/%m/", blank=True, null=True)
    promo_video_url = models.URLField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_free = models.BooleanField(default=False)
    total_duration = models.DurationField(null=True, blank=True, help_text="Auto-calculated total video duration")
    total_lessons = models.PositiveIntegerField(default=0)
    total_enrollments = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.price == 0:
            self.is_free = True
        super().save(*args, **kwargs)


class Section(models.Model):
    """Course section (module/chapter)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        unique_together = ("course", "order")
        verbose_name = "Section"

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """Individual lesson within a section."""

    class ContentType(models.TextChoices):
        VIDEO = "video", "Video"
        ARTICLE = "article", "Article"
        QUIZ = "quiz", "Quiz"
        ASSIGNMENT = "assignment", "Assignment"
        LIVE = "live", "Live Session"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content_type = models.CharField(max_length=20, choices=ContentType.choices, default=ContentType.VIDEO)
    order = models.PositiveIntegerField(default=0)
    duration = models.DurationField(null=True, blank=True, help_text="Duration for video/live lessons")
    is_preview = models.BooleanField(default=False, help_text="Free preview lesson")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Lesson"

    def __str__(self):
        return self.title

    @property
    def course(self):
        return self.section.course


class LessonContent(models.Model):
    """Actual content for a lesson (video URL, article text, attachments)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="content")
    video_url = models.URLField(blank=True, help_text="Video URL (YouTube, Vimeo, S3)")
    video_file = models.FileField(upload_to="lessons/videos/%Y/%m/", blank=True, null=True)
    article_body = models.TextField(blank=True, help_text="Markdown or HTML content")
    attachment = models.FileField(upload_to="lessons/attachments/%Y/%m/", blank=True, null=True)
    attachment_name = models.CharField(max_length=255, blank=True)
    external_resources = models.JSONField(default=list, blank=True, help_text="List of {title, url} objects")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Lesson Content"
        verbose_name_plural = "Lesson Contents"

    def __str__(self):
        return f"Content for: {self.lesson.title}"


class Enrollment(models.Model):
    """Student enrollment in a course."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-enrolled_at"]
        verbose_name = "Enrollment"

    def __str__(self):
        return f"{self.student.email} -> {self.course.title}"
