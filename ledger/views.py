from django.shortcuts import render, redirect, get_object_or_404
from customers.models import Customer
from .models import Ledger
from collections import defaultdict


# ✅ Add Ledger (works with or without preselected customer)
def add_ledger(request, customer_id=None):
    customers = Customer.objects.all()
    selected_customer = None

    # If we came from customer button, preselect the customer
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
            debit_amount=float(debit),
            credit_amount=float(credit),
            description=details,
        )

        return redirect("ledger:list_ledger")

    return render(request, "ledger/add_ledger.html", {
        "customers": customers,
        "selected_customer": selected_customer,
    })


from django.shortcuts import render
from customers.models import Customer
from .models import Ledger
from collections import defaultdict

def list_ledger(request):
    ledgers = Ledger.objects.select_related("customer").order_by("customer__name", "date", "id")

    grouped_ledgers = defaultdict(list)
    customer_balances = {}

    for ledger in ledgers:
        cust = ledger.customer

        if cust not in customer_balances:
            customer_balances[cust] = 0

        # Update balance
        customer_balances[cust] += float(ledger.debit_amount or 0) - float(ledger.credit_amount or 0)

        # Append ledger with running balance
        grouped_ledgers[cust].append({
            "ledger": ledger,
            "balance": customer_balances[cust],
        })

    # ✅ Create a helper list for easy template access
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


def list_ledger(request):
    ledgers = Ledger.objects.select_related("customer").order_by("customer__name", "date", "id")

    grouped_ledgers = defaultdict(list)
    customer_balances = {}

    for ledger in ledgers:
        cust = ledger.customer

        if cust not in customer_balances:
            customer_balances[cust] = 0

        # Update balance
        customer_balances[cust] += float(ledger.debit_amount or 0) - float(ledger.credit_amount or 0)

        # Append ledger with running balance
        grouped_ledgers[cust].append({
            "ledger": ledger,
            "balance": customer_balances[cust],
        })

    # ✅ Create a helper list for easy template access
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



# ✅ Pay Ledger (Credit Entry)
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
            debit_amount=0,
            credit_amount=float(credit),
            description=details,
        )

        return redirect("ledger:list_ledger")

    return render(request, "ledger/pay_ledger.html", {"customers": customers})


# ✅ Open Add Ledger when clicking Ledger in customer list
def open_add_ledger(request, customer_id):
    """Redirects to add ledger page with preselected customer."""
    return redirect("ledger:add_ledger_with_customer", customer_id=customer_id)
