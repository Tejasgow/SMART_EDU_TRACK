from rest_framework import serializers
from .models import Mark, Exam


# ============================================================
# 📌 Mark Entry Serializer
# ============================================================
class MarkEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for entering and displaying student marks.
    Includes read-only fields for convenience.
    """
    student_name = serializers.CharField(
        source="student.user.get_full_name", read_only=True
    )
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    recorded_by_name = serializers.CharField(
        source="entered_by.get_full_name", read_only=True
    )

    class Meta:
        model = Mark
        fields = [
            "id",
            "exam",
            "student",
            "student_name",
            "subject",
            "subject_name",
            "marks_obtained",
            "max_marks",
            "remarks",
            "grade",
            "entered_by",
            "recorded_by_name",
            "updated_at",
        ]
        read_only_fields = [
            "grade",
            "updated_at",
            "entered_by",
            "recorded_by_name",
        ]

    # --------------------------------------------------------
    # Validate that marks_obtained does not exceed max_marks
    # --------------------------------------------------------
    def validate(self, data):
        marks_obtained = data.get("marks_obtained")
        max_marks = data.get("max_marks")
        if marks_obtained is not None and max_marks is not None:
            if marks_obtained > max_marks:
                raise serializers.ValidationError(
                    "Marks obtained cannot exceed max marks."
                )
        return data

    # --------------------------------------------------------
    # Automatically assign current user as entered_by
    # --------------------------------------------------------
    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["entered_by"] = request.user
        return super().create(validated_data)


# ============================================================
# 📌 Exam Serializer
# ============================================================
class ExamSerializer(serializers.ModelSerializer):
    """
    Serializer for Exam model.
    Includes read-only fields for related names.
    """
    standard_name = serializers.CharField(source="standard.name", read_only=True)
    section_name = serializers.CharField(source="section.name", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.get_full_name", read_only=True
    )

    class Meta:
        model = Exam
        fields = [
            "id",
            "name",
            "date",
            "standard",
            "standard_name",
            "section",
            "section_name",
            "created_by",
            "created_by_name",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_by_name", "created_at"]

    # --------------------------------------------------------
    # Automatically assign current user as created_by
    # --------------------------------------------------------
    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["created_by"] = request.user
        return super().create(validated_data)
