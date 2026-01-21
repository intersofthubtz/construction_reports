from django import forms
from django.utils.safestring import mark_safe
from .models import Compliance
from setup.models import Authority
from projects.models import Project

# ---------------- Base Form ----------------
class BaseForm(forms.ModelForm):
    """
    Base form to:
    - Add red * to required fields
    - Apply Tailwind styling
    - Filter project and authority dropdowns (if present)
    - Make all fields required
    """

    TAILWIND_CLASSES = "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Make all fields required
            field.required = True

            # Add red * to required fields
            if field.required and field.label:
                field.label = mark_safe(f"{field.label} <span class='text-red-500'>*</span>")

            # Apply Tailwind classes
            existing_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_class} {self.TAILWIND_CLASSES}".strip()

            # For number fields, set min=1
            if isinstance(field, forms.IntegerField):
                field.widget.attrs.setdefault("min", 1)

        # Filter project dropdown if exists
        if "project" in self.fields:
            self.fields["project"].queryset = Project.objects.filter(is_active=True)

        # Filter authority dropdown if exists
        if "authority" in self.fields:
            self.fields["authority"].queryset = Authority.objects.filter(is_active=True)


# ---------------- Compliance Form ----------------
class ComplianceForm(BaseForm):
    class Meta:
        model = Compliance
        fields = [
            "project",
            "authority",
            "registration_no",
            "status",
            "expiry_date",
        ]
        widgets = {
            "registration_no": forms.TextInput(attrs={"placeholder": "Registration / License Number"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_expiry_date(self):
        expiry_date = self.cleaned_data.get("expiry_date")
        if not expiry_date:
            raise forms.ValidationError("Expiry date is required.")
        return expiry_date
