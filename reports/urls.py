from django.urls import path
from . import views

app_name = "reports"

urlpatterns = [


    # DASHBOARD
    path("progress-cover/", views.progress_cover_list, name="progress_cover_list"),
    path("progress-cover/create/", views.progress_cover_create, name="progress_cover_create"),
    path("progress-cover/<int:pk>/edit/", views.progress_cover_edit, name="progress_cover_edit"),
    path("progress-cover/<int:pk>/delete/", views.progress_cover_delete, name="progress_cover_delete"),
    path("progress-cover/<int:pk>/pdf/", views.progress_cover_pdf, name="progress_cover_pdf"),

    # Project Report
    path("project/", views.project_report, name="project_report"),
    path("project/download/xcel/", views.project_report_download_excel, name="project_report_download_excel"),
    path("project/download/pdf/", views.project_report_download_pdf, name="project_report_download_pdf"),
    path("project/download/word/", views.project_report_download_word, name="project_report_download_word"),
    
    
    # PROGRESS REPORT
    path("progress/", views.progress_report, name="progress_report"),
    path("progress/download/excel/", views.progress_report_download_excel, name="progress_report_download_excel"),
    path("progress/download/pdf/", views.progress_report_download_pdf, name="progress_report_download_pdf"),
    path("progress/download/word/", views.progress_report_download_word, name="progress_report_download_word"),

    
    # RESOURCES REPORT
    path("resources/", views.resources_report, name="resources_report"),
    path("resources/download/excel/", views.resources_report_download_excel, name="resources_report_download_excel"),
    path("resources/download/pdf/", views.resources_report_download_pdf, name="resources_report_download_pdf"),
    path("resources/download/word/", views.resources_report_download_word, name="resources_report_download_word"),     
    
    # FINANCE REPORTS
    path("finance/", views.finance_report, name="finance_report"),
    path("finance/download/excel/", views.finance_report_download_excel, name="finance_report_download_excel"),
    path("finance/download/pdf/", views.finance_report_download_pdf, name="finance_report_download_pdf"),
    path("finance/download/word/", views.finance_report_download_word, name="finance_report_download_word"),
    
    # QUALITY REPORTS
    path("quality/", views.quality_report, name="quality_report"),
    path("quality/download/excel/", views.quality_report_download_excel, name="quality_report_download_excel"),
    path("quality/download/pdf/", views.quality_report_download_pdf, name="quality_report_download_pdf"),
    path("quality/download/word/", views.quality_report_download_word, name="quality_report_download_word"),



]
