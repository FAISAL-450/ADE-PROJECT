from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from requisition.models import Requisition

# 🔁 Reusable Pagination Function
def get_paginated_queryset(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)

# 🏗️ Construction-Requisition List-View
def construction_pr_list(request):
    query = request.GET.get('q', '').strip()
    requisitions = Requisition.objects.filter(department='construction')

    if query:
        requisitions = requisitions.filter(project_name_requisition__icontains=query)

    requisitions_page = get_paginated_queryset(request, requisitions, per_page=10)

    return render(request, 'construction/construction_pr_list.html', {
        'requisitions': requisitions_page,
        'query': query
    })

