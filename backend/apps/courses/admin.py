"""Admin configuration for courses app."""
from django.contrib import admin
from .models import Course, Section, Lesson, LessonContent, CourseCategory, Enrollment


class SectionInline(admin.TabularInline):
    model = Section
    extra = 0
    fields = ("title", "order", "is_published")
    ordering = ("order",)


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ("title", "content_type", "order", "duration", "is_preview", "is_published")
    ordering = ("order",)


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title", "instructor", "category", "level", "status",
        "price", "is_free", "total_enrollments", "average_rating", "created_at",
    )
    list_filter = ("status", "level", "is_free", "is_featured", "category")
    search_fields = ("title", "description", "instructor__email")
    raw_id_fields = ("instructor", "category")
    readonly_fields = ("slug", "total_duration", "total_lessons", "total_enrollments", "average_rating", "total_reviews")
    inlines = [SectionInline]
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {"fields": ("instructor", "category", "title", "slug", "subtitle", "description")}),
        ("Details", {"fields": ("requirements", "what_you_will_learn", "target_audience", "language", "level")}),
        ("Media", {"fields": ("thumbnail", "promo_video_url")}),
        ("Pricing", {"fields": ("price", "is_free")}),
        ("Status", {"fields": ("status", "is_featured", "published_at")}),
        ("Stats", {"fields": ("total_duration", "total_lessons", "total_enrollments", "average_rating", "total_reviews")}),
    )


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "course__title")
    raw_id_fields = ("course",)
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "content_type", "order", "duration", "is_preview", "is_published")
    list_filter = ("content_type", "is_preview", "is_published")
    search_fields = ("title",)
    raw_id_fields = ("section",)


@admin.register(LessonContent)
class LessonContentAdmin(admin.ModelAdmin):
    list_display = ("lesson", "video_url", "created_at")
    search_fields = ("lesson__title",)
    raw_id_fields = ("lesson",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at", "is_active", "completed_at")
    list_filter = ("is_active",)
    search_fields = ("student__email", "course__title")
    raw_id_fields = ("student", "course")
    date_hierarchy = "enrolled_at"
