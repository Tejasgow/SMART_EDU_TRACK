from django.db import models
from accounts.models import User

# -------------------------
# Standard Model
# -------------------------
class Standard(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


# -------------------------
# Section Model
# -------------------------
class Section(models.Model):
    name = models.CharField(max_length=5)
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, related_name="sections")

    class Meta:
        unique_together = ('name', 'standard')
        verbose_name_plural = "Sections"

    def __str__(self):
        return f"{self.standard.name} - {self.name}"


# -------------------------
# Student Model
# -------------------------
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    standard = models.ForeignKey(Standard, on_delete=models.SET_NULL, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name()


# -------------------------
# Parent-Student Link Model
# -------------------------
class ParentStudent(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'PARENT'})
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="parents")

    class Meta:
        unique_together = ('parent', 'student')

    def __str__(self):
        return f"{self.parent.get_full_name()} ↔ {self.student.user.get_full_name()}"


# -------------------------
# Attendance Model
# -------------------------
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent')
    ]

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "STUDENT"},
        related_name="attendances"
    )
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="attendance_marked"
    )

    class Meta:
        unique_together = ('student', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.status}"


# -------------------------
# Subject Model
# -------------------------
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    standard = models.ForeignKey(Standard, on_delete=models.CASCADE, related_name='subjects')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'TEACHER'})

    def __str__(self):
        return f"{self.name} ({self.standard.name})"
