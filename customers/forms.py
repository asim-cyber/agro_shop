from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name','father_name','cnic','mobile', 'email', 'address', 'resident', 'city']
