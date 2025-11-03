from rest_framework import serializers
from .models import Assignment
from students.models import Student
from .models import AssignmentSubmission
from django.utils import timezone


# ============================================================
# 📌 Assignment Serializer
# ============================================================
class AssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Assignment model.

    Includes:
        - subject_name: Read-only name of the related subject.
        - assigned_by_name: Read-only username of the user who assigned it.
    """
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id',
            'title',
            'descriptions',
            'subject',
            'subject_name',
            'assigned_by',
            'assigned_by_name',
            'file',
            'due_date',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'assigned_by']

    # --------------------------------------------------------
    # Automatically set the user who creates the assignment
    # --------------------------------------------------------
    def create(self, validated_data):
        """
        Assigns the current authenticated user to 'assigned_by' automatically.
        """
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['assigned_by'] = request.user
        return super().create(validated_data)
    
# ============================================================
# 📌 Assignment Submission Serializer   
# ============================================================

class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmission
        fields = [
            'id',
            'assignment',
            'student',
            'submitted_file',
            'submitted_at',
            'grade'
        ]
        read_only_fields = ['id', 'submitted_at']


        def validate(self, attrs):
            """
            Custom validation to ensure a student cannot submit multiple times for the same assignment.
            """
            assignment = attrs.get('assignment')
            student = attrs.get('student')

            today = timezone.now().date()
            if assignment.due_date.date() < today:
                raise serializers.ValidationError("Cannot submit assignment after the due date.")
            if AssignmentSubmission.objects.filter(assignment=assignment, student=student).exists():
                raise serializers.ValidationError("This student has already submitted this assignment.")
            return attrs
        def create(self, validated_data):
            """ Create a new AssignmentSubmission instance. """
            validated_data['student'] = self.context['request'].user
            return super().create(validated_data)
        
class AssignmentSerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField(source='subject.name', read_only=True)
    assigned_by_name = serializers.ReadOnlyField(source='assigned_by.get_full_name', read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'descriptions', 'subject', 'subject_name',
            'assigned_by', 'assigned_by_name', 'file', 'due_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'assigned_by']

        def create(self, validated_data):
            '''
            Automatically assign the current user as the one who created the assignment.

            '''
            user = self.context['request'].user
            validated_data['assigned_by'] = user
            return super().create(validated_data)
           