# A - Import Required Modules
from django.contrib import admin
from .models import RequisitionProfile, Requisition

# B - Azure Admin Email
AZURE_ADMIN_EMAIL = 'admin@dzignscapeprofessionals.onmicrosoft.com'

# C - Mixin: Restrict Admin Access to Azure Admin
class AzureAdminOnlyMixin:
    def has_module_permission(self, request):
        return request.user.email == AZURE_ADMIN_EMAIL

    def has_view_permission(self, request, obj=None):
        return request.user.email == AZURE_ADMIN_EMAIL

    def has_change_permission(self, request, obj=None):
        return request.user.email == AZURE_ADMIN_EMAIL

    def has_delete_permission(self, request, obj=None):
        return request.user.email == AZURE_ADMIN_EMAIL

# D - RequisitionProfile Admin
@admin.register(RequisitionProfile)
class RequisitionProfileAdmin(AzureAdminOnlyMixin, admin.ModelAdmin):
    list_display = ['user', 'role']
    list_filter = ['role']
    search_fields = ['user__username']
    ordering = ['user__username']

# E - Requisition Admin
@admin.register(Requisition)
class RequisitionAdmin(AzureAdminOnlyMixin, admin.ModelAdmin):
    list_display = ['project_name_requisition', 'requisition_no', 'created_by', 'team', 'created_at']
    list_filter = ['team', 'created_by']
    search_fields = ['project_name_requisition', 'requisition_no', 'created_by__username']
    ordering = ['-created_at']
