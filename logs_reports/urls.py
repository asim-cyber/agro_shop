from django.urls import path
from . import views

app_name = "logs_reports"

urlpatterns = [
    path("daily/", views.daily_logs, name="daily_logs"),
    path("monthly/", views.monthly_logs, name="monthly_logs"),
    path("report/", views.monthly_report, name="monthly_report"),
]
