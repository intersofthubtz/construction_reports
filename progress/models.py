# from django.db import models
# from reports.models import MonthlyReport


# class WorkCategory(models.Model):
#     name = models.CharField(max_length=100)

# class WorkItem(models.Model):
#     category = models.ForeignKey(WorkCategory, on_delete=models.CASCADE)
#     description = models.TextField()

# class ProgressEntry(models.Model):
#     report = models.ForeignKey(MonthlyReport, on_delete=models.CASCADE)
#     work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE)
#     block = models.CharField(max_length=50)
#     status = models.CharField(max_length=50)
#     progress_percent = models.DecimalField(max_digits=5, decimal_places=2)
#     remarks = models.TextField(blank=True)

# class TargetProgress(models.Model):
#     report = models.ForeignKey(MonthlyReport, on_delete=models.CASCADE)
#     work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE)
#     current_progress = models.DecimalField(max_digits=5, decimal_places=2)
#     target_progress = models.DecimalField(max_digits=5, decimal_places=2)
    
