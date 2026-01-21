from django.contrib import admin
from django.utils.html import format_html
from .models import Activity, ProgressLog, SiteProjectImage, SiteVisitor


# ---------------------------
# ACTIVITY ADMIN
# ---------------------------
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'project',
        'category',
        'planned_start',
        'planned_end',
        'status_badge',
        'progress_percent',
        'is_active',
    )

    list_editable = ('is_active',)

    list_filter = (
        'status',
        'category',
        'project',
        'is_active',
    )

    search_fields = (
        'name',
        'project__name',
    )

    readonly_fields = (
        'status',
        'progress_percent',
        'actual_start',
        'actual_end',
        'created_at',
        'updated_at',
    )

    fieldsets = (
        ('Activity Info', {
            'fields': ('project', 'category', 'name', 'description', 'is_active')
        }),
        ('Planned Schedule', {
            'fields': ('planned_start', 'planned_end')
        }),
        ('System Controlled', {
            'fields': ('progress_percent', 'status', 'actual_start', 'actual_end')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by')
        }),
    )

    def status_badge(self, obj):
        colors = {
            'Pending': 'gray',
            'In Progress': 'blue',
            'Completed': 'green',
            'Delayed': 'red',
        }
        return format_html(
            '<span style="padding:4px 8px;border-radius:8px;background:{};color:white;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.status
        )
    status_badge.short_description = "Status"


# ---------------------------
# PROGRESS LOG ADMIN
# ---------------------------
@admin.register(ProgressLog)
class ProgressLogAdmin(admin.ModelAdmin):
    list_display = (
        'activity',
        'date',
        'progress_percent',
        'created_by',
        'created_at',
    )

    list_filter = (
        'activity__project',
        'date',
    )

    search_fields = (
        'activity__name',
        'activity__project__name',
    )

    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)



@admin.register(SiteVisitor)
class SiteVisitorAdmin(admin.ModelAdmin):
    list_display = (
        "document_name",
        "project",
        "visit_date",
        "is_active",
        "created_by",
        "created_at",
    )

    list_filter = (
        "project",
        "visit_date",
        "is_active",
    )

    search_fields = (
        "document_name",
        "project__name",
    )

    ordering = ("-visit_date",)

    readonly_fields = (
        "created_by",
        "created_at",
    )

    fieldsets = (
        ("Visitor Document", {
            "fields": (
                "project",
                "document_name",
                "document_file",
                "visit_date",
            )
        }),
        ("Status", {
            "fields": (
                "is_active",
            )
        }),
        ("Audit", {
            "fields": (
                "created_by",
                "created_at",
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        """Auto-assign creator"""
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        
        
@admin.register(SiteProjectImage)
class SiteProjectImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "project_name",
        "figure_name",
        "image_date",
        "image_preview",
        "is_active",
        "created_by",
        "created_at",
    )
    list_filter = ("project", "image_date", "is_active")
    search_fields = ("project__project_name", "figure_name")
    readonly_fields = ("created_by", "created_at", "image_preview")
    ordering = ("-image_date", "-created_at")

    # Optional: add image preview in admin
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = "Preview"

    def project_name(self, obj):
        return obj.project.project_name
    project_name.admin_order_field = "project__project_name"
    project_name.short_description = "Project"

    # Automatically set created_by if saving in admin
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # only set on create
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
