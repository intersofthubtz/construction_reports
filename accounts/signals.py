from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission, User

@receiver(post_migrate)
def create_or_update_groups(sender, **kwargs):
    """
    Create/update roles and assign permissions automatically.
    """
    # Define permissions per role
    role_permissions = {
        "Administrator": "__all__",
        "Construction Manager": [
            # Dashboard
            "view_dashboard",
            # Projects
            "view_project", "add_project", "change_project", "delete_project",
            # Reports
            "view_progresslog", "add_progresslog", "change_progresslog",
            "view_financereport", "add_financereport", "change_financereport",
            "view_projectreport",
            # Site management
            "access_sitemanage",
            "view_activity", "add_activity", "change_activity",
            # Finance
            "view_fundtransaction", "add_fundtransaction", "change_fundtransaction",
            "view_paymentcertificate", "add_paymentcertificate", "change_paymentcertificate",
        ],
        "Site Engineer": [
            # Dashboard
            "view_dashboard",
            # Projects
            "view_project", "add_project", "change_project",
            # Reports
            "view_progressreport", "add_progressreport", "change_progressreport",
            # Site management
            "view_activity",
            "view_activity", "add_activity", "change_activity",
            "view_progresslog", "add_progresslog", "change_progresslog",
        ],
        "Quantity Surveyor": [
            # Dashboard
            "view_dashboard",
            # Finance
            "view_fundtransaction", "add_fundtransaction", "change_fundtransaction",
            "view_paymentcertificate", "add_paymentcertificate", "change_paymentcertificate",
            # Reports
            "view_financereport", "add_financereport", "change_financereport",
        ],
        "Civil Engineer": [
            # Dashboard
            "view_dashboard",
            # Projects
            "view_project",
            # Site management
            "view_activity", "add_activity", "change_activity",
            "view_progresslog", "add_progresslog", "change_progresslog",
            # Quality
            "view_materialtest", "add_materialtest", "change_materialtest",
            "view_workapproval", "add_workapproval", "change_workapproval",
        ],
        "Architect": [
            # Dashboard
            "view_dashboard",
            # Projects
            "view_project",
            # Site management
            "view_sitemanage",
            # Quality
            "view_materialtest", "add_materialtest", "change_materialtest",
        ],
        "Administrative Officer": [
            # Dashboard
            "view_dashboard",
            # Setup
            "view_client", "add_client", "change_client", "delete_client",
            "view_contractor", "add_contractor", "change_contractor", "delete_contractor",
            "view_authority", "add_authority", "change_authority", "delete_authority",
        ],
        "Director": [
            # Dashboard
            "view_dashboard",
            # Reports
            "view_progressreport", "view_financereport", "view_projectreport",
            "view_qualityreport", "view_resourcesreport",
            # Compliance
            "view_compliance", "approve_compliance",
        ],
    }

    all_permissions = Permission.objects.all()

    for group_name, perm_codenames in role_permissions.items():
        group, _ = Group.objects.get_or_create(name=group_name)

        if perm_codenames == "__all__":
            group.permissions.set(all_permissions)
        else:
            valid_permissions = Permission.objects.filter(codename__in=perm_codenames)
            group.permissions.set(valid_permissions)

        group.save()

        # Optional: auto-assign superuser for Administrator
        if group_name == "Administrator":
            for user in User.objects.filter(groups__name="Administrator"):
                user.is_superuser = True
                user.is_staff = True
                user.user_permissions.set(all_permissions)
                user.save()
