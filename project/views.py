# A - Import Required Modules
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from .models import Project
from .forms import ProjectForm

# B - Azure Admin Check
def is_azure_admin(user):
    return user.email == 'admin@dzignscapeprofessionals.onmicrosoft.com'

# C - Filtering Function
def filter_projects(query=None, user=None, exclude_user=None):
    queryset = Project.objects.all()

    if user:
        queryset = queryset.filter(created_by=user)

    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    if query:
        queryset = queryset.filter(
            Q(name_of_project__icontains=query) |
            Q(project_address__icontains=query) |
            Q(contact_person_name__icontains=query)
        )

    return queryset

# D - Reusable Pagination Function
def get_paginated_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")

    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)

# E - Team Dashboard View (List View + Form Submission)
@login_required
def project_dashboard(request):
    query = request.GET.get("q", "").strip()
    form = ProjectForm(request.POST or None)

    # Role-based data filtering
    if is_azure_admin(request.user):
        projects = filter_projects(query=query, exclude_user=request.user)
    else:
        projects = filter_projects(query=query, user=request.user)

    projects_page = get_paginated_queryset(request, projects)

    # Save logic: Team member can submit
    if not is_azure_admin(request.user) and request.method == "POST" and form.is_valid():
        project = form.save(commit=False)
        project.created_by = request.user
        project.team = getattr(
            getattr(request.user, "project_profile", None),
            "role",
            "manager"
        )
        project.save()
        messages.success(request, "✅ Project detailed record created successfully.")
        return redirect(f"{reverse('project_dashboard')}?q={query}")

    context = {
        "projects": projects_page,
        "query": query,
        "form": form,
        "mode": "list",
        "readonly": is_azure_admin(request.user)
    }
    return render(request, "project/project_dashboard.html", context)

# F - Admin Dashboard View (Azure Admin only, read-only)
@user_passes_test(is_azure_admin)
@login_required
def admin_dashboard(request):
    query = request.GET.get("q", "").strip()
    projects = filter_projects(query=query, exclude_user=request.user)
    projects_page = get_paginated_queryset(request, projects)

    context = {
        "projects": projects_page,
        "query": query,
        "form": ProjectForm(),
        "mode": "admin",
        "readonly": True
    }
    return render(request, "project/project_dashboard.html", context)

# G - Edit View (Team member can edit)
@user_passes_test(lambda u: not is_azure_admin(u))
@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.created_by != request.user:
        raise PermissionDenied

    query = request.GET.get("q", "").strip()
    form = ProjectForm(request.POST or None, instance=project)

    if form.is_valid():
        form.save()
        messages.success(request, "✏️ Project detailed record updated successfully.")
        return redirect(f"{reverse('project_dashboard')}?q={query}")

    projects = filter_projects(query=query, user=request.user)
    projects_page = get_paginated_queryset(request, projects)

    context = {
        "form": form,
        "mode": "edit",
        "project": project,
        "query": query,
        "projects": projects_page,
        "readonly": False
    }
    return render(request, "project/project_dashboard.html", context)

# H - Delete View (Team member can delete)
@user_passes_test(lambda u: not is_azure_admin(u))
@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if project.created_by != request.user:
        raise PermissionDenied

    query = request.GET.get("q", "").strip()

    if request.method == 'POST':
        name = project.name_of_project
        project.delete()
        messages.success(request, f"🗑️ Project '{name}' deleted successfully.")
        return redirect(f"{reverse('project_dashboard')}?q={query}")

    return render(request, "project/confirm_delete.html", {
        "project": project,
        "query": query
    })
