from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("payments/", views.payment_list, name="payment_list"),
    path("payments/<int:pk>/", views.payment_view, name="payment_view"),
    path("payments/add/", views.payment_create, name="payment_add"),
    path("payments/<int:pk>/edit/", views.payment_update, name="payment_edit"),
    path("payments/<int:pk>/delete/", views.payment_delete, name="payment_delete"),
    

    path("transactions/", views.transaction_list, name="transaction_list"),
    path("transactions/<int:pk>/", views.transaction_view, name="transaction_view"),
    path("transactions/add/", views.transaction_create, name="transaction_add"),
    path("transactions/<int:pk>/edit/", views.transaction_update, name="transaction_edit"),
    path("transactions/<int:pk>/delete/", views.transaction_delete, name="transaction_delete"),
]
