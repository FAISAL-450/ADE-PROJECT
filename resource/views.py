# A - Import Required Modules
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse
from django.db.models import Q, Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from .models import Resource
from .forms import ResourceForm

# B - Azure Admin Check
def is_azure_admin(user):
    return user.email == 'admin@dzignscapeprofessionals.onmicrosoft.com'

# C - Filtering Function (Resource Name + Resource Group)
def filter_resources(query=None, user=None, exclude_user=None,
                     name_of_resource=None, resource_group=None):

    queryset = Resource.objects.all()

    # User-based filters
    if user:
        queryset = queryset.filter(created_by=user)
    if exclude_user:
        queryset = queryset.exclude(created_by=exclude_user)

    # Free-text search (Resource Name + Resource Group)
    if query:
        queryset = queryset.filter(
            Q(name_of_resource__icontains=query) |
            Q(resource_group__icontains=query)
        )

    # Resource Name filter
    if name_of_resource:
        queryset = queryset.filter(name_of_resource__icontains=name_of_resource)

    # Resource Group filter
    if resource_group:
        queryset = queryset.filter(resource_group__icontains=resource_group)

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
def resource_dashboard(request):

    query = request.GET.get("q", "").strip()
    name_of_resource = request.GET.get("name_of_resource", "").strip() or None
    resource_group = request.GET.get("resource_group", "").strip() or None

    # Role-based filtering
    if is_azure_admin(request.user):
        resources = filter_resources(
            query=query,
            exclude_user=request.user,
            name_of_resource=name_of_resource,
            resource_group=resource_group,
        )
    else:
        resources = filter_resources(
            query=query,
            user=request.user,
            name_of_resource=name_of_resource,
            resource_group=resource_group,
        )

    resources_page = get_paginated_queryset(request, resources)

    # Form
    form = ResourceForm(request.POST or None)

    # Save logic (team only)
    if not is_azure_admin(request.user) and request.method == "POST" and form.is_valid():
        resource = form.save(commit=False)
        resource.created_by = request.user
        resource.save()
        messages.success(request, "✅ Resource record created successfully.")
        return redirect(f"{reverse('resource_dashboard')}?q={query}")

    context = {
        "resources": resources_page,
        "query": query,
        "name_of_resource": name_of_resource or "",
        "resource_group": resource_group or "",
        "form": form,
        "mode": "list",
        "readonly": is_azure_admin(request.user),
    }
    return render(request, "resource/resource_dashboard.html", context)

# F - Admin Dashboard View (read-only)
@user_passes_test(is_azure_admin)
@login_required
def admin_dashboard(request):

    query = request.GET.get("q", "").strip()
    name_of_resource = request.GET.get("name_of_resource", "").strip() or None
    resource_group = request.GET.get("resource_group", "").strip() or None

    resources = filter_resources(
        query=query,
        exclude_user=request.user,
        name_of_resource=name_of_resource,
        resource_group=resource_group,
    )

    resources_page = get_paginated_queryset(request, resources)

    context = {
        "resources": resources_page,
        "query": query,
        "name_of_resource": name_of_resource or "",
        "resource_group": resource_group or "",
        "form": ResourceForm(),
        "mode": "admin",
        "readonly": True,
    }
    return render(request, "resource/resource_dashboard.html", context)

# G - Edit View (team only)
@user_passes_test(lambda u: not is_azure_admin(u))
@login_required
def edit_resource(request, pk):

    resource = get_object_or_404(Resource, pk=pk)

    if resource.created_by != request.user:
        raise PermissionDenied

    query = request.GET.get("q", "").strip()

    form = ResourceForm(
        request.POST or None,
        instance=resource
    )

    if form.is_valid():
        form.save()
        messages.success(request, "✏️ Resource record updated successfully.")
        return redirect(f"{reverse('resource_dashboard')}?q={query}")

    resources = filter_resources(query=query, user=request.user)
    resources_page = get_paginated_queryset(request, resources)

    context = {
        "form": form,
        "mode": "edit",
        "resource": resource,
        "query": query,
        "resources": resources_page,
        "readonly": False,
    }
    return render(request, "resource/resource_dashboard.html", context)

# H - Delete View (team only)
@user_passes_test(lambda u: not is_azure_admin(u))
@login_required
def delete_resource(request, pk):

    resource = get_object_or_404(Resource, pk=pk)

    if resource.created_by != request.user:
        raise PermissionDenied

    query = request.GET.get("q", "").strip()

    if request.method == 'POST':
        name = resource.name_of_resource
        resource.delete()
        messages.success(request, f"🗑️ Resource '{name}' deleted successfully.")
        return redirect(f"{reverse('resource_dashboard')}?q={query}")

    return render(request, "resource/confirm_delete.html", {
        "resource": resource,
        "query": query
    })

