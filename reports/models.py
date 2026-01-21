from django.db import models
from django.contrib.auth.models import User
from projects.models import Project


class ProgressReportCover(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    report_no = models.PositiveIntegerField()
    report_title = models.CharField(max_length=255)

    period_from = models.DateField()
    period_to = models.DateField()

    prepared_by = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to="report_covers/", null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.project_name} - Report {self.report_no}"


# ---------------------------
# PROJECT REPORT
# ---------------------------
class ProjectReport(models.Model):
    """
    Dummy model for Project Reports permissions.
    """
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False  # No DB table
        # permissions = [
            # ("view_projectreport", "Can view Project Report"),
        # ]

    def __str__(self):
        return "Project Report"

# ---------------------------
# PROGRESS REPORT
# ---------------------------
class ProgressReport(models.Model):
    """
    Dummy model for Project Reports permissions.
    """
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False  # No DB table
        # permissions = [
            # ("view_projectreport", "Can view Project Report"),
        # ]

    def __str__(self):
        return "Progress Report"
    
# ---------------------------
# RESOURCES REPORT
# ---------------------------
class ResourcesReport(models.Model):
    """
    Dummy model for Resources Reports permissions.
    """
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False  # No database table will be created
        # permissions = [
        #     ("view_resourcesreport", "Can view Resources Report"),
        # ]

    def __str__(self):
        return "Resources Report"
    
# ---------------------------
# FINANCE REPORT
# ---------------------------
class FinanceReport(models.Model):
    """
    Dummy model for Finance Reports permissions.
    """
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        # permissions = [
            # ("view_financereport", "Can view Finance Report"),
        # ]

    def __str__(self):
        return "Finance Report"


# ---------------------------
# QUALITY REPORT
# ---------------------------
class QualityReport(models.Model):
    """
    Dummy model for Quality Reports permissions.
    """
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        # permissions = [
            # ("view_qualityreport", "Can view Quality Report"),
        # ]

    def __str__(self):
        return "Quality Report"
