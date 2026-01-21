import logging
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Max, Q
from django.contrib.auth.decorators import login_required, permission_required
import io
from django.http import HttpResponse
from django.template.loader import get_template
from weasyprint import CSS, HTML
from django.template.loader import render_to_string
from projects.models import Project
from sitemanage.models import Activity, ProgressLog, SiteProjectImage, SiteVisitor
from sitemanage.forms import ActivityForm, ProgressLogForm, SiteOverviewFilterForm, SiteProjectImageForm, SiteVisitorForm
from sitemanage.services import get_project_site_overview, get_weekly_progress_trend
from .services import get_allowed_projects
logger = logging.getLogger(__name__)

# ---------------- Helpers ----------------
def get_allowed_projects(user):
    """Return queryset of projects the user is allowed to see."""
    if user.is_superuser or user.is_staff:
        return Project.objects.filter(is_active=True)
    return Project.objects.filter(
        is_active=True,
        participants__user=user,
        participants__is_active=True
    ).distinct()


def filter_by_allowed_projects(queryset, user):
    """Filter a queryset by allowed projects."""
    if user.is_superuser or user.is_staff:
        return queryset
    return queryset.filter(project__in=get_allowed_projects(user))


# ---------------- Site Overview ----------------
@login_required
@permission_required("sitemanage.access_sitemanage", raise_exception=True)
def site_overview(request):
    try:
        # Pass user to form to populate project dropdown
        form = SiteOverviewFilterForm(request.GET or None, user=request.user)
        project_data = []

        if form.is_valid():
            selected_project = form.cleaned_data.get('project_name')
            activity_start = form.cleaned_data.get('activity_start')
            activity_end = form.cleaned_data.get('activity_end')
            status = form.cleaned_data.get('status')

            projects = [selected_project] if selected_project else []

            for project in projects:
                # Filter activities
                activities = project.activities.filter(is_active=True)
                if activity_start:
                    activities = activities.filter(planned_start__gte=activity_start)
                if activity_end:
                    activities = activities.filter(planned_end__lte=activity_end)
                if status:
                    activities = activities.filter(status=status)

                # Attach latest log to each activity
                activities_with_logs = []
                for a in activities:
                    latest_log = a.progress_logs.filter(is_active=True).order_by('-date').first()
                    activities_with_logs.append({
                        'activity': a,
                        'latest_log': latest_log
                    })

                # Visitors & images
                visitors = project.site_visitors.filter(is_active=True)
                images = project.project_images.filter(
                    project=project,
                    activity__in=activities,
                    is_active=True
                ).select_related("activity")

                project_data.append({
                    'project': project,
                    'activities': activities_with_logs,
                    'visitors': visitors,
                    'images': images
                })

        # Pagination
        paginator = Paginator(project_data, 5)
        paged_projects = paginator.get_page(request.GET.get('page', 1))

        context = {
            'page_title': 'Site Overview',
            'form': form,
            'project_data': paged_projects,
            'paged_projects': paged_projects,
        }

        return render(request, 'sitemanage/site_overview.html', context)

    except Exception as e:
        messages.error(request, f"Error loading site overview: {e}")
        context = {
            'page_title': 'Site Overview',
            'form': SiteOverviewFilterForm(user=request.user),
            'project_data': [],
            'paged_projects': [],
        }
        return render(request, 'sitemanage/site_overview.html', context)

# ---------------- Activity Views ----------------
@login_required
@permission_required('sitemanage.view_activity', raise_exception=True)
def activity_list(request):
    search = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    page_number = request.GET.get('page')

    activities = Activity.objects.filter(is_active=True).select_related('project', 'category')
    activities = filter_by_allowed_projects(activities, request.user)

    if search:
        activities = activities.filter(
            Q(name__icontains=search) |
            Q(project__project_name__icontains=search)
        )

    if status:
        activities = activities.filter(status=status)

    paginator = Paginator(activities.order_by('-id'), 10)
    page_obj = paginator.get_page(page_number)

    return render(request, 'sitemanage/activity_list.html', {
        "activities": page_obj,
        "search": search,
        "status": status,
    })


