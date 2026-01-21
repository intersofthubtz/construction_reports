from django.db.models import Avg, Max
from django.db.models.functions import TruncWeek
from projects.models import Project


from .models import (
    Activity,
    ProgressLog,
    SiteVisitor,
    SiteProjectImage
)


def get_allowed_projects(user):
    """Return queryset of projects the user is allowed to see."""
    if user.is_superuser or user.is_staff:
        return Project.objects.filter(is_active=True)
    return Project.objects.filter(
        is_active=True,
        participants__user=user,
        participants__is_active=True
    ).distinct()
    

def get_project_site_overview(projects):
    """
    Returns high-level overview data per project
    """
    overview = []

    for project in projects:
        activities = Activity.objects.filter(
            project=project,
            is_active=True
        )

        progress_avg = activities.aggregate(
            avg=Avg("progress_percent")
        )["avg"] or 0

        overview.append({
            "project": project,

            # Activity stats
            "total_activities": activities.count(),
            "completed": activities.filter(status=Activity.STATUS_COMPLETED).count(),
            "in_progress": activities.filter(status=Activity.STATUS_IN_PROGRESS).count(),
            "delayed": activities.filter(status=Activity.STATUS_DELAYED).count(),

            # Progress
            "overall_progress": round(progress_avg, 1),

            # Latest updates
            "last_activity_update": activities.aggregate(
                last=Max("updated_at")
            )["last"],

            # Visitors & media
            "visitor_docs": SiteVisitor.objects.filter(
                project=project,
                is_active=True
            ).count(),

            "images_count": SiteProjectImage.objects.filter(
                project=project,
                is_active=True
            ).count(),

            "latest_image_date": SiteProjectImage.objects.filter(
                project=project,
                is_active=True
            ).aggregate(last=Max("image_date"))["last"],
        })

    return overview


def get_weekly_progress_trend(project):
    """
    Returns latest progress per week for a project
    """
    logs = (
        ProgressLog.objects
        .filter(
            activity__project=project,
            is_active=True
        )
        .annotate(week=TruncWeek("date"))
        .values("week")
        .annotate(progress=Max("progress_percent"))
        .order_by("week")
    )

    return [
        {
            "week": log["week"].strftime("%Y-%m-%d"),
            "progress": log["progress"],
        }
        for log in logs if log["week"]
    ]
