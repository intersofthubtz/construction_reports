from django.urls import path
from . import views

app_name = 'compliance'

urlpatterns = [
    # path('', views.compliance_list, name='list'),  
          # urls.py
    path("compliance/", views.compliance_list, name="compliance_list"),
    path("compliance/add/", views.compliance_create, name="compliance_add"),
    path("compliance/<int:pk>/edit/", views.compliance_update, name="compliance_edit"),
    path("compliance/<int:pk>/delete/", views.compliance_delete, name="compliance_delete"),
  
]
