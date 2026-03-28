"""Course business logic and service layer."""
import logging
from datetime import timedelta
from django.db import transaction
from django.utils import timezone

from .models import Course, Section, Lesson, Enrollment

logger = logging.getLogger(__name__)


class CourseService:
    """Service class encapsulating course-related business logic."""

    @staticmethod
    def publish_course(course: Course) -> Course:
        """Validate and publish a course."""
        errors = []
        if not course.title:
            errors.append("Course must have a title.")
        if not course.description:
            errors.append("Course must have a description.")
        sections = course.sections.filter(is_published=True)
        if sections.count() == 0:
            errors.append("Course must have at least one published section.")
        total_lessons = 0
        for section in sections:
            lesson_count = section.lessons.filter(is_published=True).count()
            if lesson_count == 0:
                errors.append(f"Section '{section.title}' must have at least one published lesson.")
            total_lessons += lesson_count
        if errors:
            raise ValueError(errors)
        course.status = Course.Status.PUBLISHED
        course.published_at = timezone.now()
        course.total_lessons = total_lessons
        course.save()
        logger.info("Course published: %s (id=%s)", course.title, course.id)
        return course

    @staticmethod
    def recalculate_course_stats(course: Course) -> Course:
        """Recalculate total lessons, duration, enrollments for a course."""
        lessons = Lesson.objects.filter(
            section__course=course, is_published=True
        )
        course.total_lessons = lessons.count()
        durations = lessons.exclude(duration__isnull=True).values_list("duration", flat=True)
        total = timedelta()
        for d in durations:
            total += d
        course.total_duration = total if total.total_seconds() > 0 else None
        course.total_enrollments = Enrollment.objects.filter(
            course=course, is_active=True
        ).count()
        course.save(update_fields=["total_lessons", "total_duration", "total_enrollments"])
        return course

    @staticmethod
    @transaction.atomic
    def enroll_student(user, course: Course) -> Enrollment:
        """Enroll a student in a course. Handles free courses directly."""
        if user.role != "student":
            raise ValueError("Only students can enroll in courses.")
        if Enrollment.objects.filter(student=user, course=course).exists():
            raise ValueError("Already enrolled in this course.")
        if not course.is_free and course.price > 0:
            raise ValueError("Payment required for this course.")
        enrollment = Enrollment.objects.create(student=user, course=course)
        course.total_enrollments = Enrollment.objects.filter(
            course=course, is_active=True
        ).count()
        course.save(update_fields=["total_enrollments"])
        # Update student profile
        if hasattr(user, "student_profile"):
            user.student_profile.total_courses_enrolled += 1
            user.student_profile.save(update_fields=["total_courses_enrolled"])
        # Update instructor profile
        if hasattr(course.instructor, "instructor_profile"):
            profile = course.instructor.instructor_profile
            profile.total_students = Enrollment.objects.filter(
                course__instructor=course.instructor, is_active=True
            ).count()
            profile.save(update_fields=["total_students"])
        logger.info("Student %s enrolled in course %s", user.email, course.title)
        return enrollment

    @staticmethod
    def duplicate_course(course: Course, new_instructor=None) -> Course:
        """Create a draft copy of an existing course with all sections and lessons."""
        instructor = new_instructor or course.instructor
        with transaction.atomic():
            new_course = Course.objects.create(
                instructor=instructor,
                category=course.category,
                title=f"{course.title} (Copy)",
                description=course.description,
                requirements=course.requirements,
                what_you_will_learn=course.what_you_will_learn,
                target_audience=course.target_audience,
                language=course.language,
                level=course.level,
                price=course.price,
                status=Course.Status.DRAFT,
            )
            for section in course.sections.all():
                new_section = Section.objects.create(
                    course=new_course,
                    title=section.title,
                    description=section.description,
                    order=section.order,
                )
                for lesson in section.lessons.all():
                    Lesson.objects.create(
                        section=new_section,
                        title=lesson.title,
                        description=lesson.description,
                        content_type=lesson.content_type,
                        order=lesson.order,
                        duration=lesson.duration,
                        is_preview=lesson.is_preview,
                    )
        return new_course
