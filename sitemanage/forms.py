from django import forms
from sitemanage.models import Activity, ProgressLog, SiteProjectImage, SiteVisitor
from setup.models import WorkCategory
from projects.models import Project
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from .services import get_allowed_projects 

class RequiredFieldMixin:
    """
    Automatically append red * to required field labels
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.required and field.label:
                field.label = mark_safe(
                    f"{field.label} <span class='text-red-500'>*</span>"
                )




class BaseFilterForm(forms.Form):
    """
    Base form for filter forms:
    - Add red * to required fields
    - Apply Tailwind styling
    """
    TAILWIND_CLASSES = "border rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-500"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Add red * to required fields
            if field.required and field.label:
                field.label = mark_safe(f"{field.label} <span class='text-red-500'>*</span>")
            # Apply Tailwind styling
            existing_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_class} {self.TAILWIND_CLASSES}".strip()


class SiteOverviewFilterForm(BaseFilterForm):
    project_name = forms.ModelChoiceField(
        label="Project",
        queryset=Project.objects.none(), 
        required=True,
        empty_label="------",  
        widget=forms.Select()
    )

    activity_start = forms.DateField(
        label="Activity Start Date",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )

    activity_end = forms.DateField(
        label="Activity End Date",
        required=False,
        widget=forms.DateInput(attrs={"type": "date"})
    )

    status = forms.ChoiceField(
        label="Activity Status",
        choices=[
            ("", "------"),  # placeholder for empty choice
            ("Pending", "Pending"),
            ("In Progress", "In Progress"),
            ("Completed", "Completed"),
            ("Delayed", "Delayed"),
        ],
        required=False,
        widget=forms.Select()
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            # Only show projects where user is a participant
            self.fields["project_name"].queryset = Project.objects.filter(
                participants__user=user,
                participants__is_active=True
            ).distinct()
# ---------------------------
# ACTIVITY FORM
# ---------------------------
class ActivityForm(RequiredFieldMixin, forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            "project",
            "category",
            "name",
            "description",
            "planned_start",
            "planned_end",
        ]
        widgets = {
            "planned_start": forms.DateInput(attrs={"type": "date"}),
            "planned_end": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project"].queryset = Project.objects.filter(is_active=True)
        self.fields["category"].queryset = WorkCategory.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("planned_start")
        end = cleaned_data.get("planned_end")
        if start and end and end < start:
            raise ValidationError("Planned end cannot be before start.")
        return cleaned_data


# ---------------------------
# PROGRESS LOG FORM
# ---------------------------
class ProgressLogForm(RequiredFieldMixin, forms.ModelForm):
    class Meta:
        model = ProgressLog
        fields = ["date", "progress_percent", "remarks"]  
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "progress_percent": forms.NumberInput(attrs={"min": 0, "max": 100}),
            "remarks": forms.Textarea(attrs={"rows": 3}),
        }




# ---------------------------
# SITE VISITOR FORM (FINAL)
# ---------------------------
class SiteVisitorForm(RequiredFieldMixin, forms.ModelForm):
    class Meta:
        model = SiteVisitor
        fields = ["project", "document_name", "document_file", "visit_date"]

        widgets = {
            "project": forms.Select(attrs={
                "class": "w-full border rounded px-3 py-2",
            }),
            "document_name": forms.TextInput(attrs={
                "class": "w-full border rounded px-3 py-2",
                "placeholder": "Visitors Book – October 2025",
            }),
            "document_file": forms.ClearableFileInput(attrs={
                "class": "w-full border rounded px-3 py-2",
                "accept": "application/pdf",
            }),
            "visit_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full border rounded px-3 py-2",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Optional: show only active projects
        self.fields["project"].queryset = Project.objects.filter(is_active=True)

    def clean_document_file(self):
        file = self.cleaned_data.get("document_file")

        if not file:
            raise ValidationError("Document file is required.")

        if not file.name.lower().endswith(".pdf"):
            raise ValidationError("Only PDF documents are allowed.")

        return file

class SiteProjectImageForm(RequiredFieldMixin, forms.ModelForm):
    class Meta:
        model = SiteProjectImage
        fields = ["project", "activity", "figure_name", "image_date", "image"]
        widgets = {
            "project": forms.Select(attrs={"class": "w-full border rounded px-3 py-2"}),
            "activity": forms.Select(attrs={"class": "w-full border rounded px-3 py-2"}),
            "figure_name": forms.TextInput(attrs={
                "class": "w-full border rounded px-3 py-2",
                "placeholder": "Excavation Progress – Day 3"
            }),
            "image_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full border rounded px-3 py-2"
            }),
            "image": forms.ClearableFileInput(attrs={
                "class": "w-full border rounded px-3 py-2",
                "accept": "image/png,image/jpeg,image/jpg",
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["project"].queryset = get_allowed_projects(user)
        else:
            self.fields["project"].queryset = Project.objects.none()

        # --- Populate activity based on POST data or instance ---
        if "project" in self.data:
            try:
                project_id = int(self.data.get("project"))
                self.fields["activity"].queryset = Activity.objects.filter(
                    project_id=project_id,
                    is_active=True
                )
            except (ValueError, TypeError):
                self.fields["activity"].queryset = Activity.objects.none()
        elif self.instance.pk and self.instance.project:
            self.fields["activity"].queryset = Activity.objects.filter(
                project=self.instance.project,
                is_active=True
            )
        else:
            self.fields["activity"].queryset = Activity.objects.none()

        # Force activity required
        self.fields["activity"].required = True

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if not image:
            raise ValidationError("Image is required.")
        if hasattr(image, "content_type"):
            if image.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
                raise ValidationError("Only JPG, JPEG, and PNG images are allowed.")
            if image.size > 5 * 1024 * 1024:
                raise ValidationError("Image must be under 5 MB.")
        return image

    
    
    






