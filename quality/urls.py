from django.urls import path
from . import views


app_name = "quality"

urlpatterns = [
    # Material Tests
    path("material/", views.material_test_list, name="material_list"),
    path("material/add/", views.material_test_create, name="material_add"),
    path("material/<int:pk>/edit/", views.material_test_update, name="material_edit"),
    path("material/<int:pk>/delete/", views.material_test_delete, name="material_delete"),
    path("material/<int:pk>/report/", views.material_test_report_view, name="material_report"),

    # Work Approvals
    path("work/", views.work_approval_list, name="work_list"),
    path("work/add/", views.work_approval_create, name="work_add"),
    path("work/<int:pk>/edit/", views.work_approval_update, name="work_edit"),
    path("work/<int:pk>/delete/", views.work_approval_delete, name="work_delete"),
]