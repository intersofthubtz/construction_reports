from django.contrib import admin
from .models import PaymentCertificate, FundTransaction


@admin.register(PaymentCertificate)
class PaymentCertificateAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "certificate_no",
        "certified_amount",
        "amount_paid",
        "payment_date",
        "is_active",
    )
    list_filter = ("project", "payment_date", "is_active")
    search_fields = ("certificate_no", "pv_no", "amount_to")
    readonly_fields = ("created_at",)


@admin.register(FundTransaction)
class FundTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "date",
        "payee",
        "type",
        "amount_paid",
        "balance_after",
        "is_active",
    )
    list_filter = ("project", "type", "date", "is_active")
    search_fields = ("payee", "pv_or_receipt_no")
    readonly_fields = ("balance_after", "created_at")
