from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from projects.models import Project
from .models import PaymentCertificate, FundTransaction
from .forms import PaymentCertificateForm, FundTransactionForm

# ---------------- Helpers ----------------
def get_allowed_projects(user):
    if user.is_superuser or user.is_staff:
        return Project.objects.filter(is_active=True)
    return Project.objects.filter(
        is_active=True,
        participants__user=user,
        participants__is_active=True
    ).distinct()


def filter_by_allowed_projects(queryset, user):
    if user.is_superuser or user.is_staff:
        return queryset
    return queryset.filter(project__in=get_allowed_projects(user))


# ---------------- Payment Certificate ----------------
@login_required
@permission_required('finance.view_paymentcertificate', raise_exception=True)
def payment_list(request):
    search = request.GET.get('q', '').strip()
    queryset = PaymentCertificate.objects.filter(is_active=True)
    queryset = filter_by_allowed_projects(queryset, request.user)

    if search:
        queryset = queryset.filter(
            Q(project__project_name__icontains=search) |
            Q(certificate_no__icontains=search) |
            Q(amount_to__icontains=search)
        )

    paginator = Paginator(queryset.order_by('-payment_date'), 10)
    payments = paginator.get_page(request.GET.get('page'))

    return render(request, "finance/payment_list.html", {'payments': payments, 'search': search})


@login_required
@permission_required("finance.view_paymentcertificate", raise_exception=True)
def payment_view(request, pk):
    payment = get_object_or_404(
        filter_by_allowed_projects(PaymentCertificate.objects.filter(is_active=True), request.user),
        pk=pk
    )
    return render(request, "finance/payment_detail.html", {"payment": payment})


@login_required
@permission_required("finance.add_paymentcertificate", raise_exception=True)
def payment_create(request):
    allowed_projects = get_allowed_projects(request.user)
    form = PaymentCertificateForm(request.POST or None)
    form.fields['project'].queryset = allowed_projects

    if form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.save()
        messages.success(request, "Payment recorded successfully")
        return redirect("finance:payment_list")

    return render(request, "finance/payment_form.html", {"form": form, "is_edit": False})


@login_required
@permission_required("finance.change_paymentcertificate", raise_exception=True)
def payment_update(request, pk):
    payment = get_object_or_404(
        filter_by_allowed_projects(PaymentCertificate.objects.filter(is_active=True), request.user),
        pk=pk
    )
    allowed_projects = get_allowed_projects(request.user)
    form = PaymentCertificateForm(request.POST or None, instance=payment)
    form.fields['project'].queryset = allowed_projects

    if form.is_valid():
        form.save()
        messages.success(request, "Payment updated successfully")
        return redirect("finance:payment_list")

    return render(request, "finance/payment_form.html", {"form": form, "is_edit": True})


@login_required
@permission_required("finance.delete_paymentcertificate", raise_exception=True)
def payment_delete(request, pk):
    payment = get_object_or_404(
        filter_by_allowed_projects(PaymentCertificate.objects.filter(is_active=True), request.user),
        pk=pk
    )
    if request.method == "POST":
        payment.is_active = False
        payment.save()
        messages.success(request, f'Payment "{payment.certificate_no}" for project "{payment.project.project_name}" has been deleted.')
        return redirect("finance:payment_list")
    return render(request, "finance/payment_delete.html", {"p": payment})


# ---------------- Fund Transaction ----------------
@login_required
@permission_required("finance.view_fundtransaction", raise_exception=True)
def transaction_list(request):
    search = request.GET.get('q', '').strip()
    queryset = FundTransaction.objects.filter(is_active=True)
    queryset = filter_by_allowed_projects(queryset, request.user)

    if search:
        queryset = queryset.filter(
            Q(payee__icontains=search) |
            Q(type__icontains=search) |
            Q(pv_or_receipt_no__icontains=search)
        )

    paginator = Paginator(queryset.order_by('-date'), 10)
    transactions = paginator.get_page(request.GET.get('page'))

    return render(request, "finance/transaction_list.html", {"transactions": transactions, "search": search})


@login_required
@permission_required("finance.view_fundtransaction", raise_exception=True)
def transaction_view(request, pk):
    transaction = get_object_or_404(
        filter_by_allowed_projects(FundTransaction.objects.filter(is_active=True), request.user),
        pk=pk
    )
    return render(request, "finance/transaction_view.html", {"transaction": transaction})


@login_required
@permission_required("finance.add_fundtransaction", raise_exception=True)
def transaction_create(request):
    allowed_projects = get_allowed_projects(request.user)
    form = FundTransactionForm(request.POST or None)
    form.fields['project'].queryset = allowed_projects

    if form.is_valid():
        obj = form.save(commit=False)
        obj.created_by = request.user
        obj.save()
        messages.success(request, "Transaction recorded successfully")
        return redirect("finance:transaction_list")

    return render(request, "finance/transaction_form.html", {"form": form, "is_edit": False})


@login_required
@permission_required("finance.change_fundtransaction", raise_exception=True)
def transaction_update(request, pk):
    transaction = get_object_or_404(
        filter_by_allowed_projects(FundTransaction.objects.filter(is_active=True), request.user),
        pk=pk
    )
    allowed_projects = get_allowed_projects(request.user)
    form = FundTransactionForm(request.POST or None, instance=transaction)
    form.fields['project'].queryset = allowed_projects

    if form.is_valid():
        form.save()
        messages.success(request, "Transaction updated successfully")
        return redirect("finance:transaction_list")

    return render(request, "finance/transaction_form.html", {"form": form, "is_edit": True})


@login_required
@permission_required("finance.delete_fundtransaction", raise_exception=True)
def transaction_delete(request, pk):
    transaction = get_object_or_404(
        filter_by_allowed_projects(FundTransaction.objects.filter(is_active=True), request.user),
        pk=pk
    )
    if request.method == "POST":
        transaction.is_active = False
        transaction.save()
        messages.success(request, f'Transaction for "{transaction.payee}" on {transaction.date} has been deleted.')
        return redirect("finance:transaction_list")
    return render(request, "finance/transaction_delete.html", {"tx": transaction})
