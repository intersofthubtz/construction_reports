from django.contrib.auth.models import User
from django.db import models
from setup.models import Contractor, ContractorType, Client, ProjectRole
from django.core.validators import FileExtensionValidator


class Project(models.Model):
    project_code = models.CharField(max_length=50, unique=True)
    project_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="projects"
    )

    # Financial
    contract_sum = models.DecimalField(max_digits=18, decimal_places=2)
    contract_duration_months = models.PositiveIntegerField()

    # Contract details
    contract_signing_date = models.DateField()
    site_possession_date = models.DateField()
    mobilization_start = models.DateField()
    mobilization_end = models.DateField()
    commencement_date = models.DateField()
    practical_completion_date = models.DateField()

    # Delay & defects
    delay_status = models.CharField(max_length=100, default="Nil")
    defects_liability_period_days = models.PositiveIntegerField(default=365)
    defects_start = models.DateField(null=True, blank=True)
    defects_end = models.DateField(null=True, blank=True)

    # System
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        permissions = [("access_projects", "Can access projects")]

    def __str__(self):
        return f"{self.project_name} ({self.client.name})"


class ProjectDocument(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents")
    title = models.CharField(max_length=255)
    document = models.FileField(
        upload_to="project_documents/",
        validators=[FileExtensionValidator(["pdf"])]
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class ProjectParticipant(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="participants"); 
    user = models.ForeignKey(User, on_delete=models.CASCADE); 
    project_role = models.ForeignKey(ProjectRole, on_delete=models.PROTECT); 
    is_active = models.BooleanField(default=True)

    class Meta: ordering = ["project_role"]

    def __str__(self): return f"{self.user.username} – {self.project_role.name}"


class ProjectContractor(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="contractors")
    contractor = models.ForeignKey(Contractor, on_delete=models.PROTECT)
    work_description = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("project", "contractor")

    def __str__(self):
        return f"{self.contractor} – {self.project.project_name}"
