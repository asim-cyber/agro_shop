from django import forms
from .models import DailyLog, MonthlyLog

class DailyLogForm(forms.ModelForm):
    class Meta:
        model = DailyLog
        fields = ["description"]

class MonthlyLogForm(forms.ModelForm):
    class Meta:
        model = MonthlyLog
        fields = ["month", "summary"]
