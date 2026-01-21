from django.urls import path
from . import views

app_name = 'sitemanage'

urlpatterns = [
    path("", views.site_overview, name="site_overview"),

    # Activities
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/<int:pk>/', views.activity_detail, name='activity_detail'),
    path('activities/create/', views.activity_create, name='activity_create'),
    path('activities/<int:pk>/update/', views.activity_update, name='activity_update'),
    path('activities/<int:pk>/delete/', views.activity_delete, name='activity_delete'),
    
    
    # ---------------- ProgressLog URLs ----------------
    path('progress/<int:activity_id>/', views.progress_log_list, name='progress_log_list'),
    path('progress/add/<int:activity_id>/', views.progress_log_create, name='progress_log_create'),
    path('progress/<int:pk>/edit/', views.progress_log_update, name='progress_log_update'),
    path('progress/<int:pk>/delete/', views.progress_log_delete, name='progress_log_delete'),


    path("site-visitors/", views.site_visitor_list, name="site_visitor_list"),
    path("site-visitors/add/", views.site_visitor_create, name="site_visitor_add"),
    path("site-visitors/<int:pk>/edit/", views.site_visitor_edit, name="site_visitor_edit"),
    path("site-visitors/<int:pk>/delete/", views.site_visitor_delete, name="site_visitor_delete"),
    
    path("project-images/", views.site_project_image_list, name="site_project_image_list"),
    path("project-images/add/", views.site_project_image_create, name="site_project_image_create"),
    path("project-images/<int:pk>/edit/", views.site_project_image_edit, name="site_project_image_edit"),
    path("project-images/<int:pk>/delete/", views.site_project_image_delete, name="site_project_image_delete"),
    path('project-images/<int:pk>/', views.site_project_image_detail, name='site_project_image_detail'),


    # AJAX
    path("ajax/load-activities/", views.ajax_load_activities, name="ajax_load_activities"),
]
