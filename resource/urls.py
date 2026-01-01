from django.urls import path
from . import views

urlpatterns = [
    # 🔹 Team dashboard: Team members see their own
    path('dashboard/', views.resource_dashboard, name='resource_dashboard'),

    # 🛡️ Admin dashboard (read-only)
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # ✏️ Edit resource entry: Team members only (their own)
    path('dashboard/edit/<int:pk>/', views.edit_resource, name='edit_resource'),

    # 🗑️ Delete resource entry: Team members only (their own)
    path('dashboard/delete/<int:pk>/', views.delete_resource, name='delete_resource'),
]
