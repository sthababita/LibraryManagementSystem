from django.contrib.auth.models import User
from django.db import models


class Course(models.Model):
    """Represents a course taught by an instructor."""

    DIFFICULTY_CHOICES = [
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Advanced", "Advanced"),
    ]

    name = models.CharField(max_length=255)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    """Tracks student enrollment in courses."""

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    progress = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.name}"


class Assignment(models.Model):
    """Assignments associated with courses."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=255)
    description = models.TextField()
    max_marks = models.IntegerField()
    due_date = models.DateTimeField()

    def __str__(self):
        return f"{self.title} ({self.course.name})"


class Notification(models.Model):
    """Stores notifications for users."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}..."


class Sponsorship(models.Model):
    """Sponsors fund students for specific courses."""

    sponsor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sponsorships")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sponsored_students")
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="sponsorships",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[("Active", "Active"), ("Completed", "Completed")],
        default="Active",
    )
    pidx = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sponsor.username} -> {self.student.username} (${self.amount})"


class Payment(models.Model):
    """Stores raw payment info if needed separately from Sponsorship."""

    sponsor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_payments")
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    pidx = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("PENDING", "Pending"), ("COMPLETED", "Completed"), ("FAILED", "Failed")],
        default="PENDING",
    )
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sponsor.username} -> {self.student.username} (${self.amount})"
