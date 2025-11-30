from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from customers.models import Customer
from products.models import Product
from .models import Invoice, InvoiceItem
from ledger.models import Ledger  # ✅ Import from ledger app


# ✅ CREATE INVOICE
def create_invoice(request):
    customers = Customer.objects.all()
    products = Product.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get("customer")
        payment_method = request.POST.get("payment_method")
        receiving_amount_raw = request.POST.get("receiving_amount", "0")
        product_ids = request.POST.getlist("product_id[]")
        quantities = request.POST.getlist("quantity[]")
        prices = request.POST.getlist("price[]")

        # Validate customer
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            messages.error(request, "Invalid customer selected.")
            return redirect("sales:create_invoice")

        # Convert receiving amount safely
        try:
            receiving_amount = Decimal(receiving_amount_raw or "0")
        except (InvalidOperation, TypeError):
            receiving_amount = Decimal("0")

        if not product_ids:
            messages.error(request, "Please add at least one product to the invoice.")
            return redirect("sales:create_invoice")

        try:
            with transaction.atomic():
                # Create invoice
                invoice = Invoice.objects.create(
                    customer=customer,
                    payment_method=payment_method,
                    receiving_amount=receiving_amount,
                    date=timezone.now(),
                )

                # Add products to invoice
                for pid, qty_raw, price_raw in zip(product_ids, quantities, prices):
                    product = Product.objects.get(id=pid)
                    qty = int(qty_raw)
                    price = Decimal(price_raw)
                    total = qty * price

                    if product.available_quantity < qty:
                        raise ValueError(f"Not enough stock for {product.name}")

                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=product,
                        quantity=qty,
                        price=price,
                        total=total,
                    )

                # Update totals after adding items
                invoice.update_totals()

                # ✅ Auto-create ledger if remaining amount exists
                if invoice.remaining_amount > 0:
                    Ledger.objects.create(
                        customer=customer,
                        debit=invoice.remaining_amount,
                        description=f"Remaining amount from Invoice #{invoice.id}",
                    )

        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect("sales:create_invoice")

        messages.success(request, f"Invoice #{invoice.id} created successfully!")
        return redirect("sales:invoice_detail", invoice_id=invoice.id)

    return render(request, "sales/create_invoice.html", {
        "customers": customers,
        "products": products
    })


# ✅ LIST INVOICES
def list_invoices(request):
    invoices = Invoice.objects.all().order_by("-date")
    return render(request, "sales/list_invoices.html", {"invoices": invoices})


# ✅ INVOICE DETAIL
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = invoice.items.all()
    return render(request, "sales/invoice_detail.html", {"invoice": invoice, "items": items})


# ✅ PRINT INVOICE
def print_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    items = invoice.items.all()

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin_left = 25 * mm
    top_y = height - 30 * mm

    # Header
    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, top_y, "🌿 Agro Shop 🌿")
    p.setFont("Helvetica", 11)
    p.drawCentredString(width / 2, top_y - 6 * mm, "123 Main Road, Quetta | Phone: 0300-1234567")

    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, top_y - 20 * mm, "INVOICE")

    # Customer Info
    y_info = top_y - 35 * mm
    p.setFont("Helvetica", 11)
    p.drawString(margin_left, y_info, f"Customer: {invoice.customer.name}")
    p.drawString(margin_left, y_info - 6 * mm, f"Payment: {invoice.payment_method}")
    p.drawString(margin_left, y_info - 12 * mm, f"Invoice #: {invoice.id}")
    p.drawString(margin_left, y_info - 18 * mm, f"Date: {invoice.date.strftime('%Y-%m-%d %H:%M')}")

    # Table of Items
    data = [["Product", "Qty", "Price", "Total"]]
    for item in items:
        data.append([item.product.name, str(item.quantity), f"{item.price:.2f}", f"{item.total:.2f}"])

    table = Table(data, colWidths=[70 * mm, 25 * mm, 30 * mm, 35 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    table.wrapOn(p, width, height)
    table.drawOn(p, margin_left, y_info - 90 * mm)

    # Totals
    totals_data = [
        ["Total Quantity", invoice.total_quantity],
        ["Grand Total", f"{invoice.grand_total:.2f}"],
        ["Received", f"{invoice.receiving_amount:.2f}"],
        ["Remaining", f"{invoice.remaining_amount:.2f}"],
    ]
    totals_table = Table(totals_data, colWidths=[60 * mm, 40 * mm])
    totals_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ]))
    totals_table.wrapOn(p, width, height)
    totals_table.drawOn(p, margin_left, y_info - 150 * mm)

    p.setFont("Helvetica-Oblique", 11)
    p.drawCentredString(width / 2, 25 * mm, "Thank you for your business!")

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")


# ✅ CUSTOMER LEDGER VIEW
def customer_ledger(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    ledgers = customer.ledgers.all().order_by('-date')
    return render(request, "sales/customer_ledger.html", {"customer": customer, "ledgers": ledgers})
