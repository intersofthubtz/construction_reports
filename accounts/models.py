from django.db import models

class Dashboard(models.Model):
    """
    Dummy model for dashboard permissions.
    We only use default Django permissions (add, change, delete, view).
    """
    class Meta:
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboard"
