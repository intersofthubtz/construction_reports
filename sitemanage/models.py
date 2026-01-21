import os
from django.utils.text import slugify
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from projects.models import Project
from setup.models import WorkCategory


# ---------------------------
# SITE MANAGEMENT
# ---------------------------
class SiteManage(models.Model):
    #dum model no database created 
    site_id = models.CharField(max_length=100, unique=True)
    site_name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        managed = False
        permissions = [
            ("access_sitemanage", "Can access site management"),
        ]

    def __str__(self):
        return self.site_name


# ---------------------------
# ACTIVITY
# ---------------------------
class Activity(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_COMPLETED = 'Completed'
    STATUS_DELAYED = 'Delayed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_DELAYED, 'Delayed'),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    category = models.ForeignKey(
        WorkCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    planned_start = models.DateField()
    planned_end = models.DateField()

    actual_start = models.DateField(null=True, blank=True)
    actual_end = models.DateField(null=True, blank=True)

    progress_percent = models.PositiveSmallIntegerField(default=0, editable=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activities_created'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activities_updated'
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['planned_start']

    def __str__(self):
        return f"{self.project} - {self.name}"
    
    @property
    def is_delayed(self):
        return self.status == self.STATUS_DELAYED

    def clean(self):
        if self.planned_start and self.planned_end:
            if self.planned_end < self.planned_start:
                raise ValidationError({
                    "planned_end": "Planned end date cannot be before planned start date."
                })

    def save(self, *args, **kwargs):
        self.full_clean()  # Enforces clean()
        super().save(*args, **kwargs)
        


# ---------------------------
# PROGRESS LOG
# ---------------------------
class ProgressLog(models.Model):
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='progress_logs'
    )
    date = models.DateField()
    progress_percent = models.PositiveSmallIntegerField()
    remarks = models.TextField(blank=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='progress_logs_created'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date']
        constraints = [
            models.CheckConstraint(
                check=models.Q(progress_percent__gte=0, progress_percent__lte=100),
                name='progress_percent_valid'
            )
        ]

    def __str__(self):
        return f"{self.activity} → {self.progress_percent}%"

    def clean(self):
        last_log = (
            ProgressLog.objects
            .filter(activity=self.activity)
            .exclude(pk=self.pk)
            .order_by('-date', '-id')
            .first()
        )

        if last_log:
            if self.progress_percent < last_log.progress_percent:
                raise ValidationError({"progress_percent": "Progress cannot decrease."})

            if self.date < last_log.date:
                raise ValidationError({"date": "Progress date cannot go backwards."})

            if self.progress_percent == 0:
                raise ValidationError({"progress_percent": "Progress cannot return to 0."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        activity = self.activity
        activity.progress_percent = self.progress_percent

        if self.progress_percent == 100:
            activity.status = Activity.STATUS_COMPLETED
            activity.actual_end = self.date
        elif self.progress_percent > 0:
            activity.status = Activity.STATUS_IN_PROGRESS
            if not activity.actual_start:
                activity.actual_start = self.date

        if (
            activity.planned_end and
            self.date > activity.planned_end and
            self.progress_percent < 100
        ):
            activity.status = Activity.STATUS_DELAYED

        activity.save(update_fields=[
            'progress_percent',
            'status',
            'actual_start',
            'actual_end'
        ])


# ---------------------------
# SITE VISITOR
# ---------------------------
class SiteVisitor(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="site_visitors"
    )

    document_name = models.CharField(max_length=255)
    document_file = models.FileField(upload_to="site_visitors/")
    visit_date = models.DateField()

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-visit_date"]
        verbose_name = "Site Visitor"
        verbose_name_plural = "Site Visitors"

    def __str__(self):
        return f"{self.project.name} - {self.document_name}"


def project_image_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    project_slug = slugify(instance.project.project_name)
    figure_slug = slugify(instance.figure_name)
    unique_id = uuid.uuid4().hex[:8]

    filename = f"{project_slug}_{figure_slug}_{instance.image_date}_{unique_id}.{ext}"
    return os.path.join("site_images", project_slug, filename)


# ---------------------------
# SITE IMAGE 
# ---------------------------
class SiteProjectImage(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="project_images"
    )

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="activity_images"
    )

    image = models.ImageField(upload_to=project_image_upload_path)
    image_date = models.DateField()

    figure_name = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-image_date", "-created_at"]
        verbose_name = "Site Project Image"
        verbose_name_plural = "Site Project Images"

    def __str__(self):
        return f"{self.project.project_name} | {self.activity} | {self.figure_name}"