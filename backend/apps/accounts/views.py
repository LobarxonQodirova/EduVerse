"""Account views: registration, login, profile management."""
from rest_framework import generics, status, views
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User, InstructorProfile, StudentProfile
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    InstructorProfileSerializer,
    StudentProfileSerializer,
)
from .permissions import IsInstructor, IsStudent


class RegisterView(generics.CreateAPIView):
    """Register a new user (student or instructor)."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Registration successful.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(views.APIView):
    """Authenticate user and return JWT tokens."""

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve and update the authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(views.APIView):
    """Change password for authenticated user."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"message": "Password changed successfully."})


class InstructorProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve/update instructor profile for the current user."""

    serializer_class = InstructorProfileSerializer
    permission_classes = [IsAuthenticated, IsInstructor]

    def get_object(self):
        profile, _ = InstructorProfile.objects.get_or_create(user=self.request.user)
        return profile


class StudentProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve/update student profile for the current user."""

    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated, IsStudent]

    def get_object(self):
        profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        return profile


class InstructorPublicView(generics.RetrieveAPIView):
    """Public view of an instructor's profile."""

    serializer_class = InstructorProfileSerializer
    permission_classes = [AllowAny]
    queryset = InstructorProfile.objects.select_related("user")
    lookup_field = "user__id"
    lookup_url_kwarg = "user_id"


class UserListView(generics.ListAPIView):
    """Admin endpoint to list all users."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    filterset_fields = ["role", "is_active"]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["created_at", "email"]
