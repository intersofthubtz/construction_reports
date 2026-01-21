from django import forms
from django.utils.safestring import mark_safe
from .models import Equipment, Manpower
from projects.models import Project

# ---------------- Base Form ----------------
class BaseResourceForm(forms.ModelForm):
    """
    Base form for Equipment and Manpower to:
    - Add red * to required fields
    - Apply Tailwind classes
    - Filter project dropdown to active projects
    - Make all fields required
    """

    TAILWIND_CLASSES = "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Make all fields required
            field.required = True

            # Add red * to required field labels
            if field.required and field.label:
                field.label = mark_safe(f"{field.label} <span class='text-red-500'>*</span>")

            # Apply Tailwind styling to widgets
            existing_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_class} {self.TAILWIND_CLASSES}".strip()

            # Special handling for number fields
            if isinstance(field, forms.IntegerField):
                field.widget.attrs.setdefault("min", 1)

        # Filter project field if it exists
        if "project" in self.fields:
            self.fields["project"].queryset = Project.objects.filter(is_active=True)


# ---------------- Equipment Form ----------------
class EquipmentForm(BaseResourceForm):
    class Meta:
        model = Equipment
        fields = ["project", "name", "category", "quantity", "condition", "delivery_date"]
        widgets = {
            "delivery_date": forms.DateInput(attrs={"type": "date"}),
            "condition": forms.Select(),
            "category": forms.TextInput(),
            "name": forms.TextInput(),
            "quantity": forms.NumberInput(),
        }


# ---------------- Manpower Form ----------------
class ManpowerForm(BaseResourceForm):
    class Meta:
        model = Manpower
        fields = ["project", "role", "count", "start_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "role": forms.TextInput(),
            "count": forms.NumberInput(),
        }
