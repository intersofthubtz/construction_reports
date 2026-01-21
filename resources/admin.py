from django.contrib import admin
from .models import Equipment, Manpower

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("name", "project_name", "category", "quantity", "condition", "is_active")
    list_filter = ("condition", "category", "is_active")
    search_fields = ("name", "project__project_name")

    def project_name(self, obj):
        return obj.project.project_name
    project_name.admin_order_field = "project__project_name"
    project_name.short_description = "Project"

@admin.register(Manpower)
class ManpowerAdmin(admin.ModelAdmin):
    list_display = ("role", "count", "project_name", "start_date", "is_active")
    list_filter = ("start_date", "is_active")
    search_fields = ("role", "project__project_name")

    def project_name(self, obj):
        return obj.project.project_name if obj.project else "-"
    project_name.admin_order_field = "project__project_name"
    project_name.short_description = "Project"
