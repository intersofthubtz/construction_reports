from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Compliance
from .forms import ComplianceForm

# LIST
@login_required
@permission_required('compliance.view_compliance', raise_exception=True)
def compliance_list(request):
    search = request.GET.get('q', '').strip()

    queryset = Compliance.objects.filter(is_active=True)\
        .select_related("project", "authority")

    if search:
        queryset = queryset.filter(
            Q(project__project_name__icontains=search) |
            Q(authority__name__icontains=search) |
            Q(registration_no__icontains=search) |
            Q(status__icontains=search)
        )

    paginator = Paginator(queryset.order_by('expiry_date'), 10)
    compliances = paginator.get_page(request.GET.get('page'))

    return render(request, 'compliance/compliance_list.html', {
        'compliances': compliances,
        'search': search,
    })


# CREATE
@login_required
@permission_required('compliance.add_compliance', raise_exception=True)
def compliance_create(request):
    form = ComplianceForm(request.POST or None)

    if form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.save()
        messages.success(request, "Compliance record added successfully.")
        return redirect('compliance:compliance_list')

    if request.method == "POST":
        messages.error(request, "Failed to add compliance record.")

    return render(request, 'compliance/compliance_form.html', {
        'form': form,
        'is_edit': False,
    })


# UPDATE
@login_required
@permission_required('compliance.change_compliance', raise_exception=True)
def compliance_update(request, pk):
    obj = get_object_or_404(Compliance, pk=pk, is_active=True)
    form = ComplianceForm(request.POST or None, instance=obj)

    if form.is_valid():
        form.save()
        messages.success(request, "Compliance record updated successfully.")
        return redirect('compliance:compliance_list')

    if request.method == "POST":
        messages.error(request, "Failed to update compliance record.")

    return render(request, 'compliance/compliance_form.html', {
        'form': form,
        'is_edit': True,
    })


# DELETE (SOFT)
@login_required
@permission_required('compliance.delete_compliance', raise_exception=True)
def compliance_delete(request, pk):
    obj = get_object_or_404(Compliance, pk=pk, is_active=True)

    if request.method == "POST":
        obj.is_active = False
        obj.save()
        messages.success(request, "Compliance record deleted.")
        return redirect('compliance:compliance_list')

    return render(request, 'compliance/compliance_delete.html', {'c': obj})
