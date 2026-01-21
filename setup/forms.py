from django import forms
from django.utils.safestring import mark_safe
from .models import Client, ContractorType, Contractor, ProjectRole, WorkCategory, Authority

# ---------------- Base Form ----------------
class BaseSetupForm(forms.ModelForm):
    """
    Base form for setup models to:
    - Apply Tailwind styling
    - Add red * to required fields
    - Make all fields required by default
    - Handle read-only fields in child forms
    """

    TAILWIND_CLASSES = "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Make all fields required by default
            field.required = True

            # Exclude description from being required
            if field_name == "description":
                field.required = False

            # Add red * to required fields
            if field.required and field.label:
                field.label = mark_safe(f"{field.label} <span class='text-red-500'>*</span>")

            # Apply Tailwind classes
            existing_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_class} {self.TAILWIND_CLASSES}".strip()

            # Set textarea rows if not already set
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 3)


class UniqueActiveNameMixin:
    def clean_name(self):
        name = self.cleaned_data["name"]

        qs = self._meta.model.objects.filter(
            name__iexact=name,
            is_active=True
        )

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("This name already exists.")

        return name
    
    
# ---------------- Client Form ----------------
class ClientForm(BaseSetupForm):
    class Meta:
        model = Client
        fields = ['tin_number', 'name', 'postal_address', 'city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make TIN read-only when editing
        if self.instance and self.instance.pk:
            self.fields['tin_number'].disabled = True

# ---------------- Contractor Type Form ----------------
class ContractorTypeForm(BaseSetupForm):
    class Meta:
        model = ContractorType
        fields = ['name', 'description']

# ---------------- Contractor Form ----------------
class ContractorForm(BaseSetupForm):
    class Meta:
        model = Contractor
        fields = ['tin_number', 'contractor_type', 'name', 'address', 'city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['tin_number'].disabled = True

class ProjectRoleForm(UniqueActiveNameMixin, BaseSetupForm):
    class Meta:
        model = ProjectRole
        fields = ["name", "description"]


class WorkCategoryForm(UniqueActiveNameMixin, BaseSetupForm):
    class Meta:
        model = WorkCategory
        fields = ["name", "description"]


class AuthorityForm(UniqueActiveNameMixin, BaseSetupForm):
    class Meta:
        model = Authority
        fields = ["name", "description"]
