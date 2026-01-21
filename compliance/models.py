from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
from setup.models import Authority 

class Compliance(models.Model):

    STATUS_CHOICES = [
        ('Valid', 'Valid'),
        ('Expired', 'Expired'),
        ('Pending', 'Pending'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    authority = models.ForeignKey(
        Authority,
        on_delete=models.PROTECT,
        related_name="compliances"
    )

    registration_no = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    expiry_date = models.DateField()

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['expiry_date']
        permissions = [
            ("can_approve_compliance", "Can approve compliance"),
        ]

    def __str__(self):
        return f"{self.authority.name} - {self.project}"
