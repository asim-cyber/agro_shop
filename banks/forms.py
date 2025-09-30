from django import forms
from .models import Bank

class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ['name', 'account_number', 'balance']
