from django.db.models import Count
from projects.models import Project
from sitemanage.models import Activity, SiteVisitor


def build_dashboard_context(user):
    is_super = user.is_superuser

    # Projects
    projects = Project.objects.filter(is_active=True)
    if not is_super:
        projects = projects.filter(participants__user=user).distinct()

    # Activities
    activities = Activity.objects.filter(is_active=True)
    if not is_super:
        activities = activities.filter(project__participants__user=user).distinct()

    # Visitors
    visitors = SiteVisitor.objects.filter(is_active=True)
    if not is_super:
        visitors = visitors.filter(project__participants__user=user).distinct()

    # Aggregate activity counts per status
    activity_stats = activities.values("status").annotate(count=Count("id"))

    # Calculate totals including Pending
    total_activities = activities.count()
    completed_all = activities.filter(status="Completed").count()
    in_progress_all = activities.filter(status="In Progress").count()
    delayed_all = activities.filter(status="Delayed").count()
    pending_all = total_activities - (completed_all + in_progress_all + delayed_all)

    # Create status_counts dict
    status_counts = {a["status"]: a["count"] for a in activity_stats}
    if pending_all > 0:
        status_counts["Pending"] = pending_all

    activity_labels = list(status_counts.keys())
    activity_counts = list(status_counts.values())

    # Combine label & count for easier chart legend
    activity_data = [{"label": k, "count": v} for k, v in status_counts.items()]

    # Projects Overview
    projects_overview = []
    for project in projects:
        project_activities = activities.filter(project=project)
        total = project_activities.count()

        completed = project_activities.filter(status="Completed").count()
        in_progress = project_activities.filter(status="In Progress").count()
        delayed = project_activities.filter(status="Delayed").count()
        pending = total - (completed + in_progress + delayed)

        completion_rate = round((completed / total) * 100, 1) if total else 0

        projects_overview.append({
            "id": project.id,
            "name": project.project_name,
            "total_activities": total,

            "completed": completed,
            "in_progress": in_progress,
            "delayed": delayed,
            "pending": pending,

            "completion_rate": completion_rate,

            "completed_pct": completion_rate,
            "in_progress_pct": round((in_progress / total) * 100, 1) if total else 0,
            "delayed_pct": round((delayed / total) * 100, 1) if total else 0,
            "pending_pct": round((pending / total) * 100, 1) if total else 0,

            "activities": list(project_activities.values("id", "name", "status")),
        })

    # Auto-sort projects: most delayed first, then lowest completion
    projects_overview.sort(key=lambda p: (-p["delayed"], p["completion_rate"]))

    return {
        "total_projects": projects.count(),
        "total_activities": total_activities,
        "total_visitors": visitors.count(),
        "completion_rate": round((completed_all / total_activities) * 100, 1) if total_activities else 0,

        "activity_labels": activity_labels,
        "activity_counts": activity_counts,
        "activity_data": activity_data,  # for chart legend

        "projects_overview": projects_overview,

        "reports_children": {
            "project": is_super or user.has_perm("reports.view_projectreport"),
            "progress": is_super or user.has_perm("reports.view_projectprogress"),
            "finance": is_super or user.has_perm("reports.view_financereport"),
            "quality": is_super or user.has_perm("reports.view_qualityreport"),
            "resources": is_super or user.has_perm("reports.view_resourcesreport"),
        },
    }
