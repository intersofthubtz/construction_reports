from django.contrib import admin
from django.utils.html import format_html
from .models import MaterialTest, WorkApproval


# ---------------------------
# MATERIAL TEST ADMIN
# ---------------------------
@admin.register(MaterialTest)
class MaterialTestAdmin(admin.ModelAdmin):
    list_display = (
        'project',
        'material_type',
        'test_date',
        'result_badge',
        'consultant',
        'is_active',
        'created_by',
        'created_at',
    )

    list_filter = (
        'material_type',
        'result',
        'project',
        'is_active',
    )

    search_fields = (
        'project__name',
        'consultant',
        'material_type',
    )

    list_editable = ('is_active',)  # make is_active editable directly in the list

    readonly_fields = ('created_by', 'created_at')

    fieldsets = (
        ('Material Test Info', {
            'fields': (
                'project',
                'material_type',
                'test_date',
                'result',
                'consultant',
                'report_file',
                'is_active',
            )
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at')
        }),
    )

    def result_badge(self, obj):
        color = 'green' if obj.result == 'Pass' else 'red'
        return format_html(
            '<span style="padding:4px 8px; border-radius:6px; background-color:{}; color:white;">{}</span>',
            color,
            obj.result
        )
    result_badge.short_description = "Result"

    # Automatically set created_by on save
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# ---------------------------
# WORK APPROVAL ADMIN
# ---------------------------
@admin.register(WorkApproval)
class WorkApprovalAdmin(admin.ModelAdmin):
    list_display = (
        'activity_display',
        'approved_by',
        'approval_date',
        'remarks',
        'is_active',
    )

    list_filter = (
        'activity__project',
        'approved_by',
        'is_active',
    )

    search_fields = (
        'activity__name',
        'activity__project__name',
        'approved_by__username',
        'remarks',
    )

    list_editable = ('is_active',)

    readonly_fields = ('approved_by', 'approval_date')

    fieldsets = (
        ('Work Approval Info', {
            'fields': (
                'activity',
                'remarks',
                'is_active',
            )
        }),
        ('Audit', {
            'fields': (
                'approved_by',
                'approval_date',
            )
        }),
    )

    def activity_display(self, obj):
        return f"{obj.activity.name} ({obj.activity.project.name})"
    activity_display.short_description = "Activity"

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.approved_by = request.user
        super().save_model(request, obj, form, change)
