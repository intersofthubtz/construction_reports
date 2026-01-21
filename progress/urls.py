from django.urls import path

from projects.views import project_list
from .views import progress_list

app_name = "progress"

urlpatterns = [
    path("", progress_list, name="progress_list"),
]
