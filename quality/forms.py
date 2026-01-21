from django import forms
from django.utils.safestring import mark_safe
from .models import MaterialTest, WorkApproval
from projects.models import Project

# ---------------- Base Form ----------------
class BaseForm(forms.ModelForm):
    """
    Base form to:
    - Add red * to required fields
    - Apply Tailwind styling
    - Filter project dropdowns (if present)
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


# ---------------- Material Test Form ----------------
class MaterialTestForm(BaseForm):
    class Meta:
        model = MaterialTest
        fields = [
            "project",
            "material_type",
            "test_date",
            "result",
            "consultant",
            "report_file",
        ]
        widgets = {
            "test_date": forms.DateInput(attrs={"type": "date"}),
            "consultant": forms.TextInput(attrs={"placeholder": "Consultant name"}),
            "report_file": forms.ClearableFileInput(),
        }


# ---------------- Work Approval Form ----------------
class WorkApprovalForm(BaseForm):
    class Meta:
        model = WorkApproval
        fields = ["activity", "remarks"]
        widgets = {
            "remarks": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Optional remarks or notes"
            }),
        }
