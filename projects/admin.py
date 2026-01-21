from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Project,
    ProjectContractor,
    ProjectParticipant,
    ProjectDocument,
    ProjectRole,
)
from django.contrib.auth.models import User


# -----------------------------
# Inline Admins
# -----------------------------

class ProjectContractorInline(admin.TabularInline):
    model = ProjectContractor
    extra = 1
    autocomplete_fields = ["contractor"]
    fields = ("contractor", "work_description")
    show_change_link = True


class ProjectParticipantInline(admin.StackedInline):
    model = ProjectParticipant
    extra = 1
    autocomplete_fields = ["user", "project_role"]
    fields = ("user", "project_role")
    show_change_link = True


class ProjectDocumentInline(admin.StackedInline):
    model = ProjectDocument
    extra = 1
    fields = ("title", "document", "uploaded_by", "uploaded_at")
    readonly_fields = ("uploaded_by", "uploaded_at")
    show_change_link = True


# -----------------------------
# Project Admin
# -----------------------------

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "project_code",
        "project_name",
        "client",
        "location",
        "contract_sum",
        "contract_duration_months",
        "created_by",
        "is_active",
    )
    list_filter = ("is_active", "client", "created_at")
    search_fields = ("project_code", "project_name", "client__name", "location")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [ProjectContractorInline, ProjectParticipantInline, ProjectDocumentInline]

    fieldsets = (
        ("Project Information", {
            "fields": ("project_code", "project_name", "client", "location")
        }),
        ("Financial Details", {
            "fields": ("contract_sum", "contract_duration_months")
        }),
        ("Contract Dates", {
            "fields": (
                "contract_signing_date",
                "site_possession_date",
                "mobilization_start",
                "mobilization_end",
                "commencement_date",
                "practical_completion_date",
            )
        }),
        ("Defects & Delays", {
            "fields": (
                "delay_status",
                "defects_liability_period_days",
                "defects_start",
                "defects_end",
            )
        }),
        ("System", {
            "fields": ("created_by", "is_active", "created_at", "updated_at")
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        Automatically set 'uploaded_by' for ProjectDocument inlines
        """
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, ProjectDocument) and not instance.uploaded_by:
                instance.uploaded_by = request.user
            instance.save()
        formset.save_m2m()


# -----------------------------
# ProjectContractor Admin
# -----------------------------

@admin.register(ProjectContractor)
class ProjectContractorAdmin(admin.ModelAdmin):
    list_display = ("project", "contractor", "work_description")
    search_fields = ("project__project_name", "contractor__name")
    autocomplete_fields = ("project", "contractor")


# -----------------------------
# ProjectParticipant Admin
# -----------------------------

@admin.register(ProjectParticipant)
class ProjectParticipantAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "project_role")
    list_filter = ("project_role",)
    search_fields = ("project__project_name", "user__username")
    autocomplete_fields = ("project", "user", "project_role")


# -----------------------------
# ProjectDocument Admin
# -----------------------------

@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "uploaded_by", "uploaded_at", "download_link")
    search_fields = ("title", "project__project_name")
    readonly_fields = ("uploaded_by", "uploaded_at")

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

    def download_link(self, obj):
        if obj.document:
            return format_html(
                '<a href="{}" target="_blank" class="text-blue-600 hover:underline">📥 Download</a>',
                obj.document.url
            )
        return "-"
    download_link.short_description = "Document"


# -----------------------------
# ProjectRole Admin (for autocomplete)
# -----------------------------

@admin.register(ProjectRole)
class ProjectRoleAdmin(admin.ModelAdmin):
    search_fields = ["name"]  # required for autocomplete_fields
