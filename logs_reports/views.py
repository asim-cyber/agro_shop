from django.shortcuts import render, redirect
from .models import DailyLog, MonthlyLog
from .forms import DailyLogForm, MonthlyLogForm
from sales.models import Invoice
from django.db.models import Sum
from datetime import date
import json
from datetime import date
from sales.models import Invoice  # make sure this import matches your app structure


def daily_logs(request):
    if request.method == "POST":
        form = DailyLogForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("logs_reports:daily_logs")
    else:
        form = DailyLogForm()
    logs = DailyLog.objects.all()
    return render(request, "logs_reports/daily_logs.html", {"form": form, "logs": logs})


def monthly_logs(request):
    if request.method == "POST":
        form = MonthlyLogForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("logs_reports:monthly_logs")
    else:
        form = MonthlyLogForm()
    logs = MonthlyLog.objects.all()
    return render(request, "logs_reports/monthly_logs.html", {"form": form, "logs": logs})





def monthly_report(request):
    """Generate monthly sales report with totals and chart data."""
    today = date.today()

    # ✅ Get all invoices for the current month
    invoices = Invoice.objects.filter(date__year=today.year, date__month=today.month)

    # ✅ Calculate totals
    total_sales = sum(inv.grand_total for inv in invoices)
    total_quantity = sum(inv.total_quantity for inv in invoices)

    # ✅ Chart data
    chart_labels = [inv.customer.name for inv in invoices] or ["No Data"]
    chart_values = [inv.grand_total for inv in invoices] or [0]

    # ✅ Context for template
    context = {
        "invoices": invoices,
        "total_sales": total_sales,
        "total_quantity": total_quantity,
        "chart_labels": json.dumps(chart_labels),
        "chart_values": json.dumps(chart_values),
    }

    return render(request, "logs_reports/monthly_report.html", context)