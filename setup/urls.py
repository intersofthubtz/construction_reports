from django.urls import path
from . import views

app_name = "setup"

urlpatterns = [
    
    # Client URLs
    path("clients/", views.client_list, name="client_list"),
    path("clients/add/", views.client_create, name="client_create"),
    path("clients/<str:pk>/edit/", views.client_edit, name="client_edit"),
    path("clients/<str:pk>/delete/", views.client_delete, name="client_delete"),

    # Contractor Type URLs
    path("contractor-types/", views.contractor_type_list, name="contractor_type_list"),
    path("contractor-types/create/", views.contractor_type_create, name="contractor_type_create"),
    path("contractor-types/<int:pk>/edit/", views.contractor_type_edit, name="contractor_type_edit"),
    path("contractor-types/<int:pk>/delete/", views.contractor_type_delete, name="contractor_type_delete"),
    
    # Contractor URLs
    path("contractors/", views.contractor_list, name="contractor_list"),
    path("contractors/create/", views.contractor_create, name="contractor_create"),
    path("contractors/<str:tin_number>/edit/", views.contractor_edit, name="contractor_edit"),
    path("contractors/<str:tin_number>/delete/", views.contractor_delete, name="contractor_delete"),
    
    # Project Role URLs
    path("project-roles/", views.project_role_list, name="project_role_list"),
    path("project-roles/create/", views.project_role_create, name="project_role_create"),
    path("project-roles/<int:pk>/edit/", views.project_role_edit, name="project_role_edit"),
    path("project-roles/<int:pk>/delete/", views.project_role_delete, name="project_role_delete"),  
    
    #Work Category URLs
    path("work-categories/", views.work_category_list, name="work_category_list"),  
    path("work-categories/create/", views.work_category_create, name="work_category_create"),  
    path("work-categories/<int:pk>/edit/", views.work_category_edit, name="work_category_edit"),  
    path("work-categories/<int:pk>/delete/", views.work_category_delete, name="work_category_delete"),
    
    # Construction Stages
    path("authorities/", views.authority_list, name="authority_list"),
    path("authorities/create/", views.authority_create, name="authority_create"),
    path("authorities/<int:pk>/edit/", views.authority_edit, name="authority_edit"),
    path("authorities/<int:pk>/delete/", views.authority_delete, name="authority_delete"),
]
