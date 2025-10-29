from django.db import models
from students.models import Student, Subject
from accounts.models import User

# ============================================================
# 📌 Assignment File Upload Path
# ============================================================
def assignment_upload_path(instance, filename):
    """
    Generates file path for uploaded assignment files.

    Example:
        assignments/<subject_name>/<filename>
    """
    return f"assignments/{instance.subject.name}/{filename}"


# ============================================================
# 📌 Assignment Model
# ============================================================
class Assignment(models.Model):
    """
    Represents an assignment given by a teacher or principal to students.

    Fields:
        - title: Title of the assignment.
        - descriptions: Optional detailed description.
        - subject: Related Subject.
        - assigned_by: User who created the assignment (Teacher or Principal).
        - file: Optional uploaded file.
        - due_date: Deadline for the assignment.
        - created_at: Timestamp of assignment creation.
    """
    title = models.CharField(max_length=200)
    descriptions = models.TextField(blank=True)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_assignments"
    )
    file = models.FileField(
        upload_to=assignment_upload_path,
        blank=True,
        null=True
    )
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'

    def __str__(self):
        """
        Returns a human-readable string representation.
        """
        return f"{self.title} ({self.subject})"
