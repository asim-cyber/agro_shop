from django.shortcuts import render, redirect
from .models import Customer
from .forms import CustomerForm

# Add Customer
def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customers:list_customers')
    else:
        form = CustomerForm()
    return render(request, 'customers/add_customer.html', {'form': form})


# List Customers
def list_customers(request):
    customers = Customer.objects.all()
    return render(request, 'customers/list_customers.html', {'customers': customers})
