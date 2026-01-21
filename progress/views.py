from django.shortcuts import render
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def progress_list(request):
    # Logic to retrieve and display progress data
    return render(request, 'progress/progress_list.html')