@login_required
@permission_required('sitemanage.view_activity', raise_exception=True)
def activity_detail(request, pk):
    activity = get_object_or_404(filter_by_allowed_projects(Activity.objects.filter(is_active=True), request.user), pk=pk)
    return render(request, 'sitemanage/activity_detail.html', {
        "page_title": f"Activity Detail: {activity.name}",
        "activity": activity
    })


@login_required
@permission_required('sitemanage.add_activity', raise_exception=True)
def activity_create(request):
    allowed_projects = get_allowed_projects(request.user)
    form = ActivityForm(request.POST or None)
    form.fields['project'].queryset = allowed_projects

    if form.is_valid():
        activity = form.save(commit=False)
        activity.created_by = request.user
        activity.updated_by = request.user
        activity.is_active = True
        activity.save()
        messages.success(request, "Activity created successfully!")
        return redirect('sitemanage:activity_list')

    return render(request, 'sitemanage/activity_form.html', {
        "form": form,
        "activity": None,
        "page_title": "Add Activity"
    })


@login_required
@permission_required('sitemanage.change_activity', raise_exception=True)
def activity_update(request, pk):
    activity = get_object_or_404(filter_by_allowed_projects(Activity.objects.filter(is_active=True), request.user), pk=pk)
    allowed_projects = get_allowed_projects(request.user)
    form = ActivityForm(request.POST or None, instance=activity)
    form.fields['project'].queryset = allowed_projects

    if form.is_valid():
        activity = form.save(commit=False)
        activity.updated_by = request.user
        activity.save()
        messages.success(request, "Activity updated successfully!")
        return redirect('sitemanage:activity_list')

    return render(request, 'sitemanage/activity_form.html', {
        "form": form,
        "activity": activity,
        "page_title": f"Edit Activity: {activity.name}"
    })


@login_required
@permission_required('sitemanage.delete_activity', raise_exception=True)
def activity_delete(request, pk):
    activity = get_object_or_404(filter_by_allowed_projects(Activity.objects.filter(is_active=True), request.user), pk=pk)
    if request.method == "POST":
        activity.is_active = False  # soft delete
        activity.save()
        messages.success(request, f"Activity {activity.name} deleted successfully!")
        return redirect('sitemanage:activity_list')

    return render(request, 'sitemanage/activity_confirm_delete.html', {
        "activity": activity,
        "page_title": f"Delete Activity: {activity.name}"
    })


# ---------------- Progress Log Views ----------------
@login_required
@permission_required('sitemanage.view_progresslog', raise_exception=True)
def progress_log_list(request, activity_id):
    activity = get_object_or_404(filter_by_allowed_projects(Activity.objects.filter(is_active=True), request.user), pk=activity_id)
    logs = activity.progress_logs.filter(is_active=True)

    last_log = logs.order_by('-date').first()
    is_completed = last_log and last_log.progress_percent == 100

    return render(request, 'sitemanage/progress_log_list.html', {
        'activity': activity,
        'logs': logs.order_by('-date'),
        'is_completed': is_completed,
    })


@login_required
@permission_required('sitemanage.add_progresslog', raise_exception=True)
def progress_log_create(request, activity_id):
    activity = get_object_or_404(
        filter_by_allowed_projects(Activity.objects.filter(is_active=True), request.user),
        pk=activity_id
    )

    if request.method == 'POST':
        # Pass instance with activity to the form
        form = ProgressLogForm(request.POST, instance=ProgressLog(activity=activity))
        if form.is_valid():
            log = form.save(commit=False)
            log.created_by = request.user
            log.is_active = True
            log.save()
            messages.success(request, 'Progress log added successfully.')
            return redirect('sitemanage:progress_log_list', activity_id=activity.id)
    else:
        form = ProgressLogForm(instance=ProgressLog(activity=activity))

    return render(request, 'sitemanage/progress_log_form.html', {
        'form': form,
        'activity': activity,
        'page_title': f"Add Progress for {activity.name}"
    })



