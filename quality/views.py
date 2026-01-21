from django.core.paginator import Paginator
from django.db.models import Q
from django.http import FileResponse, Http404
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required

from projects.models import Project
from .models import MaterialTest, WorkApproval
from .forms import MaterialTestForm, WorkApprovalForm


# ---------------- Helpers ----------------
def get_allowed_projects(user):
    """Return queryset of projects the user is allowed to access."""
    if user.is_superuser or user.is_staff:
        return Project.objects.filter(is_active=True)
    return Project.objects.filter(
        is_active=True,
        participants__user=user,
        participants__is_active=True
    ).distinct()


def filter_by_allowed_projects(queryset, user):
    """Filter queryset by allowed projects (for MaterialTest)."""
    if user.is_superuser or user.is_staff:
        return queryset
    return queryset.filter(project__in=get_allowed_projects(user))


def filter_work_by_allowed_projects(queryset, user):
    """Filter WorkApproval queryset by allowed projects via activity."""
    if user.is_superuser or user.is_staff:
        return queryset
    allowed_projects = get_allowed_projects(user)
    return queryset.filter(activity__project__in=allowed_projects)


# ---------------- Material Test ----------------
@login_required
@permission_required('quality.view_materialtest', raise_exception=True)
def material_test_list(request):
    search = request.GET.get('q', '').strip()
    qs = MaterialTest.objects.filter(is_active=True).select_related("project")
    qs = filter_by_allowed_projects(qs, request.user)

    if search:
        qs = qs.filter(
            Q(project__project_name__icontains=search) |
            Q(material_type__icontains=search) |
            Q(consultant__icontains=search) |
            Q(result__icontains=search)
        )

    paginator = Paginator(qs.order_by('-id'), 10)
    materials = paginator.get_page(request.GET.get('page'))

    return render(request, 'quality/material_list.html', {
        'materials': materials,
        'search': search,
    })


@login_required
@permission_required('quality.view_materialtest', raise_exception=True)
def material_test_report_view(request, pk):
    obj = get_object_or_404(MaterialTest, pk=pk, is_active=True)
    if obj.project not in get_allowed_projects(request.user):
        raise Http404("You do not have access to this report.")
    if not obj.report_file:
        raise Http404("No report uploaded")
    return FileResponse(obj.report_file.open("rb"), as_attachment=False)


# ---------------- Material Test ----------------
@login_required
@permission_required('quality.add_materialtest', raise_exception=True)
def material_test_create(request):
    form = MaterialTestForm(request.POST or None, request.FILES or None)
    form.fields['project'].queryset = get_allowed_projects(request.user)

    if form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.is_active = True
        obj.save()
        messages.success(request, f"Material test '{obj.material_type}' for project '{obj.project.project_name}' added successfully.")
        return redirect('quality:material_list')

    if request.method == "POST":
        messages.error(request, "Please correct the errors below.")

    return render(request, 'quality/material_form.html', {
        'form': form,
        'is_edit': False,
    })


@login_required
@permission_required('quality.can_approve_material', raise_exception=True)
def material_test_update(request, pk):
    obj = get_object_or_404(MaterialTest, pk=pk, is_active=True)
    if obj.project not in get_allowed_projects(request.user):
        messages.error(request, "You do not have permission to update this material test.")
        return redirect('quality:material_list')

    form = MaterialTestForm(request.POST or None, request.FILES or None, instance=obj)
    form.fields['project'].queryset = get_allowed_projects(request.user)

    if form.is_valid():
        form.save()
        messages.success(request, f"Material test '{obj.material_type}' for project '{obj.project.project_name}' updated successfully.")
        return redirect('quality:material_list')

    return render(request, 'quality/material_form.html', {
        'form': form,
        'is_edit': True,
    })


@login_required
@permission_required('quality.delete_materialtest', raise_exception=True)
def material_test_delete(request, pk):
    obj = get_object_or_404(MaterialTest, pk=pk, is_active=True)
    if obj.project not in get_allowed_projects(request.user):
        messages.error(request, "You do not have permission to delete this material test.")
        return redirect('quality:material_list')

    if request.method == "POST":
        obj.is_active = False
        obj.save()
        messages.success(request, f"Material test '{obj.material_type}' for project '{obj.project.project_name}' deleted successfully.")
        return redirect("quality:material_list")

    return render(request, "quality/material_delete.html", {"m": obj})



# ---------------- Work Approval ----------------
@login_required
@permission_required('quality.view_workapproval', raise_exception=True)
def work_approval_list(request):
    search = request.GET.get('q', '').strip()
    qs = WorkApproval.objects.filter(is_active=True).select_related('activity', 'approved_by')
    qs = filter_work_by_allowed_projects(qs, request.user)

    if search:
        qs = qs.filter(
            Q(activity__name__icontains=search) |
            Q(approved_by__username__icontains=search)
        )

    paginator = Paginator(qs.order_by('-id'), 10)
    approvals = paginator.get_page(request.GET.get('page'))

    return render(request, 'quality/work_list.html', {
        'approvals': approvals,
        'search': search,
    })


# ---------------- Work Approval ----------------
@login_required
@permission_required('quality.can_approve_work', raise_exception=True)
def work_approval_create(request):
    form = WorkApprovalForm(request.POST or None)
    allowed_projects = get_allowed_projects(request.user)
    form.fields['activity'].queryset = form.fields['activity'].queryset.filter(project__in=allowed_projects)

    if form.is_valid():
        obj = form.save(commit=False)
        obj.approved_by = request.user
        obj.is_active = True
        obj.save()
        messages.success(request, f"Work for activity '{obj.activity.name}' approved successfully.")
        return redirect("quality:work_list")

    return render(request, "quality/work_form.html", {
        "form": form,
        "is_edit": False,
    })


@login_required
@permission_required('quality.can_approve_work', raise_exception=True)
def work_approval_update(request, pk):
    approval = get_object_or_404(WorkApproval, pk=pk, is_active=True)
    if approval.activity.project not in get_allowed_projects(request.user):
        messages.error(request, "You do not have permission to update this work approval.")
        return redirect("quality:work_list")

    form = WorkApprovalForm(request.POST or None, instance=approval)
    allowed_projects = get_allowed_projects(request.user)
    form.fields['activity'].queryset = form.fields['activity'].queryset.filter(project__in=allowed_projects)

    if form.is_valid():
        form.save()
        messages.success(request, f"Work approval for activity '{approval.activity.name}' updated successfully.")
        return redirect("quality:work_list")

    return render(request, "quality/work_form.html", {
        "form": form,
        "is_edit": True,
        "approval": approval,
    })


@login_required
@permission_required('quality.delete_workapproval', raise_exception=True)
def work_approval_delete(request, pk):
    approval = get_object_or_404(WorkApproval, pk=pk, is_active=True)
    if approval.activity.project not in get_allowed_projects(request.user):
        messages.error(request, "You do not have permission to delete this work approval.")
        return redirect("quality:work_list")

    approval.is_active = False
    approval.save()
    messages.success(request, f"Work approval for activity '{approval.activity.name}' revoked successfully.")
    return redirect('quality:work_list')