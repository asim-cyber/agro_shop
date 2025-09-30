from django.db import models

class DailyLog(models.Model):
    date = models.DateField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"Daily Log {self.date}"

class MonthlyLog(models.Model):
    month = models.CharField(max_length=20)  # e.g. "September 2025"
    summary = models.TextField()

    def __str__(self):
        return f"Monthly Log {self.month}"
