"""Discussion views: forums, threads, and replies."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permissions import IsInstructorOrAdmin
from .models import DiscussionForum, Thread, Reply
from .serializers import (
    DiscussionForumSerializer,
    ThreadListSerializer,
    ThreadDetailSerializer,
    ThreadCreateSerializer,
    ReplySerializer,
)


class DiscussionForumViewSet(viewsets.ModelViewSet):
    """Manage discussion forums. One per course, managed by instructors."""

    serializer_class = DiscussionForumSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["course"]

    def get_queryset(self):
        user = self.request.user
        qs = DiscussionForum.objects.select_related("course")
        if user.role == "student":
            qs = qs.filter(
                course__enrollments__student=user,
                course__enrollments__is_active=True,
            )
        elif user.role == "instructor":
            qs = qs.filter(course__instructor=user)
        return qs.distinct()

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsInstructorOrAdmin()]
        return [IsAuthenticated()]


class ThreadViewSet(viewsets.ModelViewSet):
    """Manage threads within a discussion forum."""

    permission_classes = [IsAuthenticated]
    filterset_fields = ["thread_type", "is_resolved", "is_pinned"]
    search_fields = ["title", "body"]
    ordering_fields = ["created_at", "upvotes", "view_count"]

    def get_queryset(self):
        return Thread.objects.filter(
            forum_id=self.kwargs["forum_pk"]
        ).select_related("author")

    def get_serializer_class(self):
        if self.action == "create":
            return ThreadCreateSerializer
        if self.action == "retrieve":
            return ThreadDetailSerializer
        return ThreadListSerializer

    def retrieve(self, request, *args, **kwargs):
        """Increment view count on retrieval."""
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=["view_count"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        forum = DiscussionForum.objects.get(pk=self.kwargs["forum_pk"])
        if forum.is_locked:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("This forum is locked.")
        serializer.save(forum=forum)

    @action(detail=True, methods=["post"])
    def upvote(self, request, forum_pk=None, pk=None):
        thread = self.get_object()
        thread.upvotes += 1
        thread.save(update_fields=["upvotes"])
        return Response({"upvotes": thread.upvotes})

    @action(detail=True, methods=["post"])
    def resolve(self, request, forum_pk=None, pk=None):
        thread = self.get_object()
        thread.is_resolved = True
        thread.save(update_fields=["is_resolved"])
        return Response({"is_resolved": True})


class ReplyViewSet(viewsets.ModelViewSet):
    """Manage replies within a thread."""

    serializer_class = ReplySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_queryset(self):
        return Reply.objects.filter(
            thread_id=self.kwargs["thread_pk"],
            parent__isnull=True,
        ).select_related("author").prefetch_related("children__author")

    def perform_create(self, serializer):
        thread = Thread.objects.get(pk=self.kwargs["thread_pk"])
        if thread.is_locked:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("This thread is locked.")
        serializer.save(thread=thread)

    @action(detail=True, methods=["post"])
    def accept(self, request, thread_pk=None, pk=None):
        """Mark a reply as the accepted answer."""
        reply = self.get_object()
        Reply.objects.filter(thread=reply.thread, is_accepted_answer=True).update(
            is_accepted_answer=False
        )
        reply.is_accepted_answer = True
        reply.save(update_fields=["is_accepted_answer"])
        reply.thread.is_resolved = True
        reply.thread.save(update_fields=["is_resolved"])
        return Response({"is_accepted_answer": True})

    @action(detail=True, methods=["post"])
    def upvote(self, request, thread_pk=None, pk=None):
        reply = self.get_object()
        reply.upvotes += 1
        reply.save(update_fields=["upvotes"])
        return Response({"upvotes": reply.upvotes})
