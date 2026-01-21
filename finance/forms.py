from django import forms
from django.utils.safestring import mark_safe
from .models import PaymentCertificate, FundTransaction
from projects.models import Project

class RequiredFieldMixin:
    """Auto add * to required fields"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.required and field.label:
                field.label = mark_safe(f"{field.label} <span class='text-red-500'>*</span>")
                
# ---------------- Payment Certificate Form ----------------
class PaymentCertificateForm(RequiredFieldMixin, forms.ModelForm):
    class Meta:
        model = PaymentCertificate
        fields = "__all__"
        exclude = ("created_by", "created_at", "is_active")
        widgets = {
            "project": forms.Select(attrs={"class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "certificate_no": forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "certified_amount": forms.NumberInput(attrs={"class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "date_certified": forms.DateInput(attrs={"type": "date", "class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "amount_paid": forms.NumberInput(attrs={"class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "amount_from": forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "amount_to": forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "payment_date": forms.DateInput(attrs={"type": "date", "class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "pv_no": forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only active projects
        self.fields["project"].queryset = Project.objects.filter(is_active=True)
        for field in self.fields.values():
            field.required = True

# ---------------- Fund Transaction Form ----------------
class FundTransactionForm(RequiredFieldMixin, forms.ModelForm):
    class Meta:
        model = FundTransaction
        fields = "__all__"
        exclude = ("created_by", "created_at", "balance_after", "is_active")
        widgets = {
            "project": forms.Select(attrs={"class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "payee": forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "type": forms.Select(attrs={"class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "amount_paid": forms.NumberInput(attrs={"class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "pv_or_receipt_no": forms.TextInput(attrs={"class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
            "remarks": forms.Textarea(attrs={"rows": 2, "class": "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = Project.objects.filter(is_active=True)
        for field in self.fields.values():
            field.required = True
