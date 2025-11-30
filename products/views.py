from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Category, Product, StockIn, StockOut
from .forms import CategoryForm, ProductForm, StockInForm, StockOutForm


# ---------------- CATEGORY ---------------- #
def add_category(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully!")
            return redirect("products:list_products")
    else:
        form = CategoryForm()
    return render(request, "products/add_category.html", {"form": form})


# ---------------- PRODUCT ---------------- #
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect("products:list_products")
    else:
        form = ProductForm()
    return render(request, "products/add_product.html", {"form": form})


def list_products(request):
    products = Product.objects.all()
    return render(request, "products/list_products.html", {"products": products})


def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect("products:list_products")
    else:
        form = ProductForm(instance=product)
    return render(request, "products/update_product.html", {"form": form, "product": product})


# ---------------- STOCK IN ---------------- #
def stock_in_list(request, product_id):
    """Show stock in history for a product"""
    product = get_object_or_404(Product, id=product_id)
    stockins = StockIn.objects.filter(product=product).order_by("-order_date")
    return render(
        request,
        "products/stock_in_list.html",
        {"product": product, "stockins": stockins},
    )

def add_stock_in(request, product_id):
    """Add new stock entry for a product"""
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = StockInForm(request.POST)
        if form.is_valid():
            stock_in = form.save(commit=False)
            stock_in.product = product

            # ✅ Ensure positive quantity
            if stock_in.quantity <= 0:
                messages.error(request, "Quantity must be greater than 0.")
                return redirect("products:stock_in_list", product_id=product.id)

            # ✅ Ensure numeric fields are not None
            product.total_quantity = product.total_quantity or 0
            product.available_quantity = product.available_quantity or 0

            # ✅ Safely increase stock
            new_available = product.available_quantity + stock_in.quantity
            if new_available < 0:  # just to be sure — though it shouldn't
                new_available = 0

            product.total_quantity += stock_in.quantity
            product.available_quantity = new_available
            product.save()

            # ✅ Save stock record
            stock_in.save()

            messages.success(request, "Stock added successfully!")
            return redirect("products:stock_in_list", product_id=product.id)
        else:
            messages.error(request, "Invalid form data.")
    else:
        form = StockInForm()

    return render(request, "products/add_stock_in.html", {"form": form, "product": product})




# ---------------- STOCK OUT ---------------- #
def stock_out_list(request, product_id):
    """Show stock out history for a product"""
    product = get_object_or_404(Product, id=product_id)
    stockouts = StockOut.objects.filter(product=product).order_by("-date")
    return render(
        request,
        "products/stock_out_list.html",
        {"product": product, "stockouts": stockouts},
    )


def add_stock_out(request, product_id):
    """Add new stock out entry for a product"""
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = StockOutForm(request.POST)
        if form.is_valid():
            stock_out = form.save(commit=False)
            stock_out.product = product

            # ✅ Ensure numeric fields are not None
            product.available_quantity = product.available_quantity or 0

            # ✅ Ensure positive quantity
            if stock_out.quantity <= 0:
                messages.error(request, "Quantity must be greater than 0.")
                return redirect("products:stock_out_list", product_id=product.id)

            # ✅ Check stock before reducing
            if stock_out.quantity <= product.available_quantity:
                product.available_quantity -= stock_out.quantity
                product.save()
                stock_out.save()
                messages.success(request, "Stock out recorded successfully!")
                return redirect("products:stock_out_list", product_id=product.id)
            else:
                messages.error(request, "Not enough stock available!")
        else:
            messages.error(request, "Invalid form data.")
    else:
        form = StockOutForm()

    return render(request, "products/add_stock_out.html", {"form": form, "product": product})
