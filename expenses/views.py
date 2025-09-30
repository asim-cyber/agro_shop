from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from .forms import ExpenseForm

def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("expenses:list_expenses")
    else:
        form = ExpenseForm()
    return render(request, "expenses/add_expense.html", {"form": form})

def list_expenses(request):
    expenses = Expense.objects.all()
    return render(request, "expenses/list_expenses.html", {"expenses": expenses})


def update_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            return redirect("expenses:list_expenses")
    else:
        form = ExpenseForm(instance=expense)
    return render(request, "expenses/update_expense.html", {"form": form})

def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == "POST":
        expense.delete()
        return redirect("expenses:list_expenses")
    return render(request, "expenses/delete_expense.html", {"expense": expense})
