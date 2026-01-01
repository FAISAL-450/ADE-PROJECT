from django.urls import path
from . import views

urlpatterns = [
    # 🔹 Team dashboard: team members manage their own Requisition records
    path('dashboard/', views.requisition_dashboard, name='requisition_dashboard'),

    # 🔹 Admin dashboard: Azure admin views all Requisition records
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),

    # ✏️ Edit Requisition entry (Team member can edit)
    path('dashboard/edit/<int:pk>/', views.edit_requisition, name='edit_requisition'),

    # 🗑️ Delete Requisition entry (Team member can delete)
    path('dashboard/delete/<int:pk>/', views.delete_requisition, name='delete_requisition'),

    # 📤 Submit Requisition for approval (team)
    path('dashboard/submit/<int:pk>/', views.submit_requisition_for_approval, name='submit_requisition_for_approval'),

    # ✅ Approve Requisition (admin)
    path('dashboard/approve/<int:pk>/', views.approve_requisition, name='approve_requisition'),

    # 🔎 Auto-fill API endpoint (used by JavaScript)
    path('dashboard/get_requisition_details/<int:pk>/', views.get_requisition_details, name='get_requisition_details'),
]
