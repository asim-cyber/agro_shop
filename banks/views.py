from django.shortcuts import render, redirect
from .models import Bank
from .forms import BankForm

def add_bank(request):
    if request.method == "POST":
        form = BankForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('banks:list_banks')
    else:
        form = BankForm()
    return render(request, 'banks/add_bank.html', {'form': form})

def list_banks(request):
    banks = Bank.objects.all()
    return render(request, 'banks/list_banks.html', {'banks': banks})
