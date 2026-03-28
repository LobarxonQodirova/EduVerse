"""Calendar views: events, deadlines, and schedules."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from apps.accounts.permissions import IsInstructorOrAdmin
from .models import Event, Deadline, Schedule
from .serializers import EventSerializer, DeadlineSerializer, ScheduleSerializer


class EventViewSet(viewsets.ModelViewSet):
    """Manage calendar events."""

    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["course", "event_type", "is_cancelled"]
    search_fields = ["title", "description"]
    ordering_fields = ["start_time", "created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = Event.objects.select_related("course", "creator")
        if user.role == "student":
            qs = qs.filter(
                course__enrollments__student=user,
                course__enrollments__is_active=True,
            )
        elif user.role == "instructor":
            qs = qs.filter(creator=user)
        return qs.distinct()

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsInstructorOrAdmin()]
        return [IsAuthenticated()]

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """List events in the next 7 days."""
        now = timezone.now()
        week_later = now + timedelta(days=7)
        events = self.get_queryset().filter(
            start_time__gte=now, start_time__lte=week_later, is_cancelled=False
        )
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def month(self, request):
        """List events for a given month. Query params: year, month."""
        year = int(request.query_params.get("year", timezone.now().year))
        month = int(request.query_params.get("month", timezone.now().month))
        events = self.get_queryset().filter(
            start_time__year=year, start_time__month=month
        )
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)


class DeadlineViewSet(viewsets.ModelViewSet):
    """Manage course deadlines."""

    serializer_class = DeadlineSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["course", "deadline_type", "priority"]
    ordering_fields = ["due_date"]

    def get_queryset(self):
        user = self.request.user
        qs = Deadline.objects.select_related("course")
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

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """List deadlines in the next 14 days."""
        now = timezone.now()
        two_weeks = now + timedelta(days=14)
        deadlines = self.get_queryset().filter(
            due_date__gte=now, due_date__lte=two_weeks
        )
        serializer = self.get_serializer(deadlines, many=True)
        return Response(serializer.data)


class ScheduleViewSet(viewsets.ModelViewSet):
    """Manage recurring course schedules."""

    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["course", "day_of_week", "is_active"]

    def get_queryset(self):
        user = self.request.user
        qs = Schedule.objects.select_related("course")
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

    @action(detail=False, methods=["get"])
    def today(self, request):
        """List schedules for today's day of the week."""
        today = timezone.now().date()
        day_of_week = today.weekday()
        schedules = self.get_queryset().filter(
            day_of_week=day_of_week, is_active=True,
            effective_from__lte=today,
        ).exclude(effective_until__lt=today)
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)
