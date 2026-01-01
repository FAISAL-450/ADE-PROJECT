from django.urls import path
from . import views
app_name = 'construction'  
urlpatterns = [
    path('requisition-detailed/', views.construction_pr_list, name='construction_pr_list'),
   
]
