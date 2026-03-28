"""Account URL patterns."""
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("instructor-profile/", views.InstructorProfileView.as_view(), name="instructor-profile"),
    path("student-profile/", views.StudentProfileView.as_view(), name="student-profile"),
    path("instructors/<uuid:user_id>/", views.InstructorPublicView.as_view(), name="instructor-public"),
    path("users/", views.UserListView.as_view(), name="user-list"),
]