@login_required
@permission_required('sitemanage.change_progresslog', raise_exception=True)
def progress_log_update(request, pk):
    # Only get logs for activities the user has access to
    log = get_object_or_404(
        ProgressLog.objects.filter(is_active=True),
        pk=pk
    )

    # Check if user has access to the activity/project
    allowed_activities = Activity.objects.filter(
        pk=log.activity.pk
    )
    allowed_activities = filter_by_allowed_projects(allowed_activities, request.user)
    if not allowed_activities.exists():
        messages.error(request, "Access denied.")
        return redirect('sitemanage:progress_log_list', activity_id=log.activity.id)

    form = ProgressLogForm(request.POST or None, instance=log)

    if form.is_valid():
        log = form.save(commit=False)
        log.updated_by = request.user
        log.save()
        messages.success(request, 'Progress log updated successfully.')
        return redirect('sitemanage:progress_log_list', activity_id=log.activity.id)

    return render(request, 'sitemanage/progress_log_form.html', {
        'form': form,
        'activity': log.activity,
        'page_title': f"Update Progress for {log.activity.name}",
        'log': log
    })




@login_required
@permission_required('sitemanage.delete_progresslog', raise_exception=True)
def progress_log_delete(request, pk):
    log = get_object_or_404(
    filter_by_allowed_projects(
        ProgressLog.objects.filter(is_active=True),
        request.user
    ),
    pk=pk
    )
    last_log = log.activity.progress_logs.filter(is_active=True).order_by('-date').first()
    if last_log and last_log.progress_percent == 100:
        messages.error(request, "Completed activities cannot be deleted.")
        return redirect('sitemanage:progress_log_list', activity_id=log.activity.id)

    activity_id = log.activity.id
    if request.method == 'POST':
        log.is_active = False  # soft delete
        log.save()
        messages.success(request, 'Progress log deleted successfully.')
        return redirect('sitemanage:progress_log_list', activity_id=activity_id)

    return render(request, 'sitemanage/progress_log_confirm_delete.html', {'log': log})


# ---------------- Site Visitor Views ----------------

@login_required
@permission_required("sitemanage.view_sitevisitor", raise_exception=True)
def site_visitor_list(request):
    search = request.GET.get("q", "").strip()

    # Base queryset with project access control
    qs = SiteVisitor.objects.filter(is_active=True).select_related("project")
    qs = filter_by_allowed_projects(qs, request.user)

    if search:
        qs = qs.filter(
            Q(document_name__icontains=search) |
            Q(project__project_name__icontains=search)
        )

    paginator = Paginator(qs.order_by("-visit_date"), 10)
    visitors = paginator.get_page(request.GET.get("page"))

    return render(request, "sitemanage/site_visitor_list.html", {
        "visitors": visitors,
        "search": search,
        "page_title": "Site Visitor Documents",
    })


@login_required
@permission_required("sitemanage.add_sitevisitor", raise_exception=True)
def site_visitor_create(request):
    allowed_projects = get_allowed_projects(request.user)

    if request.method == "POST":
        form = SiteVisitorForm(request.POST, request.FILES)
        form.fields["project"].queryset = allowed_projects

        if form.is_valid():
            visitor = form.save(commit=False)
            visitor.created_by = request.user
            visitor.is_active = True
            visitor.save()

            messages.success(
                request,
                f'Visitor document "{visitor.document_name}" uploaded successfully.'
            )
            return redirect("sitemanage:site_visitor_list")
    else:
        form = SiteVisitorForm()
        form.fields["project"].queryset = allowed_projects

    return render(request, "sitemanage/site_visitor_form.html", {
        "form": form,
        "is_edit": False,
        "page_title": "Add Site Visitor Document",
    })


@login_required
@permission_required("sitemanage.change_sitevisitor", raise_exception=True)
def site_visitor_edit(request, pk):
    # Secure object access
    visitor = get_object_or_404(
        filter_by_allowed_projects(
            SiteVisitor.objects.filter(is_active=True),
            request.user
        ),
        pk=pk
    )

    allowed_projects = get_allowed_projects(request.user)

    if request.method == "POST":
        form = SiteVisitorForm(request.POST, request.FILES, instance=visitor)
        form.fields["project"].queryset = allowed_projects

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Visitor document "{visitor.document_name}" updated successfully.'
            )
            return redirect("sitemanage:site_visitor_list")
    else:
        form = SiteVisitorForm(instance=visitor)
        form.fields["project"].queryset = allowed_projects

    return render(request, "sitemanage/site_visitor_form.html", {
        "form": form,
        "is_edit": True,
        "visitor": visitor,
        "page_title": "Edit Site Visitor Document",
    })


