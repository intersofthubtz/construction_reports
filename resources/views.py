from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q

from projects.models import Project
from .models import Equipment, Manpower
from .forms import EquipmentForm, ManpowerForm


# ---------------- Helpers ----------------
def get_allowed_projects(user):
    """Return active projects the user can access."""
    if user.is_superuser or user.is_staff:
        return Project.objects.filter(is_active=True)
    return Project.objects.filter(
        is_active=True,
        participants__user=user,
        participants__is_active=True
    ).distinct()


def filter_by_allowed_projects(queryset, user):
    """Filter a queryset by allowed projects for non-admin users."""
    if user.is_superuser or user.is_staff:
        return queryset
    return queryset.filter(project__in=get_allowed_projects(user))


# ---------------- Equipment ----------------
@login_required
@permission_required("resources.view_equipment", raise_exception=True)
def equipment_list(request):
    search = request.GET.get("q", "").strip()
    page_number = request.GET.get("page")

    equipment = Equipment.objects.select_related("project").filter(is_active=True)
    equipment = filter_by_allowed_projects(equipment, request.user).order_by("name")

    if search:
        equipment = equipment.filter(
            Q(name__icontains=search) |
            Q(project__project_name__icontains=search) |
            Q(category__icontains=search)
        )

    paginator = Paginator(equipment, 10)
    page_obj = paginator.get_page(page_number)

    return render(request, "resources/equipment_list.html", {
        "equipment": page_obj,
        "search": search,
    })


@login_required
@permission_required("resources.view_equipment", raise_exception=True)
def equipment_detail(request, pk):
    equipment = get_object_or_404(
        filter_by_allowed_projects(Equipment.objects.select_related("project").filter(is_active=True), request.user),
        pk=pk
    )
    return render(request, "resources/equipment_detail.html", {"equipment": equipment})


@login_required
@permission_required("resources.add_equipment", raise_exception=True)
def equipment_create(request):
    allowed_projects = get_allowed_projects(request.user)
    if request.method == "POST":
        form = EquipmentForm(request.POST)
        form.fields['project'].queryset = allowed_projects
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.is_active = True
            obj.save()
            return redirect("resources:equipment_list")
    else:
        form = EquipmentForm()
        form.fields['project'].queryset = allowed_projects

    return render(request, "resources/equipment_form.html", {
        "form": form,
        "page_title": "Add Equipment"
    })


@login_required
@permission_required("resources.change_equipment", raise_exception=True)
def equipment_edit(request, pk):
    equipment = get_object_or_404(
        filter_by_allowed_projects(Equipment.objects.select_related("project").filter(is_active=True), request.user),
        pk=pk
    )
    allowed_projects = get_allowed_projects(request.user)

    if request.method == "POST":
        form = EquipmentForm(request.POST, instance=equipment)
        form.fields['project'].queryset = allowed_projects
        if form.is_valid():
            form.save()
            return redirect("resources:equipment_detail", pk=pk)
    else:
        form = EquipmentForm(instance=equipment)
        form.fields['project'].queryset = allowed_projects

    return render(request, "resources/equipment_form.html", {
        "form": form,
        "page_title": "Edit Equipment"
    })


@login_required
@permission_required("resources.delete_equipment", raise_exception=True)
def equipment_delete(request, pk):
    equipment = get_object_or_404(
        filter_by_allowed_projects(Equipment.objects.filter(is_active=True), request.user),
        pk=pk
    )
    if request.method == "POST":
        equipment.is_active = False
        equipment.save()
        return redirect("resources:equipment_list")
    return render(request, "resources/equipment_confirm_delete.html", {
        "object": equipment,
        "cancel_url": "resources:equipment_list"
    })


# ---------------- Manpower ----------------
@login_required
@permission_required("resources.view_manpower", raise_exception=True)
def manpower_list(request):
    search = request.GET.get("q", "").strip()
    page_number = request.GET.get("page")

    manpower = Manpower.objects.select_related("project").filter(is_active=True)
    manpower = filter_by_allowed_projects(manpower, request.user).order_by("role")

    if search:
        manpower = manpower.filter(
            Q(role__icontains=search) |
            Q(project__project_name__icontains=search)
        )

    paginator = Paginator(manpower, 10)
    page_obj = paginator.get_page(page_number)

    return render(request, "resources/manpower_list.html", {
        "manpower": page_obj,
        "search": search,
    })


@login_required
@permission_required("resources.view_manpower", raise_exception=True)
def manpower_detail(request, pk):
    manpower = get_object_or_404(
        filter_by_allowed_projects(Manpower.objects.select_related("project").filter(is_active=True), request.user),
        pk=pk
    )
    return render(request, "resources/manpower_detail.html", {"manpower": manpower})


@login_required
@permission_required("resources.add_manpower", raise_exception=True)
def manpower_create(request):
    allowed_projects = get_allowed_projects(request.user)
    if request.method == "POST":
        form = ManpowerForm(request.POST)
        form.fields['project'].queryset = allowed_projects
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.is_active = True
            obj.save()
            return redirect("resources:manpower_list")
    else:
        form = ManpowerForm()
        form.fields['project'].queryset = allowed_projects

    return render(request, "resources/manpower_form.html", {
        "form": form,
        "page_title": "Add Manpower"
    })


@login_required
@permission_required("resources.change_manpower", raise_exception=True)
def manpower_update(request, pk):
    manpower = get_object_or_404(
        filter_by_allowed_projects(Manpower.objects.select_related("project").filter(is_active=True), request.user),
        pk=pk
    )
    allowed_projects = get_allowed_projects(request.user)

    if request.method == "POST":
        form = ManpowerForm(request.POST, instance=manpower)
        form.fields['project'].queryset = allowed_projects
        if form.is_valid():
            form.save()
            return redirect("resources:manpower_list")
    else:
        form = ManpowerForm(instance=manpower)
        form.fields['project'].queryset = allowed_projects

    return render(request, "resources/manpower_form.html", {
        "form": form,
        "page_title": "Edit Manpower"
    })


@login_required
@permission_required("resources.delete_manpower", raise_exception=True)
def manpower_delete(request, pk):
    manpower = get_object_or_404(
        filter_by_allowed_projects(Manpower.objects.filter(is_active=True), request.user),
        pk=pk
    )
    if request.method == "POST":
        manpower.is_active = False
        manpower.save()
        return redirect("resources:manpower_list")
    return render(request, "resources/manpower_confirm_delete.html", {
        "object": manpower,
        "cancel_url": "resources:manpower_list"
    })
