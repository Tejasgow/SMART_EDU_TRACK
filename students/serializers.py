from rest_framework import serializers
from accounts.models import User
from performance.models import Exam, Mark
from .models import Student, Standard, Section, ParentStudent, Attendance, Subject


# ============================================================
#  STUDENT REGISTRATION SERIALIZER
# ============================================================
class StudentRegistrationSerializer(serializers.ModelSerializer):
    firstname = serializers.CharField(write_only=True)
    lastname = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)
    standard_id = serializers.IntegerField(write_only=True)
    section_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Student
        fields = ["id", "firstname", "lastname", "email", "password", "standard_id", "section_id"]

    def create(self, validated_data):
        """
        Creates a new user with the 'student' role and links it to a Student record.
        """
        user = User.objects.create(
            username=validated_data["email"],
            email=validated_data["email"],
            first_name=validated_data["firstname"],
            last_name=validated_data["lastname"],
            role="STUDENT"
        )
        user.set_password(validated_data["password"])
        user.save()

        # Fetch related standard and section safely
        try:
            standard = Standard.objects.get(id=validated_data["standard_id"])
        except Standard.DoesNotExist:
            raise serializers.ValidationError({"standard_id": "Invalid standard ID."})

        try:
            section = Section.objects.get(id=validated_data["section_id"])
        except Section.DoesNotExist:
            raise serializers.ValidationError({"section_id": "Invalid section ID."})

        # Create student record
        student = Student.objects.create(user=user, standard=standard, section=section)
        return student

    def to_representation(self, instance):
        return {
            "student_id": instance.id,
            "firstname": instance.user.first_name,
            "lastname": instance.user.last_name,
            "email": instance.user.email,
            "standard": instance.standard.name if instance.standard else None,
            "section": instance.section.name if instance.section else None,
            "message": "Student registered successfully"
        }


# ============================================================
#  LINK PARENT TO STUDENT
# ============================================================
class LinkParentSerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField()
    student_id = serializers.IntegerField()

    class Meta:
        model = ParentStudent
        fields = ["id", "parent_id", "student_id"]

    def validate(self, data):
        # Validate parent role
        try:
            User.objects.get(id=data["parent_id"], role="PARENT")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid parent_id or user is not a parent.")

        # Validate student existence
        if not Student.objects.filter(id=data["student_id"]).exists():
            raise serializers.ValidationError("Invalid student_id.")
        return data

    def create(self, validated_data):
        link, _ = ParentStudent.objects.get_or_create(
            parent_id=validated_data["parent_id"],
            student_id=validated_data["student_id"]
        )
        return link

    def to_representation(self, instance):
        return {
            "link_id": instance.id,
            "student": instance.student.user.first_name,
            "parent": instance.parent.first_name,
            "message": "Parent linked to student successfully"
        }


# ============================================================
#  STANDARD AND SECTION SERIALIZERS
# ============================================================
class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["id", "name", "standard"]


class StandardSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Standard
        fields = ["id", "name", "sections"]


# ============================================================
#  ATTENDANCE SERIALIZERS
# ============================================================
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ["id", "student", "date", "status", "marked_by"]
        read_only_fields = ["id", "marked_by"]


class AttendanceMarkSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    date = serializers.DateField()
    status = serializers.ChoiceField(choices=[("PRESENT", "Present"), ("ABSENT", "Absent")])

    def validate_student_id(self, value):
        if not Student.objects.filter(id=value).exists():
            raise serializers.ValidationError("Student with this ID does not exist.")
        return value


class AttendanceDailySerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    standard = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ["date", "status", "student_name", "standard", "section"]

    def get_student_name(self, obj):
        return obj.student.user.first_name

    def get_standard(self, obj):
        return obj.student.standard.name if obj.student.standard else None

    def get_section(self, obj):
        return obj.student.section.name if obj.student.section else None


class AttendanceSummarySerializer(serializers.Serializer):
    student_name = serializers.CharField()
    standard = serializers.CharField()
    section = serializers.CharField()
    total_present = serializers.IntegerField()
    total_absent = serializers.IntegerField()
    attendance_percentage = serializers.CharField()


# ============================================================
#  SUBJECT SERIALIZER
# ============================================================
class SubjectSerializer(serializers.ModelSerializer):
    standard_name = serializers.CharField(source="standard.name", read_only=True)
    teacher_name = serializers.CharField(source="teacher.get_full_name", read_only=True)

    class Meta:
        model = Subject
        fields = ["id", "name", "code", "standard", "standard_name", "teacher", "teacher_name"]


# ============================================================
#  EXAM & MARK SERIALIZERS
# ============================================================
class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ["id", "name", "date", "total_marks"]


class MarkSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)
    recorded_by = serializers.StringRelatedField()

    class Meta:
        model = Mark
        fields = [
            "id", "student", "subject", "exam", "marks_obtained",
            "max_marks", "grade", "remarks", "recorded_by", "updated_at"
        ]
        read_only_fields = ["recorded_by", "updated_at"]
