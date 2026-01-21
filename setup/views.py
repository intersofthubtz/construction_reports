from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required
from .models import ContractorType, Authority, Contractor, Client, ProjectRole, WorkCategory
from .forms import ClientForm, AuthorityForm, ContractorTypeForm, ContractorForm, ProjectRoleForm, WorkCategoryForm

# -----------------------------
# Client CRUD
# -----------------------------
@login_required
@permission_required('setup.view_client', raise_exception=True)
def client_list(request):
    search = request.GET.get("q", "").strip()
    page_number = request.GET.get("page")

    clients = Client.objects.filter(is_active=True).order_by("name")

    if search:
        clients = clients.filter(
            Q(name__icontains=search) |
            Q(tin_number__icontains=search) |
            Q(city__icontains=search) |
            Q(postal_address__icontains=search)
        )

    paginator = Paginator(clients, 10)  
    page_obj = paginator.get_page(page_number)

    return render(request, "setup/client_list.html", {
        "clients": page_obj,
        "search": search,
    })

@login_required
@permission_required('setup.add_client', raise_exception=True)
def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Client created successfully!")
            return redirect("setup:client_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ClientForm()
    return render(request, "setup/client_form.html", {"form": form})

@login_required
@permission_required('setup.change_client', raise_exception=True)
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Client updated successfully!")
            return redirect("setup:client_list")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ClientForm(instance=client)
    return render(request, "setup/client_form.html", {"form": form, "client": client})


@login_required
@permission_required('setup.delete_client', raise_exception=True)
def client_delete(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == "POST":
        client.is_active = False
        client.save()
        return redirect("setup:client_list")

    return render(request, "setup/client_confirm_delete.html", {"client": client})


# -----------------------------
# Contractor Type Views
# -----------------------------
@login_required
@permission_required('setup.view_contractortype', raise_exception=True)
def contractor_type_list(request):
    search = request.GET.get("q", "").strip()
    page_number = request.GET.get("page")

    types = ContractorType.objects.filter(is_active=True).order_by("name")

    if search:
        types = types.filter(Q(name__icontains=search) | Q(description__icontains=search))

    paginator = Paginator(types, 10)
    page_obj = paginator.get_page(page_number)

    return render(request, "setup/contractor_type_list.html", {
        "types": page_obj,
        "search": search,
    })


@login_required
@permission_required('setup.add_contractortype', raise_exception=True)
def contractor_type_create(request):
    if request.method == "POST":
        form = ContractorTypeForm(request.POST)
        if form.is_valid():
            type_obj = form.save(commit=False)
            type_obj.is_active = True
            type_obj.save()
            messages.success(request, f'Contractor Type "{type_obj.name}" created successfully.')
            return redirect("setup:contractor_type_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContractorTypeForm()

    return render(request, "setup/contractor_type_form.html", {"form": form})


@login_required
@permission_required('setup.change_contractortype', raise_exception=True)
def contractor_type_edit(request, pk):
    contractor_type = get_object_or_404(ContractorType, pk=pk)

    if request.method == "POST":
        form = ContractorTypeForm(request.POST, instance=contractor_type)
        if form.is_valid():
            form.save()
            messages.success(request, f'Contractor Type "{contractor_type.name}" updated successfully.')
            return redirect("setup:contractor_type_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContractorTypeForm(instance=contractor_type)

    return render(request, "setup/contractor_type_form.html", {"form": form, "contractor_type": contractor_type})


@login_required
@permission_required('setup.delete_contractortype', raise_exception=True)
def contractor_type_delete(request, pk):
    contractor_type = get_object_or_404(ContractorType, pk=pk)
    if request.method == "POST":
        contractor_type.is_active = False
        contractor_type.save()
        messages.success(request, f'Contractor Type "{contractor_type.name}" deleted successfully.')
        return redirect("setup:contractor_type_list")
    return render(request, "setup/contractor_type_confirm_delete.html", {"contractor_type": contractor_type})



# -----------------------------
# Contractor Views
# -----------------------------
@login_required
@permission_required('setup.view_contractor', raise_exception=True)
def contractor_list(request):
    search = request.GET.get("q", "").strip()
    page_number = request.GET.get("page")

    contractors = Contractor.objects.filter(is_active=True).select_related("contractor_type").order_by("-tin_number")

    if search:
        contractors = contractors.filter(
            Q(name__icontains=search) |
            Q(tin_number__icontains=search) |
            Q(city__icontains=search) |
            Q(contractor_type__name__icontains=search)
        )

    paginator = Paginator(contractors, 10)
    page_obj = paginator.get_page(page_number)

    return render(request, "setup/contractor_list.html", {
        "contractors": page_obj,
        "search": search,
    })


@login_required
@permission_required('setup.add_contractor', raise_exception=True)
def contractor_create(request):
    if request.method == "POST":
        form = ContractorForm(request.POST)
        if form.is_valid():
            contractor = form.save(commit=False)
            contractor.is_active = True
            contractor.save()
            messages.success(request, f'Contractor "{contractor.name}" created successfully.')
            return redirect("setup:contractor_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ContractorForm()

    return render(request, "setup/contractor_form.html", {"form": form})

@login_required
@permission_required('setup.change_contractor', raise_exception=True)
def contractor_edit(request, tin_number):
    contractor = get_object_or_404(Contractor, tin_number=tin_number)

    if request.method == "POST":
        form = ContractorForm(request.POST, instance=contractor)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Contractor "{contractor.name}" updated successfully.'
            )
            return redirect("setup:contractor_list")
    else:
        form = ContractorForm(instance=contractor)

    return render(
        request,
        "setup/contractor_form.html",
        {"form": form, "contractor": contractor}
    )

@login_required
@permission_required('setup.delete_contractor', raise_exception=True)
def contractor_delete(request, tin_number):
    contractor = get_object_or_404(Contractor, tin_number=tin_number)

    if request.method == "POST":
        contractor.is_active = False
        contractor.save()
        messages.success(
            request,
            f'Contractor "{contractor.name}" deleted successfully.'
        )
        return redirect("setup:contractor_list")

    return render(
        request,
        "setup/contractor_confirm_delete.html",
        {"contractor": contractor}
    )


# -----------------------------
# Project Role Views 
# -----------------------------
@login_required
@permission_required("setup.view_projectrole", raise_exception=True)
def project_role_list(request):
    search = request.GET.get("q", "").strip()
    page_number = request.GET.get("page")

    roles = ProjectRole.objects.filter(is_active=True).order_by("name")

    if search:
        roles = roles.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    paginator = Paginator(roles, 10)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "setup/project_role_list.html",
        {
            "projectroles": page_obj,
            "search": search,
        }
    )


@login_required
@permission_required("setup.add_projectrole", raise_exception=True)
def project_role_create(request):
    form = ProjectRoleForm(request.POST or None)

    if form.is_valid():
        role = form.save(commit=False)
        role.updated_by = request.user
        role.save()
        messages.success(request, "Project role created successfully.")
        return redirect("setup:project_role_list")

    return render(
        request,
        "setup/project_role_form.html",
        {"form": form}
    )


@login_required
@permission_required("setup.change_projectrole", raise_exception=True)
def project_role_edit(request, pk):
    role = get_object_or_404(ProjectRole, pk=pk, is_active=True)

    form = ProjectRoleForm(request.POST or None, instance=role)

    if form.is_valid():
        role = form.save(commit=False)
        role.updated_by = request.user
        role.save()
        messages.success(request, "Project role updated successfully.")
        return redirect("setup:project_role_list")

    return render(
        request,
        "setup/project_role_form.html",
        {"form": form}
    )


@login_required
@permission_required("setup.delete_projectrole", raise_exception=True)
def project_role_delete(request, pk):
    role = get_object_or_404(ProjectRole, pk=pk, is_active=True)

    if request.method == "POST":
        role.is_active = False
        role.updated_by = request.user
        role.save()
        messages.success(request, "Project role deleted successfully.")
        return redirect("setup:project_role_list")

    return render(
        request,
        "setup/project_role_confirm_delete.html",
        {"role": role}
    )


# -----------------------------
# List Work Categories
# -----------------------------
@login_required
@permission_required("setup.view_workcategory", raise_exception=True)
def work_category_list(request):
    search = request.GET.get("q", "").strip()
    page_number = request.GET.get("page")

    categories = WorkCategory.objects.filter(is_active=True).order_by("-id")

    if search:
        categories = categories.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    paginator = Paginator(categories, 10)  
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "setup/work_category_list.html",
        {
            "categories": page_obj,
            "search": search,
        },
    )
# -----------------------------
# Create Work Category
# -----------------------------
@login_required
@permission_required("setup.add_workcategory", raise_exception=True)
def work_category_create(request):
    if request.method == "POST":
        form = WorkCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.is_active = True
            category.save()
            messages.success(request, f'Work Category "{category.name}" created successfully.')
            return redirect("setup:work_category_list")
    
    else:
        form = WorkCategoryForm()

    return render(request, "setup/work_category_form.html", {"form": form})


# -----------------------------
# Edit Work Category
# -----------------------------
@login_required
@permission_required("setup.change_workcategory", raise_exception=True)
def work_category_edit(request, pk):
    category = get_object_or_404(WorkCategory, pk=pk, is_active=True)

    if request.method == "POST":
        form = WorkCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Work Category "{category.name}" updated successfully.')
            return redirect("setup:work_category_list")
  
    else:
        form = WorkCategoryForm(instance=category)

    return render(request, "setup/work_category_form.html", {"form": form, "category": category})


# -----------------------------
# Delete Work Category
# -----------------------------
@login_required
@permission_required("setup.delete_workcategory", raise_exception=True)
def work_category_delete(request, pk):
    category = get_object_or_404(WorkCategory, pk=pk, is_active=True)

    if request.method == "POST":
        category.is_active = False
        category.save()
        messages.success(request, f'Work Category "{category.name}" deleted successfully.')
        return redirect("setup:work_category_list")

    return render(request, "setup/work_category_confirm_delete.html", {"category": category})


# -----------------------------
# List Authorities
# -----------------------------
@login_required
@permission_required("setup.view_authority", raise_exception=True)
def authority_list(request):
    search = request.GET.get("q", "").strip()
    page_number = request.GET.get("page")

    authorities = Authority.objects.filter(is_active=True)

    if search:
        authorities = authorities.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )

    paginator = Paginator(authorities.order_by("-id"), 10)
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "setup/authority_list.html",
        {
            "authorities": page_obj,
            "search": search,
        }
    )


