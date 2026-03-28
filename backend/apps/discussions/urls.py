"""Discussion URL patterns."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "discussions"

router = DefaultRouter()
router.register(r"forums", views.DiscussionForumViewSet, basename="forum")

urlpatterns = [
    path("", include(router.urls)),
    # Threads within a forum
    path(
        "forums/<uuid:forum_pk>/threads/",
        views.ThreadViewSet.as_view({"get": "list", "post": "create"}),
        name="forum-threads",
    ),
    path(
        "forums/<uuid:forum_pk>/threads/<uuid:pk>/",
        views.ThreadViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        name="forum-thread-detail",
    ),
    path(
        "forums/<uuid:forum_pk>/threads/<uuid:pk>/upvote/",
        views.ThreadViewSet.as_view({"post": "upvote"}),
        name="thread-upvote",
    ),
    path(
        "forums/<uuid:forum_pk>/threads/<uuid:pk>/resolve/",
        views.ThreadViewSet.as_view({"post": "resolve"}),
        name="thread-resolve",
    ),
    # Replies within a thread
    path(
        "threads/<uuid:thread_pk>/replies/",
        views.ReplyViewSet.as_view({"get": "list", "post": "create"}),
        name="thread-replies",
    ),
    path(
        "threads/<uuid:thread_pk>/replies/<uuid:pk>/",
        views.ReplyViewSet.as_view({"get": "retrieve", "patch": "partial_update", "delete": "destroy"}),
        name="thread-reply-detail",
    ),
    path(
        "threads/<uuid:thread_pk>/replies/<uuid:pk>/accept/",
        views.ReplyViewSet.as_view({"post": "accept"}),
        name="reply-accept",
    ),
    path(
        "threads/<uuid:thread_pk>/replies/<uuid:pk>/upvote/",
        views.ReplyViewSet.as_view({"post": "upvote"}),
        name="reply-upvote",
    ),
]
