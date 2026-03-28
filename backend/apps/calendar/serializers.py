"""Serializers for calendar events, deadlines, and schedules."""
from rest_framework import serializers
from .models import Event, Deadline, Schedule


class EventSerializer(serializers.ModelSerializer):
    duration = serializers.DurationField(read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True, default=None)
    creator_name = serializers.CharField(source="creator.full_name", read_only=True)

    class Meta:
        model = Event
        fields = [
            "id", "course", "course_title", "creator", "creator_name",
            "title", "description", "event_type",
            "start_time", "end_time", "duration",
            "location", "meeting_url", "is_all_day",
            "recurrence", "recurrence_end_date", "color",
            "is_cancelled", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "creator", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, attrs):
        if attrs.get("end_time") and attrs.get("start_time"):
            if attrs["end_time"] <= attrs["start_time"]:
                raise serializers.ValidationError("End time must be after start time.")
        return attrs


class DeadlineSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    is_past_due = serializers.BooleanField(read_only=True)

    class Meta:
        model = Deadline
        fields = [
            "id", "course", "course_title", "title", "description",
            "deadline_type", "due_date", "priority",
            "assignment", "quiz", "reminder_sent",
            "is_past_due", "created_at",
        ]
        read_only_fields = ["id", "reminder_sent", "created_at"]


class ScheduleSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source="get_day_of_week_display", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Schedule
        fields = [
            "id", "course", "course_title", "title",
            "day_of_week", "day_name", "start_time", "end_time",
            "location", "meeting_url", "is_active",
            "effective_from", "effective_until", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        if attrs.get("end_time") and attrs.get("start_time"):
            if attrs["end_time"] <= attrs["start_time"]:
                raise serializers.ValidationError("End time must be after start time.")
        return attrs