@login_required
@permission_required("sitemanage.delete_sitevisitor", raise_exception=True)
def site_visitor_delete(request, pk):
    visitor = get_object_or_404(
        filter_by_allowed_projects(
            SiteVisitor.objects.filter(is_active=True),
            request.user
        ),
        pk=pk
    )

    if request.method == "POST":
        visitor.is_active = False
        visitor.save(update_fields=["is_active"])

        messages.success(
            request,
            f'Visitor document "{visitor.document_name}" removed successfully.'
        )
        return redirect("sitemanage:site_visitor_list")

    return render(request, "sitemanage/site_visitor_confirm_delete.html", {
        "visitor": visitor,
        "page_title": "Delete Site Visitor Document",
    })


# ---------------- Site Project Image Views ----------------
@login_required
@permission_required("sitemanage.view_siteprojectimage", raise_exception=True)
def site_project_image_list(request):
    search = request.GET.get("q", "").strip()

    qs = SiteProjectImage.objects.filter(
        is_active=True
    ).select_related("project", "activity")

    qs = filter_by_allowed_projects(qs, request.user)

    if search:
        qs = qs.filter(
            Q(project__project_name__icontains=search) |
            Q(activity__name__icontains=search) |
            Q(figure_name__icontains=search)
        )

    # Group by project + activity + image_date
    batch_qs = (
        qs.values(
            "project",
            "project__project_name",
            "activity",
            "activity__name",
            "image_date"
        )
        .annotate(latest_id=Max("id"))
        .order_by("-image_date", "-latest_id")
    )

    latest_ids = [row["latest_id"] for row in batch_qs]

    images = (
        SiteProjectImage.objects
        .filter(id__in=latest_ids)
        .select_related("project", "activity")
        .order_by("-image_date")
    )

    paginator = Paginator(images, 10)
    page = request.GET.get("page")

    return render(request, "sitemanage/site_project_image_list.html", {
        "images": paginator.get_page(page),
        "search": search,
        "page_title": "Project Activity Images",
    })



@login_required
@permission_required("sitemanage.view_siteprojectimage", raise_exception=True)
def site_project_image_detail(request, pk):
    image_obj = get_object_or_404(
        SiteProjectImage.objects.filter(is_active=True),
        pk=pk
    )

    images = SiteProjectImage.objects.filter(
        project=image_obj.project,
        activity=image_obj.activity,
        image_date=image_obj.image_date,
        is_active=True
    ).order_by("-created_at")

    return render(request, "sitemanage/site_project_image_detail.html", {
        "image_obj": image_obj,
        "images": images,
        "page_title": (
            f"{image_obj.project.project_name} | "
            f"{image_obj.activity.name if image_obj.activity else 'General'} | "
            f"{image_obj.image_date}"
        ),
    })

@login_required
@permission_required("sitemanage.add_siteprojectimage", raise_exception=True)
def site_project_image_create(request):
    allowed_projects = get_allowed_projects(request.user)

    if request.method == "POST":
        form = SiteProjectImageForm(request.POST, request.FILES, user=request.user)
        images = request.FILES.getlist("image")  # multiple files

        if not images:
            messages.error(request, "Please select at least one image.")
        elif form.is_valid():
            success_count = 0
            for img in images:
                # Validate each image manually
                if img.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
                    messages.error(request, f"{img.name} has invalid file type.")
                    continue
                if img.size > 5 * 1024 * 1024:
                    messages.error(request, f"{img.name} exceeds 5 MB.")
                    continue

                try:
                    SiteProjectImage.objects.create(
                        project=form.cleaned_data["project"],
                        activity=form.cleaned_data["activity"],
                        figure_name=form.cleaned_data["figure_name"],
                        image_date=form.cleaned_data["image_date"],
                        image=img,
                        created_by=request.user,
                        is_active=True
                    )
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to save image {img.name}: {str(e)}")
                    messages.error(request, f"Failed to save '{img.name}': {str(e)}")

            if success_count:
                messages.success(request, f"{success_count} image(s) uploaded successfully.")
                return redirect("sitemanage:site_project_image_list")
            else:
                messages.error(request, "No images were uploaded. Check errors above.")

        else:
            logger.warning("SiteProjectImage form errors: %s", form.errors)
            messages.error(request, "Form validation failed. Check errors.")

    else:
        form = SiteProjectImageForm(user=request.user)

    return render(request, "sitemanage/site_project_image_form.html", {
        "form": form,
        "page_title": "Upload Project Image",
    })


