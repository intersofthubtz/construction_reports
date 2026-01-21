from django.contrib import admin
from .models import Compliance

# admin.py
@admin.register(Compliance)
class ComplianceAdmin(admin.ModelAdmin):
    list_display = (
        'project',
        'authority',
        'registration_no',
        'status',
        'expiry_date',
        'is_active',
    )
    list_filter = ('authority', 'status', 'is_active')
    search_fields = ('registration_no', 'project__project_name')
    ordering = ('expiry_date',)

