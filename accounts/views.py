from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from accounts import models
from accounts.utils.dashboard import build_dashboard_context
from projects.models import Project
from sitemanage.models import Activity, SiteVisitor
from .forms import LoginForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("accounts:dashboard")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
@permission_required('accounts.view_dashboard', raise_exception=True)
def dashboard(request):
    """
    Dashboard view with permission check.
    Only users with 'access_dashboard' can view.
    """
    context = build_dashboard_context(request.user)
    return render(request, "accounts/dashboard/dashboard.html", context)