@login_required
def ajax_load_activities(request):
    project_id = request.GET.get("project_id")
    selected_activity = request.GET.get("selected_activity")

    activities = Activity.objects.filter(
        project_id=project_id,
        is_active=True
    ).order_by("planned_start")

    return render(
        request,
        "sitemanage/partials/activity_options.html",
        {
            "activities": activities,
            "request": request, 
        }
    )


@login_required
@permission_required("sitemanage.change_siteprojectimage", raise_exception=True)
def site_project_image_edit(request, pk):
    image_obj = get_object_or_404(SiteProjectImage.objects.filter(is_active=True), pk=pk)
    allowed_projects = get_allowed_projects(request.user)

    batch_images = SiteProjectImage.objects.filter(
        project=image_obj.project,
        activity=image_obj.activity,
        figure_name=image_obj.figure_name,
        image_date=image_obj.image_date,
        is_active=True
    )

    if request.method == "POST":
        form = SiteProjectImageForm(request.POST, request.FILES, instance=image_obj, user=request.user)
        new_images = request.FILES.getlist("image")

        if form.is_valid():
            batch_data = {
                "project": form.cleaned_data["project"],
                "activity": form.cleaned_data["activity"],
                "figure_name": form.cleaned_data["figure_name"],
                "image_date": form.cleaned_data["image_date"],
            }
            batch_images.update(**batch_data)

            success_count = 0
            for img in new_images:
                if img.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
                    messages.error(request, f"{img.name} has invalid file type.")
                    continue
                if img.size > 5 * 1024 * 1024:
                    messages.error(request, f"{img.name} exceeds 5 MB.")
                    continue

                SiteProjectImage.objects.create(
                    project=batch_data["project"],
                    activity=batch_data["activity"],
                    figure_name=batch_data["figure_name"],
                    image_date=batch_data["image_date"],
                    image=img,
                    created_by=request.user,
                    is_active=True
                )
                success_count += 1

            messages.success(request, f"Batch updated successfully. {success_count} new image(s) added.")
            return redirect("sitemanage:site_project_image_list")
        else:
            logger.warning("SiteProjectImage edit form errors: %s", form.errors)
            messages.error(request, "Failed to update batch. Check form for errors.")

    else:
        form = SiteProjectImageForm(instance=image_obj, user=request.user)

    return render(request, "sitemanage/site_project_image_form.html", {
        "form": form,
        "page_title": f"Edit Project Image Batch - {image_obj.figure_name}",
        "image": batch_images,
    })



@login_required
@permission_required("sitemanage.delete_siteprojectimage", raise_exception=True)
def site_project_image_delete(request, pk):
    # Get the selected image
    image_obj = get_object_or_404(
        filter_by_allowed_projects(SiteProjectImage.objects.filter(is_active=True), request.user),
        pk=pk
    )

    # Find all images in the same batch (project + figure_name + image_date)
    batch_images = SiteProjectImage.objects.filter(
        project=image_obj.project,
        activity=image_obj.activity,
        figure_name=image_obj.figure_name,
        image_date=image_obj.image_date,
        is_active=True
    )

    if request.method == "POST":
        # Soft-delete all images in the batch
        batch_images.update(is_active=False)
        messages.success(request, f'All images for "{image_obj.figure_name}" in project "{image_obj.project.project_name}" on {image_obj.image_date} were deleted successfully.')
        return redirect("sitemanage:site_project_image_list")

    return render(request, "sitemanage/site_project_image_confirm_delete.html", {
        "image_obj": image_obj,
        "page_title": f'Delete Project Image: {image_obj.figure_name}',
    })