# -----------------------------
# Create Authority
# -----------------------------
@login_required
@permission_required("setup.add_authority", raise_exception=True)
def authority_create(request):
    if request.method == "POST":
        form = AuthorityForm(request.POST)
        if form.is_valid():
            authority = form.save(commit=False)
            authority.created_by = request.user
            authority.is_active = True
            authority.save()
            messages.success(request, f'Authority "{authority.name}" created successfully.')
            return redirect("setup:authority_list")

    else:
        form = AuthorityForm()

    return render(
        request,
        "setup/authority_form.html",
        {"form": form}
    )


# -----------------------------
# Edit Authority
# -----------------------------
@login_required
@permission_required("setup.change_authority", raise_exception=True)
def authority_edit(request, pk):
    authority = get_object_or_404(Authority, pk=pk, is_active=True)

    if request.method == "POST":
        form = AuthorityForm(request.POST, instance=authority)
        if form.is_valid():
            form.save()
            messages.success(request, f'Authority "{authority.name}" updated successfully.')
            return redirect("setup:authority_list")

    else:
        form = AuthorityForm(instance=authority)

    return render(
        request,
        "setup/authority_form.html",
        {"form": form, "authority": authority}
    )


# -----------------------------
# Delete Authority
# -----------------------------
@login_required
@permission_required("setup.delete_authority", raise_exception=True)
def authority_delete(request, pk):
    authority = get_object_or_404(Authority, pk=pk, is_active=True)

    if request.method == "POST":
        authority.is_active = False
        authority.save()
        messages.success(request, f'Authority "{authority.name}" deleted successfully.')
        return redirect("setup:authority_list")

    return render(
        request,
        "setup/authority_delete.html",
        {"authority": authority}
    )

