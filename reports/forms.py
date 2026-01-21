from django import forms
from django.utils.safestring import mark_safe
from projects.models import Project
from reports.models import ProgressReportCover

class ProgressReportCoverForm(forms.ModelForm):
    class Meta:
        model = ProgressReportCover
        fields = [
            "project",
            "report_title",
            "report_no",
            "period_from",
            "period_to",
            "prepared_by",
            "cover_image",
        ]
        widgets = {
            "period_from": forms.DateInput(attrs={"type": "date"}),
            "period_to": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Make all fields required & add red asterisk
        for field_name, field in self.fields.items():
            field.required = True
            if field.label:
                field.label = mark_safe(f"{field.label} <span class='text-red-500'>*</span>")

        # Restrict projects to assigned projects
        if "project" in self.fields and user:
            if user.is_superuser or user.is_staff:
                self.fields["project"].queryset = Project.objects.filter(is_active=True)
            else:
                self.fields["project"].queryset = Project.objects.filter(
                    is_active=True,
                    participants__user=user,
                    participants__is_active=True,
                ).distinct()
