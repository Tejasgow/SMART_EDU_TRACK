from rest_framework import serializers
from .models import Assignment


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
