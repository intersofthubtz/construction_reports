from django.urls import path
from . import views

app_name = "resources"

urlpatterns = [

    # Equipment
    path("equipment/", views.equipment_list, name="equipment_list"),
    path("equipment/add/", views.equipment_create, name="equipment_create"),
    path("equipment/<int:pk>/", views.equipment_detail, name="equipment_detail"),
    path("equipment/<int:pk>/edit/", views.equipment_edit, name="equipment_edit"),
    path("equipment/<int:pk>/delete/", views.equipment_delete, name="equipment_delete"),

    # Manpower
    path("manpower/", views.manpower_list, name="manpower_list"),
    path("manpower/add/", views.manpower_create, name="manpower_create"),
    path("manpower/<int:pk>/", views.manpower_detail, name="manpower_detail"),
    path("manpower/<int:pk>/edit/", views.manpower_update, name="manpower_update"),
    path("manpower/<int:pk>/delete/", views.manpower_delete, name="manpower_delete"),
]
