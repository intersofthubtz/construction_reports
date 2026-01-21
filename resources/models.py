from django.db import models
from projects.models import Project
from django.contrib.auth.models import User

class Equipment(models.Model):
    CONDITION_CHOICES = (
        ("good", "Good"),
        ("fair", "Fair"),
        ("poor", "Poor"),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="equipment")
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    delivery_date = models.DateField()

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        permissions = [
            # ("access_resources", "Can access resources"),
        ]

    def __str__(self):
        # Use project_name, not name
        return f"{self.name} ({self.project.project_name})"


class Manpower(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="manpower"
    )
    role = models.CharField(max_length=100)
    count = models.PositiveIntegerField()
    start_date = models.DateField(help_text="Month this manpower applies to")

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        if self.project:
            return f"{self.role} - {self.count} ({self.project.project_name})"
        return f"{self.role} - {self.count}"