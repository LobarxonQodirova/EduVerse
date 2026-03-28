"""Serializers for discussion forums, threads, and replies."""
from rest_framework import serializers
from apps.accounts.serializers import UserSerializer
from .models import DiscussionForum, Thread, Reply


class ReplySerializer(serializers.ModelSerializer):
    author_detail = UserSerializer(source="author", read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Reply
        fields = [
            "id", "thread", "author", "author_detail", "parent", "body",
            "is_accepted_answer", "upvotes", "is_edited",
            "children", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "author", "is_edited", "upvotes", "created_at", "updated_at"]

    def get_children(self, obj):
        children = obj.children.select_related("author").all()
        return ReplySerializer(children, many=True).data

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class ThreadListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    reply_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Thread
        fields = [
            "id", "forum", "author", "author_name", "title",
            "thread_type", "is_pinned", "is_locked", "is_resolved",
            "view_count", "upvotes", "reply_count", "created_at",
        ]


class ThreadDetailSerializer(serializers.ModelSerializer):
    author_detail = UserSerializer(source="author", read_only=True)
    replies = serializers.SerializerMethodField()
    reply_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Thread
        fields = [
            "id", "forum", "author", "author_detail", "title", "body",
            "thread_type", "is_pinned", "is_locked", "is_resolved",
            "view_count", "upvotes", "reply_count",
            "replies", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "author", "view_count", "upvotes", "created_at", "updated_at"]

    def get_replies(self, obj):
        top_level = obj.replies.filter(parent__isnull=True).select_related("author")
        return ReplySerializer(top_level, many=True).data


class ThreadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = ["forum", "title", "body", "thread_type"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class DiscussionForumSerializer(serializers.ModelSerializer):
    thread_count = serializers.IntegerField(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = DiscussionForum
        fields = [
            "id", "course", "course_title", "title", "description",
            "is_locked", "allow_anonymous", "thread_count", "reply_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
