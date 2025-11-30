from django.shortcuts import render, redirect, get_object_or_404
from customers.models import Customer
from .models import Ledger
from collections import defaultdict
from decimal import Decimal 

# ✅ Add Ledger
def add_ledger(request, customer_id=None):
    customers = Customer.objects.all()
    selected_customer = None

    if customer_id:
        selected_customer = get_object_or_404(Customer, id=customer_id)

    if request.method == "POST":
        customer_id = request.POST.get("customer") or customer_id
        date = request.POST.get("date")
        debit = request.POST.get("debit") or 0
        credit = request.POST.get("credit") or 0
        details = request.POST.get("details")

        customer = get_object_or_404(Customer, id=customer_id)

        Ledger.objects.create(
            customer=customer,
            date=date,
            debit=Decimal(debit),
            credit=Decimal(credit),
            description=details,
        )

        return redirect("ledger:list_ledger")

    return render(request, "ledger/add_ledger.html", {
        "customers": customers,
        "selected_customer": selected_customer,
    })


# ✅ List Ledger (Grouped by Customer)
def list_ledger(request):
    ledgers = Ledger.objects.select_related("customer").order_by("customer__name", "date", "id")

    grouped_ledgers = defaultdict(list)
    customer_balances = {}

    for ledger in ledgers:
        cust = ledger.customer

        if cust not in customer_balances:
            customer_balances[cust] = 0

        # Update running balance
        customer_balances[cust] += float(ledger.debit or 0) - float(ledger.credit or 0)

        grouped_ledgers[cust].append({
            "ledger": ledger,
            "balance": customer_balances[cust],
        })

    ledger_summary = []
    for cust, entries in grouped_ledgers.items():
        ledger_summary.append({
            "customer": cust,
            "entries": entries,
            "final_balance": customer_balances[cust],
        })

    return render(request, "ledger/list_ledger.html", {
        "ledger_summary": ledger_summary,
    })


# ✅ Pay Ledger (Credit entry for payment)
def pay_ledger(request):
    customers = Customer.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get("customer")
        date = request.POST.get("date")
        credit = request.POST.get("credit") or 0
        details = request.POST.get("details")

        customer = get_object_or_404(Customer, id=customer_id)

        Ledger.objects.create(
            customer=customer,
            date=date,
            debit=Decimal("0"),
            credit=Decimal(credit),
            description=details,
        )

        return redirect("ledger:list_ledger")

    return render(request, "ledger/pay_ledger.html", {"customers": customers})


# ✅ Redirect helper (used when adding from Customer page)
def open_add_ledger(request, customer_id):
    return redirect("ledger:add_ledger_with_customer", customer_id=customer_id)
