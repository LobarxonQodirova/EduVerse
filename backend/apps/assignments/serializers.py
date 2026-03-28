"""Serializers for assignments, submissions, rubrics, grades, and feedback."""
from rest_framework import serializers
from apps.accounts.serializers import UserSerializer
from .models import Assignment, Submission, Rubric, Grade, Feedback


class RubricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rubric
        fields = ["id", "assignment", "criterion", "description", "max_points", "order"]
        read_only_fields = ["id"]


class AssignmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for assignment listings."""

    course_title = serializers.CharField(source="course.title", read_only=True)
    submission_count = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            "id", "course", "course_title", "title", "assignment_type",
            "max_score", "due_date", "is_published", "is_past_due",
            "submission_count", "created_at",
        ]

    def get_submission_count(self, obj):
        return obj.submissions.count()


class AssignmentDetailSerializer(serializers.ModelSerializer):
    """Full assignment detail with rubrics."""

    rubrics = RubricSerializer(many=True, read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    has_submitted = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            "id", "course", "course_title", "lesson", "title", "description",
            "assignment_type", "max_score", "due_date", "allow_late_submission",
            "late_penalty_percent", "max_attempts", "attachment", "is_published",
            "is_past_due", "rubrics", "has_submitted", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_has_submitted(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.submissions.filter(student=request.user).exists()
        return False


class AssignmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating assignments."""

    class Meta:
        model = Assignment
        fields = [
            "course", "lesson", "title", "description", "assignment_type",
            "max_score", "due_date", "allow_late_submission",
            "late_penalty_percent", "max_attempts", "attachment", "is_published",
        ]


class FeedbackSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)

    class Meta:
        model = Feedback
        fields = [
            "id", "submission", "author", "author_name", "comment",
            "attachment", "is_private", "created_at",
        ]
        read_only_fields = ["id", "author", "created_at"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class GradeSerializer(serializers.ModelSerializer):
    grader_name = serializers.CharField(source="grader.full_name", read_only=True)

    class Meta:
        model = Grade
        fields = [
            "id", "submission", "grader", "grader_name", "score",
            "max_score", "percentage", "letter_grade",
            "rubric_scores", "graded_at",
        ]
        read_only_fields = ["id", "percentage", "letter_grade", "graded_at"]

    def create(self, validated_data):
        validated_data["grader"] = self.context["request"].user
        return super().create(validated_data)


class SubmissionSerializer(serializers.ModelSerializer):
    """Full submission with grade and feedback."""

    student_detail = UserSerializer(source="student", read_only=True)
    grade = GradeSerializer(read_only=True)
    feedbacks = FeedbackSerializer(many=True, read_only=True)
    is_late = serializers.BooleanField(read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id", "assignment", "student", "student_detail", "status",
            "text_content", "file_upload", "url_link",
            "attempt_number", "is_late", "submitted_at", "updated_at",
            "grade", "feedbacks",
        ]
        read_only_fields = ["id", "student", "attempt_number", "submitted_at", "updated_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        assignment = validated_data["assignment"]
        attempt = Submission.objects.filter(
            student=user, assignment=assignment
        ).count() + 1
        if attempt > assignment.max_attempts:
            raise serializers.ValidationError("Maximum attempts reached.")
        validated_data["student"] = user
        validated_data["attempt_number"] = attempt
        if assignment.due_date and assignment.is_past_due:
            validated_data["status"] = Submission.Status.LATE
        return super().create(validated_data)
