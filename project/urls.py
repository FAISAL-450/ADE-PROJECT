from django.urls import path
from . import views

urlpatterns = [
    # 🔹 Team dashboard: team members manage their own team's projects
    path('dashboard/', views.project_dashboard, name='project_dashboard'),

    # 🔹 Admin dashboard: Azure admin views all project records
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # ✏️ Edit project entry (Team member can edit)
    path('dashboard/edit/<int:pk>/', views.edit_project, name='edit_project'),

    # 🗑️ Delete project entry (Team member can delete)
    path('dashboard/delete/<int:pk>/', views.delete_project, name='delete_project'),
]
