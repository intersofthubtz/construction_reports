from django.contrib import admin
from .models import Authority, Client, ContractorType, Contractor, WorkCategory

# -----------------------------
# Client Admin
# -----------------------------
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('tin_number', 'name', 'postal_address', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Mark selected clients as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected clients as inactive"

# -----------------------------
# Contractor Type Admin
# -----------------------------
@admin.register(ContractorType)
class ContractorTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Mark selected contractor types as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected contractor types as inactive"

# -----------------------------
# Contractor Admin
# -----------------------------
@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    list_display = ('tin_number', 'name', 'contractor_type', 'city')
    search_fields = ('tin_number', 'name')
    list_filter = ('contractor_type',)


#Work Category Admin can be added similarly when the model is defined
@admin.register(WorkCategory)
class WorkCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
    make_active.short_description = "Mark selected work categories as active"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
    make_inactive.short_description = "Mark selected work categories as inactive"
    

# ---------------- Authority Admin ----------------
@admin.register(Authority)
class AuthorityAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")