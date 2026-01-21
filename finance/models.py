from django.db import models
from django.contrib.auth.models import User
from projects.models import Project


class PaymentCertificate(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="payment_certificates"
    )

    certificate_no = models.CharField(max_length=100, unique=True)
    certified_amount = models.DecimalField(max_digits=15, decimal_places=2)
    date_certified = models.DateField()

    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    amount_from = models.CharField(max_length=255)
    amount_to = models.CharField(max_length=255)

    payment_date = models.DateField()
    pv_no = models.CharField(max_length=50)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-payment_date"]
        # permissions = [
        #     ("view_paymentcertificate", "Can view Payment Certificates"),
        # ]

    def __str__(self):
        return f"{self.certificate_no} – {self.project}"


class FundTransaction(models.Model):
    CREDIT = "Credit"
    DEBIT = "Debit"

    TRANSACTION_TYPES = [
        (CREDIT, "Credit"),
        (DEBIT, "Debit"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="fund_transactions"
    )

    date = models.DateField()
    payee = models.CharField(max_length=255)
    type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)

    description = models.TextField()
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        editable=False
    )

    pv_or_receipt_no = models.CharField(max_length=50)
    remarks = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["date", "id"]
        # permissions = [
        #     ("view_fundtransaction", "Can view Fund Transactions"),
        # ]

    def save(self, *args, **kwargs):
        """
        Auto-calculate running balance per project
        """
        last_tx = (
            FundTransaction.objects
            .filter(project=self.project)
            .exclude(pk=self.pk)
            .order_by("-date", "-id")
            .first()
        )

        previous_balance = last_tx.balance_after if last_tx else 0

        if self.type == self.CREDIT:
            self.balance_after = previous_balance + self.amount_paid
        else:
            self.balance_after = previous_balance - self.amount_paid

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.project} | {self.type} | {self.amount_paid}"

