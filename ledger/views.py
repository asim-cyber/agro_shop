from django.shortcuts import render, redirect, get_object_or_404
from customers.models import Customer
from .models import Ledger


# ✅ Add Ledger (can work with or without customer_id)
def add_ledger(request, customer_id=None):
    customers = Customer.objects.all()
    selected_customer = None

    # If coming from /ledger/customer/<id>/ — preselect that customer
    if customer_id:
        selected_customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        customer_id = request.POST.get("customer") or customer_id
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
            description=details,
        )
        return redirect("ledger:list_ledger")

    return render(request, "ledger/add_ledger.html", {
        "customers": customers,
        "selected_customer": selected_customer,
    })


# ✅ List Ledger
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

    return render(request, "ledger/list_ledger.html", {
        "ledger_entries_with_balance": ledger_entries_with_balance
    })


# ✅ Pay Ledger (credit only)
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
            debit_amount=0,
            credit_amount=credit,
            description=details,
        )
        return redirect("ledger:list_ledger")

    return render(request, "ledger/pay_ledger.html", {"customers": customers})


# ✅ Redirect Customer Ledger Button to Add Ledger Page
def open_add_ledger(request, customer_id):
    """Redirect customer ledger button to the add_ledger page with that customer pre-selected."""
    return redirect("ledger:add_ledger_with_customer", customer_id=customer_id)
