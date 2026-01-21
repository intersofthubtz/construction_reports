from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile

from .models import Project, ProjectContractor, ProjectParticipant, ProjectDocument
from setup.models import Contractor, ProjectRole

# ---------------- Shared Tailwind Style ----------------
TAILWIND_INPUT = (
    "w-full border border-gray-300 rounded px-3 py-2 "
    "focus:outline-none focus:ring-2 focus:ring-blue-500 "
    "focus:border-blue-500 text-sm bg-white"
)

# ---------------- Date widget ----------------
class DateInput(forms.DateInput):
    input_type = "date"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("attrs", {})
        kwargs["attrs"]["class"] = TAILWIND_INPUT
        super().__init__(*args, **kwargs)


# ---------------- Project Form ----------------
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ["created_by", "created_at", "updated_at", "is_active"]

        widgets = {
            field: DateInput()
            for field in [
                "contract_signing_date",
                "site_possession_date",
                "mobilization_start",
                "mobilization_end",
                "commencement_date",
                "practical_completion_date",
                "defects_start",
                "defects_end",
            ]
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, DateInput):
                field.widget.attrs["class"] = TAILWIND_INPUT


# ---------------- Contractor Formset ----------------
ProjectContractorFormSet = inlineformset_factory(
    Project,
    ProjectContractor,
    fields=["contractor", "work_description"],
    extra=1,
    can_delete=True,
    widgets={
        "contractor": forms.Select(attrs={"class": TAILWIND_INPUT}),
        "work_description": forms.TextInput(attrs={"class": TAILWIND_INPUT}),
    },
)


# ---------------- Participant Form ----------------
class ProjectParticipantForm(forms.ModelForm):
    class Meta:
        model = ProjectParticipant
        fields = ["user", "project_role"]
        widgets = {
            "user": forms.Select(attrs={"class": TAILWIND_INPUT}),
            "project_role": forms.Select(attrs={"class": TAILWIND_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["project_role"].queryset = ProjectRole.objects.filter(is_active=True)


# ---------------- Participant Formset ----------------
ProjectParticipantFormSet = inlineformset_factory(
    Project,
    ProjectParticipant,
    form=ProjectParticipantForm,
    extra=1,
    can_delete=True,
)


# ---------------- Document Form ----------------
class ProjectDocumentForm(forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ["title", "document"]
        widgets = {
            "title": forms.TextInput(attrs={"class": TAILWIND_INPUT}),
            "document": forms.ClearableFileInput(
                attrs={
                    "class": TAILWIND_INPUT,
                    "accept": "application/pdf",
                }
            ),
        }

    def clean_document(self):
        document = self.cleaned_data.get("document")

        if not document:
            return document

        if not isinstance(document, UploadedFile):
            return document

        if not document.name.lower().endswith(".pdf"):
            raise ValidationError("Only PDF files are allowed.")

        if document.content_type != "application/pdf":
            raise ValidationError("Invalid file type. Please upload a PDF document.")

        if document.size > 10 * 1024 * 1024:
            raise ValidationError("File size must be under 10MB.")

        return document
