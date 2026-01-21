from django.db import models
from django.contrib.auth.models import User


class Client(models.Model):
    tin_number = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=255)
    postal_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        permissions = [
            # ("access_setup", "Can access setup module"),
            # ("access_clients", "Can access client module"),
            # ("create_clients", "Can create clients"),
            # ("edit_clients", "Can edit clients"),
            # ("delete_clients", "Can delete clients"),
        ]

    def __str__(self):
        return self.name
    

class ContractorType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        permissions = [
            # ("view_contractor_types", "Can view contractor types"),
            # ("create_contractor_types", "Can create contractor types"),
            # ("edit_contractor_types", "Can edit contractor types"),
            # ("delete_contractor_types", "Can delete contractor types"),
        ]

    def __str__(self):
        return self.name


class Contractor(models.Model):
    tin_number = models.CharField(max_length=20, primary_key=True)
    contractor_type = models.ForeignKey(ContractorType, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        permissions = [
            # ("view_contractors", "Can view contractors"),
            # ("create_contractors", "Can create contractors"),
            # ("edit_contractors", "Can edit contractors"),
            # ("delete_contractors", "Can delete contractors"),
        ]

    def __str__(self):
        return f"{self.name} ({self.contractor_type.name})"


class ProjectRole(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_project_roles",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                condition=models.Q(is_active=True),
                name="unique_active_project_role_name",
            )
        ]

    def __str__(self):
        return self.name
    

class WorkCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_work_categories"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                condition=models.Q(is_active=True),
                name="unique_active_work_category_name",
            )
        ]

    def __str__(self):
        return self.name

    
class Authority(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_authorities"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                condition=models.Q(is_active=True),
                name="unique_active_authority_name",
            )
        ]

    def __str__(self):
        return self.name
