from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Project, ProjectDocument
from .forms import ProjectForm, ProjectDocumentForm, ProjectContractorFormSet, ProjectParticipantFormSet

# -----------------------------
# Project List
# -----------------------------
@login_required
@permission_required("projects.view_project", raise_exception=True)
def project_list(request):

    if request.user.is_superuser or request.user.is_staff:
        # Admins see all projects
        projects = Project.objects.filter(is_active=True)
    else:
        # Normal users see only assigned projects
        projects = Project.objects.filter(
            participants__user=request.user,
            participants__is_active=True,
            is_active=True
        ).distinct()

    projects = projects.select_related("client").order_by("-commencement_date")

    # Search
    search = request.GET.get("q", "").strip()
    if search:
        projects = projects.filter(
            Q(project_code__icontains=search) |
            Q(project_name__icontains=search) |
            Q(client__name__icontains=search)
        )

    paginator = Paginator(projects, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "projects/project_list.html", {
        "projects": page_obj,
        "search": search,
    })

# -----------------------------
# Project Detail
# -----------------------------
@login_required
@permission_required("projects.view_project", raise_exception=True)
def project_detail(request, pk):

    if request.user.is_superuser or request.user.is_staff:
        project = get_object_or_404(Project, pk=pk, is_active=True)
    else:
        project = get_object_or_404(
            Project,
            pk=pk,
            is_active=True,
            participants__user=request.user,
            participants__is_active=True
        )

    return render(request, "projects/project_detail.html", {"project": project})



# -----------------------------
# Project Create
# -----------------------------
@login_required
@permission_required("projects.add_project", raise_exception=True)
def project_create(request):
    if request.method == "POST":
        project_form = ProjectForm(request.POST)
        contractor_formset = ProjectContractorFormSet(request.POST, prefix="contractor")
        participant_formset = ProjectParticipantFormSet(request.POST, prefix="participant")
        document_form = ProjectDocumentForm(request.POST, request.FILES)

        if (
            project_form.is_valid()
            and contractor_formset.is_valid()
            and participant_formset.is_valid()
            and document_form.is_valid()
        ):
            try:
                with transaction.atomic():
                    project = project_form.save(commit=False)
                    project.created_by = request.user
                    project.save()

                    contractor_formset.instance = project
                    contractor_formset.save()

                    participant_formset.instance = project
                    participant_formset.save()

                    if document_form.cleaned_data.get("document"):
                        document = document_form.save(commit=False)
                        document.project = project
                        document.uploaded_by = request.user
                        document.save()

                messages.success(request, "✅ Project created successfully.")
                return redirect("projects:project_list")

            except Exception:
                messages.error(
                    request,
                    "❌ Failed to create project. Please try again."
                )

        else:
            messages.error(
                request,
                "❌ Failed to create project. Please correct the errors below."
            )

        # ❗ IMPORTANT: re-render form with errors
        return render(request, "projects/project_form.html", {
            "project_form": project_form,
            "contractor_formset": contractor_formset,
            "participant_formset": participant_formset,
            "document_form": document_form,
            "existing_doc": None,
        })

    else:
        project_form = ProjectForm()
        contractor_formset = ProjectContractorFormSet(prefix="contractor")
        participant_formset = ProjectParticipantFormSet(prefix="participant")
        document_form = ProjectDocumentForm()

    return render(request, "projects/project_form.html", {
        "project_form": project_form,
        "contractor_formset": contractor_formset,
        "participant_formset": participant_formset,
        "document_form": document_form,
        "existing_doc": None,
    })
 
    
# -----------------------------
# Project Edit 
# -----------------------------
@login_required
@permission_required("projects.change_project", raise_exception=True)
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        project_form = ProjectForm(request.POST, instance=project)
        contractor_formset = ProjectContractorFormSet(
            request.POST, instance=project, prefix="contractor"
        )
        participant_formset = ProjectParticipantFormSet(
            request.POST, instance=project, prefix="participant"
        )
        document_form = ProjectDocumentForm(
            request.POST,
            request.FILES,
            instance=project.documents.first() if project.documents.exists() else None,
        )

        project_valid = project_form.is_valid()
        contractor_valid = contractor_formset.is_valid()
        participant_valid = participant_formset.is_valid()
        document_valid = document_form.is_valid()
        
        # Debug: print errors to consol
        if not project_valid:
           print("ProjectForm errors:", project_form.errors)
        if not contractor_valid:
           print("ContractorFormSet errors:", contractor_formset.errors)
        if not participant_valid:
            print("ParticipantFormSet errors:", participant_formset.errors)
        if not document_valid:
            print("DocumentForm errors:", document_form.errors)


        if project_valid and contractor_valid and participant_valid and document_valid:
            try:
                with transaction.atomic():
                    project = project_form.save(commit=False)
                    project.updated_at = timezone.now()
                    project.save()

                    contractor_formset.instance = project
                    contractor_formset.save()

                    participant_formset.instance = project
                    participant_formset.save()

                    if document_form.cleaned_data.get("document"):
                        doc = document_form.save(commit=False)
                        doc.project = project
                        doc.uploaded_by = request.user
                        doc.save()

                messages.success(request, "✅ Project updated successfully.")
                return redirect("projects:project_list")
            except Exception:
                messages.error(request, "❌ Failed to update project. Please try again.")
        else:
            messages.error(request, "❌ Failed to update project. Please correct the errors below.")
    else:
        project_form = ProjectForm(instance=project)
        contractor_formset = ProjectContractorFormSet(instance=project, prefix="contractor")
        participant_formset = ProjectParticipantFormSet(instance=project, prefix="participant")
        document_form = ProjectDocumentForm(
            instance=project.documents.first() if project.documents.exists() else None
        )

    return render(
        request,
        "projects/project_form.html",
        {
            "project_form": project_form,
            "contractor_formset": contractor_formset,
            "participant_formset": participant_formset,
            "document_form": document_form,
        },
    )


# -----------------------------
# Project Delete    
# -----------------------------
@login_required
@permission_required("projects.delete_project", raise_exception=True)
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, is_active=True)

    if request.method == "POST":
        try:
            # Mark project as inactive
            project.is_active = False
            project.save()

            # Optionally mark related records inactive
            project.documents.update(is_active=False)
            project.participants.update(is_active=False)
            project.contractors.update(is_active=False)

            messages.success(request, "✅ Project deactivated successfully (all files kept).")
            return redirect("projects:project_list")

        except Exception as e:
            messages.error(request, f"❌ Failed to deactivate project. Error: {e}")
            return redirect("projects:project_list")

    return render(
        request,
        "projects/project_confirm_delete.html",
        {"project": project}
    )
