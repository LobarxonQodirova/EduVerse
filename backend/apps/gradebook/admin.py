"""Admin configuration for gradebook app."""
from django.contrib import admin
from .models import GradeBook, GradeEntry, GradeScale


class GradeEntryInline(admin.TabularInline):
    model = GradeEntry
    extra = 0
    fields = ("title", "entry_type", "score", "max_score", "weight", "graded_at")
    readonly_fields = ("created_at",)


@admin.register(GradeScale)
class GradeScaleAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default", "created_at")
    list_filter = ("is_default",)
    search_fields = ("name",)


@admin.register(GradeBook)
class GradeBookAdmin(admin.ModelAdmin):
    list_display = (
        "student", "course", "overall_percentage", "letter_grade",
        "graded_assignments", "graded_quizzes", "updated_at",
    )
    list_filter = ("letter_grade",)
    search_fields = ("student__email", "course__title")
    raw_id_fields = ("student", "course", "grade_scale")
    inlines = [GradeEntryInline]


@admin.register(GradeEntry)
class GradeEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "gradebook", "entry_type", "score", "max_score", "weight", "graded_at")
    list_filter = ("entry_type",)
    search_fields = ("title",)
    raw_id_fields = ("gradebook", "assignment", "quiz")
