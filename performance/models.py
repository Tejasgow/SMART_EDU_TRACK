from django.db import models
from accounts.models import User
from students.models import Student, Standard, Section, Subject


# ============================================================
# 📌 Exam Model
# ============================================================
class Exam(models.Model):
    """
    Represents an exam for a particular standard and section.
    """
    name = models.CharField(
        max_length=100,
        help_text="Name of the exam, e.g., Midterm Test"
    )
    date = models.DateField(help_text="Exam date")
    standard = models.ForeignKey(
        Standard, on_delete=models.CASCADE, related_name="exams"
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="exams"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['TEACHER', 'ADMIN']},
        related_name="created_exams",
        help_text="User who created the exam"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('name', 'standard', 'section')

    def __str__(self):
        return f"{self.name} - {self.standard.name} {self.section.name}"


# ============================================================
# 📌 Mark Model
# ============================================================
class Mark(models.Model):
    """
    Represents marks obtained by a student for a particular subject and exam.
    """
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="marks")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="marks")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="marks")
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    max_marks = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True, null=True)
    grade = models.CharField(max_length=3, blank=True, null=True)
    entered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__in': ['TEACHER', 'ADMIN']},
        related_name="entered_marks",
        help_text="User who entered the marks"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('exam', 'student', 'subject')
        ordering = ['exam__date', 'subject__name']

    # --------------------------------------------------------
    # Override save to validate marks and auto-calculate grade
    # --------------------------------------------------------
    def save(self, *args, **kwargs):
        # Validation: marks_obtained cannot exceed max_marks
        if self.marks_obtained > self.max_marks:
            raise ValueError("Marks obtained cannot exceed max marks.")

        # Auto-calculate grade based on percentage
        percentage = (self.marks_obtained / self.max_marks) * 100
        if percentage >= 90:
            self.grade = "A+"
        elif percentage >= 75:
            self.grade = "A"
        elif percentage >= 60:
            self.grade = "B"
        elif percentage >= 45:
            self.grade = "C"
        else:
            self.grade = "D"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.subject.name} ({self.exam.name})"
