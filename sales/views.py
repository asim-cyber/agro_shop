from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

from .models import Invoice, InvoiceItem
from products.models import Product
from customers.models import Customer


# ✅ Create Invoice
def create_invoice(request):
    products = Product.objects.all()
    customers = Customer.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get("customer")
        payment_method = request.POST.get("payment_method")
        receiving_amount = float(request.POST.get("receiving_amount") or 0)

        customer = get_object_or_404(Customer, id=customer_id)

        # Create empty invoice first
        invoice = Invoice.objects.create(
            customer=customer,
            date=timezone.now(),
            payment_method=payment_method,
            receiving_amount=receiving_amount,
        )

        product_ids = request.POST.getlist("product_id[]")
        quantities = request.POST.getlist("quantity[]")
        prices = request.POST.getlist("price[]")

        total_qty = 0
        grand_total = 0

        for i in range(len(product_ids)):
            product = Product.objects.get(id=product_ids[i])
            qty = int(quantities[i])
            price = float(prices[i])
            total = qty * price

            # Create item
            InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                quantity=qty,
                price=price,
                total=total,
            )

            total_qty += qty
            grand_total += total

            # Optional: reduce product stock
            if hasattr(product, "stock"):
                product.stock = max(product.stock - qty, 0)
                product.save()

        # ✅ Save totals after all items are added
        invoice.total_quantity = total_qty
        invoice.grand_total = grand_total
        invoice.remaining_amount = grand_total - receiving_amount
        invoice.save()

        return redirect("sales:invoice_detail", invoice_id=invoice.id)

    return render(request, "sales/create_invoice.html", {"customers": customers, "products": products})


# ✅ List Invoices
def list_invoices(request):
    invoices = Invoice.objects.all().order_by("-date")
    return render(request, "sales/list_invoices.html", {"invoices": invoices})


# ✅ Invoice Detail
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = invoice.items.all()
    return render(request, "sales/invoice_detail.html", {"invoice": invoice, "items": items})


# ✅ Print Invoice (PDF)
def print_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    items = invoice.items.all()

    total_quantity = sum(item.quantity for item in items)
    grand_total = sum(item.total for item in items)

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
    p.drawString(margin_left, y_info - 6 * mm, f"Contact: {getattr(invoice.customer, 'contact', '')}")
    p.drawString(margin_left, y_info - 12 * mm, f"Payment: {invoice.payment_method}")
    p.drawString(margin_left, y_info - 18 * mm, f"Invoice Date: {invoice.date.strftime('%Y-%m-%d %H:%M')}")
    p.drawString(margin_left, y_info - 24 * mm, f"Invoice #: {invoice.id}")

    # Table: Items
    data = [["Item", "Qty", "Price", "Total"]]
    for item in items:
        data.append([
            item.product.name,
            str(item.quantity),
            f"{item.price:.2f}",
            f"{item.total:.2f}",
        ])

    table = Table(data, colWidths=[70 * mm, 25 * mm, 30 * mm, 35 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    table.wrapOn(p, width, height)
    table.drawOn(p, margin_left, y_info - 90 * mm)

    # Totals Table
    totals_data = [
        ["Total Quantity", total_quantity],
        ["Grand Total", f"{grand_total:.2f}"],
        ["Receiving Amount", f"{invoice.receiving_amount:.2f}"],
        ["Remaining Amount", f"{invoice.remaining_amount:.2f}"],
    ]

    totals_table = Table(totals_data, colWidths=[60 * mm, 40 * mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    totals_table.wrapOn(p, width, height)
    totals_table.drawOn(p, margin_left, y_info - 150 * mm)

    # Footer
    p.setFont("Helvetica-Oblique", 11)
    p.drawCentredString(width / 2, 25 * mm, "Thank you for your business!")

    p.showPage()
    p.save()
    buffer.seek(0)

    return HttpResponse(buffer, content_type='application/pdf')
