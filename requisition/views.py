# A - Import Required Modules
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.db.models import Q, Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse

from .models import Requisition
from .forms import RequisitionForm
from project.models import Project
from resource.models import Resource

# B - Azure Admin Check
def is_azure_admin(user):
    return user.email == 'admin@dzignscapeprofessionals.onmicrosoft.com'

# C - Filtering Function (Project Name + Requisition No)
def filter_requisitions(query=None, user=None, exclude_user=None,
                        project=None, requisition_no=None):

    queryset = Requisition.objects.all()

    # User-based filters
    if user:
        queryset = queryset.filter(created_by=user)
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free-text search (Project Name + Requisition No)
    if query:
        queryset = queryset.filter(
            Q(project_name_requisition__name_of_project__icontains=query) |
            Q(requisition_no__icontains=query)
        )

    # Project Name filter
    if project:
        queryset = queryset.filter(
            project_name_requisition__name_of_project__icontains=project
        )

    # Requisition No filter
    if requisition_no:
        queryset = queryset.filter(
            requisition_no__icontains=requisition_no
        )

    return queryset

# D - Pagination Helper
def get_paginated_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")

    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)

# E - Team Dashboard View
@login_required
def requisition_dashboard(request):

    query = request.GET.get("q", "").strip()
    project = request.GET.get("project", "").strip() or None
    requisition_no = request.GET.get("requisition_no", "").strip() or None

    # Role-based filtering
    if is_azure_admin(request.user):
        requisitions = filter_requisitions(
            query=query,
            exclude_user=request.user,
            project=project,
            requisition_no=requisition_no,
        )
    else:
        requisitions = filter_requisitions(
            query=query,
            user=request.user,
            project=project,
            requisition_no=requisition_no,
        )

    requisitions_page = get_paginated_queryset(request, requisitions)

    # Form
    form = RequisitionForm(request.POST or None, user=request.user)

    # Save logic (team only)
    if not is_azure_admin(request.user) and request.method == "POST" and form.is_valid():
        requisition = form.save(commit=False)
        requisition.created_by = request.user
        requisition.save()
        messages.success(request, "✅ Requisition record created successfully.")
        return redirect(
            f"{reverse('requisition_dashboard')}?q={query}&project={project or ''}&requisition_no={requisition_no or ''}"
        )

    context = {
        "requisitions": requisitions_page,
        "query": query,
        "project": project or "",
        "requisition_no": requisition_no or "",
        "form": form,
        "mode": "list",
        "readonly": is_azure_admin(request.user),
    }
    return render(request, "requisition/requisition_dashboard.html", context)

# F - Admin Dashboard View (read-only)
@user_passes_test(is_azure_admin)
@login_required
def admin_dashboard(request):
    query = request.GET.get("q", "").strip()
    project = request.GET.get("project", "").strip() or None
    requisition_no = request.GET.get("requisition_no", "").strip() or None

    requisitions = filter_requisitions(
        query=query,
        exclude_user=request.user,
        project=project,
        requisition_no=requisition_no,
    )

    requisitions_page = get_paginated_queryset(request, requisitions)

    context = {
        "requisitions": requisitions_page,
        "query": query,
        "project": project or "",
        "requisition_no": requisition_no or "",
        "form": RequisitionForm(user=request.user),
        "mode": "admin",
        "readonly": True,
    }
    return render(request, "requisition/requisition_dashboard.html", context)

# G - Edit View (team only)
@user_passes_test(lambda u: not is_azure_admin(u))
@login_required
def edit_requisition(request, pk):

    requisition = get_object_or_404(Requisition, pk=pk)

    if requisition.created_by != request.user:
        raise PermissionDenied

    query = request.GET.get("q", "").strip()

    form = RequisitionForm(
        request.POST or None,
        instance=requisition,
        user=request.user
    )

    if form.is_valid():
        form.save()
        messages.success(request, "✏️ Requisition record updated successfully.")
        return redirect(f"{reverse('requisition_dashboard')}?q={query}")

    requisitions = filter_requisitions(query=query, user=request.user)
    requisitions_page = get_paginated_queryset(request, requisitions)

    context = {
        "form": form,
        "mode": "edit",
        "requisition": requisition,
        "query": query,
        "requisitions": requisitions_page,
        "readonly": False,
    }
    return render(request, "requisition/requisition_dashboard.html", context)

# H - Delete View (team only)
@user_passes_test(lambda u: not is_azure_admin(u))
@login_required
def delete_requisition(request, pk):

    requisition = get_object_or_404(Requisition, pk=pk)

    if requisition.created_by != request.user:
        raise PermissionDenied

    query = request.GET.get("q", "").strip()

    if request.method == 'POST':
        name = requisition.project_name_requisition
        requisition.delete()
        messages.success(request, f"🗑️ Requisition '{name}' deleted successfully.")
        return redirect(f"{reverse('requisition_dashboard')}?q={query}")

    return render(request, "requisition/confirm_delete.html", {
        "requisition": requisition,
        "query": query
    })

# I - Submit Requisition for Approval (team only)
@user_passes_test(lambda u: not is_azure_admin(u))
@login_required
def submit_requisition_for_approval(request, pk):

    requisition = get_object_or_404(Requisition, pk=pk)

    if requisition.created_by != request.user:
        raise PermissionDenied

    requisition.submitted_for_approval = True
    requisition.save()

    messages.success(request, "📤 Requisition submitted to admin for approval.")
    return redirect(reverse('requisition_dashboard'))
# J - Approve Requisition (admin only)
@user_passes_test(is_azure_admin)
@login_required
def approve_requisition(request, pk):

    requisition = get_object_or_404(Requisition, pk=pk)

    requisition.admin_approved = True
    requisition.save()

    messages.success(request, "✅ Requisition approved successfully.")
    return redirect(reverse('admin_dashboard'))

# K - Auto-Fill API (Used by JavaScript)
def get_requisition_details(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    return JsonResponse({
        "resource_unit": resource.resource_unit or "",
    })
