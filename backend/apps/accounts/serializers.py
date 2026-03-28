"""Account serializers for registration, login, and profile management."""
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, InstructorProfile, StudentProfile


class UserSerializer(serializers.ModelSerializer):
    """Public user information."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id", "email", "first_name", "last_name", "full_name",
            "role", "avatar", "bio", "phone", "is_email_verified",
            "created_at",
        ]
        read_only_fields = ["id", "email", "is_email_verified", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    """User registration serializer."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email", "first_name", "last_name", "password",
            "password_confirm", "role",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        if attrs.get("role") == User.Role.ADMIN:
            raise serializers.ValidationError({"role": "Cannot register as admin."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Create role-specific profile
        if user.role == User.Role.INSTRUCTOR:
            InstructorProfile.objects.create(user=user)
        else:
            StudentProfile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """Email + password login returning JWT tokens."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(email=attrs["email"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("Account is deactivated.")
        refresh = RefreshToken.for_user(user)
        return {
            "user": UserSerializer(user).data,
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
        }


class ChangePasswordSerializer(serializers.Serializer):
    """Change password for authenticated users."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class InstructorProfileSerializer(serializers.ModelSerializer):
    """Instructor profile details."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = InstructorProfile
        fields = [
            "id", "user", "headline", "expertise", "website",
            "linkedin_url", "github_url", "youtube_url",
            "total_students", "total_courses", "total_revenue",
            "average_rating", "is_verified", "created_at",
        ]
        read_only_fields = [
            "id", "total_students", "total_courses",
            "total_revenue", "average_rating", "is_verified", "created_at",
        ]


class StudentProfileSerializer(serializers.ModelSerializer):
    """Student profile details."""

    user = UserSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            "id", "user", "level", "interests",
            "total_courses_enrolled", "total_courses_completed",
            "total_certificates", "total_learning_hours", "created_at",
        ]
        read_only_fields = [
            "id", "total_courses_enrolled", "total_courses_completed",
            "total_certificates", "total_learning_hours", "created_at",
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Update user basic info."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "bio", "phone", "date_of_birth", "avatar"]
