from django.shortcuts import render, redirect, get_object_or_404
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
    customers = Customer.objects.all().order_by('-id')  # newest first
    return render(request, 'customers/list_customers.html', {'customers': customers})


# Update Customer
def update_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customers:list_customers')
    else:
        form = CustomerForm(instance=customer)
    
    return render(request, 'customers/add_customer.html', {''
    'form': form,
    'customer': customer,
    'title' : 'Update Customer',
    'button_text' : 'Update Customer'
    })
