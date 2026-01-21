from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
from sitemanage.models import Activity


# ---------------------------
# MATERIAL TEST
# ---------------------------
class MaterialTest(models.Model):
    MATERIAL_CHOICES = [
        ('Steel', 'Steel'),
        ('Concrete', 'Concrete'),
        ('Blocks', 'Blocks'),
    ]

    RESULT_CHOICES = [
        ('Pass', 'Pass'),
        ('Fail', 'Fail'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    material_type = models.CharField(max_length=20, choices=MATERIAL_CHOICES)
    test_date = models.DateField()
    result = models.CharField(max_length=10, choices=RESULT_CHOICES)
    consultant = models.CharField(max_length=255)
    report_file = models.FileField(upload_to='material_tests/')
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="material_tests"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-test_date"]
        permissions = [
            ("can_approve_material", "Can approve material test"),
        ]

    def __str__(self):
        return f"{self.material_type} - {self.project}"


# ---------------------------
# WORK APPROVAL
# ---------------------------
class WorkApproval(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="work_approvals"
    )
    approval_date = models.DateField(auto_now_add=True)
    remarks = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-approval_date"]
        permissions = [
            ("can_approve_work", "Can approve work"),
        ]

    def __str__(self):
        return f"Approval - {self.activity}"
