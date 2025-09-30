from django.shortcuts import render, redirect, get_object_or_404
from customers.models import Customer
from .models import Ledger

def add_ledger(request):
    customers = Customer.objects.all()
    if request.method == "POST":
        customer_id = request.POST.get("customer")
        date = request.POST.get("date")
        debit = request.POST.get("debit")
        credit = request.POST.get("credit")
        details = request.POST.get("details")

        customer = get_object_or_404(Customer, id=customer_id)

        debit = float(debit) if debit else 0
        credit = float(credit) if credit else 0

        Ledger.objects.create(
            customer=customer,
            date=date,
            debit_amount=debit,
            credit_amount=credit,
            description=details,  # make sure model field is description
        )
        return redirect("ledger:list_ledger")  # ✅ updated
    return render(request, "ledger/add_ledger.html", {"customers": customers})


def list_ledger(request):
    ledgers = Ledger.objects.all().order_by("date", "id")
    running_balance = 0
    ledger_entries_with_balance = []

    for ledger in ledgers:
        running_balance += float(ledger.debit_amount or 0) - float(ledger.credit_amount or 0)
        ledger_entries_with_balance.append({
            "ledger": ledger,
            "balance": running_balance,
        })

    return render(
        request,
        "ledger/list_ledger.html",
        {"ledger_entries_with_balance": ledger_entries_with_balance}
    )

def pay_ledger(request):
    customers = Customer.objects.all()
    if request.method == "POST":
        customer_id = request.POST.get("customer")
        date = request.POST.get("date")
        credit = request.POST.get("credit")
        details = request.POST.get("details")

        customer = get_object_or_404(Customer, id=customer_id)

        credit = float(credit) if credit else 0

        Ledger.objects.create(
            customer=customer,
            date=date,
            debit_amount=0,           # 👈 no debit
            credit_amount=credit,     # 👈 payment
            description=details
        )
        return redirect("ledger:list_ledger")
    return render(request, "ledger/pay_ledger.html", {"customers": customers})
