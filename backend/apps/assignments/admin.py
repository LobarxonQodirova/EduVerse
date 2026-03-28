"""Admin configuration for assignments app."""
from django.contrib import admin
from .models import Assignment, Submission, Rubric, Grade, Feedback


class RubricInline(admin.TabularInline):
    model = Rubric
    extra = 1
    fields = ("criterion", "description", "max_points", "order")
    ordering = ("order",)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "title", "course", "assignment_type", "max_score",
        "due_date", "is_published", "created_at",
    )
    list_filter = ("assignment_type", "is_published", "allow_late_submission")
    search_fields = ("title", "description", "course__title")
    raw_id_fields = ("course", "lesson")
    inlines = [RubricInline]
    date_hierarchy = "created_at"


class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 0
    fields = ("author", "comment", "is_private", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "student", "assignment", "status", "attempt_number",
        "submitted_at", "is_late",
    )
    list_filter = ("status",)
    search_fields = ("student__email", "assignment__title")
    raw_id_fields = ("student", "assignment")
    inlines = [FeedbackInline]
    date_hierarchy = "submitted_at"


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("submission", "grader", "score", "max_score", "percentage", "letter_grade", "graded_at")
    search_fields = ("submission__student__email",)
    raw_id_fields = ("submission", "grader")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("author", "submission", "is_private", "created_at")
    list_filter = ("is_private",)
    search_fields = ("comment",)
    raw_id_fields = ("author", "submission")
