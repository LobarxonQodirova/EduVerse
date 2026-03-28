"""Custom permissions for role-based access control."""
from rest_framework.permissions import BasePermission


class IsInstructor(BasePermission):
    """Allow access only to instructors."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "instructor"
        )


class IsStudent(BasePermission):
    """Allow access only to students."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "student"
        )


class IsAdminUser(BasePermission):
    """Allow access only to admin users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsInstructorOrAdmin(BasePermission):
    """Allow access to instructors and admins."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in ("instructor", "admin")
        )


class IsOwnerOrReadOnly(BasePermission):
    """Object-level permission: only owners can modify."""

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        if hasattr(obj, "user"):
            return obj.user == request.user
        if hasattr(obj, "instructor"):
            return obj.instructor == request.user
        return False


class IsCourseInstructor(BasePermission):
    """Only the course instructor can modify course content."""

    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        if hasattr(obj, "course"):
            return obj.course.instructor == request.user
        if hasattr(obj, "instructor"):
            return obj.instructor == request.user
        return False


class IsEnrolledOrInstructor(BasePermission):
    """Access for enrolled students or the course instructor."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        course = getattr(obj, "course", obj)
        if course.instructor == user:
            return True
        return course.enrollments.filter(student=user, is_active=True).exists()
