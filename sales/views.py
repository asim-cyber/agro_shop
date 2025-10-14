from django.shortcuts import render, redirect, get_object_or_404
from .models import Invoice, InvoiceItem
from products.models import Product
from customers.models import Customer
from django.utils import timezone
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet


def create_invoice(request):
    products = Product.objects.all()
    customers = Customer.objects.all()

    if request.method == "POST":
        customer_id = request.POST.get("customer")
        payment_method = request.POST.get("payment_method")
        receiving_amount = float(request.POST.get("receiving_amount", 0))

        customer = Customer.objects.filter(id=customer_id).first()
        invoice = Invoice.objects.create(
            customer=customer,
            date=timezone.now(),
            payment_method=payment_method,
            receiving_amount=receiving_amount,
        )

        total_qty, grand_total = 0, 0
        product_ids = request.POST.getlist("product_id")
        quantities = request.POST.getlist("quantity")
        prices = request.POST.getlist("price")

        for i in range(len(product_ids)):
            product = Product.objects.get(id=product_ids[i])
            qty = int(quantities[i])
            price = float(prices[i])
            total = qty * price

            InvoiceItem.objects.create(
                invoice=invoice, product=product, quantity=qty, price=price, total=total
            )

            total_qty += qty
            grand_total += total

        # ✅ Save totals
        invoice.total_quantity = total_qty
        invoice.grand_total = grand_total
        invoice.remaining_amount = grand_total - receiving_amount
        invoice.save()

        return redirect("sales:invoice_detail", invoice_id=invoice.pk)

    return render(request, "sales/create_invoice.html", {"products": products, "customers": customers})


def list_invoices(request):
    invoices = Invoice.objects.all().order_by("-date")
    return render(request, "sales/list_invoices.html", {"invoices": invoices})


def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = InvoiceItem.objects.filter(invoice=invoice)
    return render(request, "sales/invoice_detail.html", {"invoice": invoice, "items": items})


def print_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    items = invoice.items.all()
    total_quantity = sum(i.quantity for i in items)
    grand_total = sum(i.quantity * i.price for i in items)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    styles = getSampleStyleSheet()
    margin_left = 25 * mm
    top_y = height - 30 * mm

    p.setFont("Helvetica", 10)
    p.drawString(margin_left, top_y, f"Date Created: {invoice.date}")

    p.setFont("Helvetica-Bold", 20)
    p.drawCentredString(width / 2, top_y - 10 * mm, "🌿 Agro Shop 🌿")

    p.setFont("Helvetica", 11)
    p.drawCentredString(width / 2, top_y - 16 * mm, "123 Main Road, Quetta | Phone: 0300-1234567")

    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2, top_y - 30 * mm, "INVOICE")

    y_info = top_y - 45 * mm
    p.setFont("Helvetica", 11)
    p.drawString(margin_left, y_info, f"Customer Name: {invoice.customer.name}")
    p.drawString(margin_left, y_info - 6 * mm, f"Contact: {getattr(invoice.customer, 'contact', '')}")
    p.drawString(margin_left, y_info - 12 * mm, f"CNIC: {getattr(invoice.customer, 'cnic', '')}")
    p.drawString(margin_left, y_info - 18 * mm, f"Billed Date: {invoice.date}")
    p.drawString(margin_left, y_info - 24 * mm, f"Payment Type: {getattr(invoice, 'payment_method', '')}")
    p.drawString(margin_left, y_info - 30 * mm, f"Receipt No: {invoice.id}")

    data = [["Item Name", "Quantity", "Total"]]
    for item in items:
        data.append([item.product.name, item.quantity, f"{item.quantity * item.price:.2f}"])

    table = Table(data, colWidths=[80 * mm, 30 * mm, 40 * mm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    table_width, table_height = table.wrap(width, height)
    items_table_y = y_info - 70 * mm
    table.drawOn(p, margin_left, items_table_y)

    totals_data = [
        ["Total Quantity", total_quantity],
        ["Grand Total", f"{grand_total:.2f}"],
        ["Cash Type", getattr(invoice, 'payment_method', '')],
        ["Receiving Amount", getattr(invoice, 'receiving_amount', '')],
        ["Returned Amount", getattr(invoice, 'returned_amount', '')],
        ["Remaining Amount", getattr(invoice, 'remaining_amount', '')],
    ]

    totals_table = Table(totals_data, colWidths=[60 * mm, 40 * mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    totals_w, totals_h = totals_table.wrap(width, height)
    totals_y = items_table_y - table_height - 100
    totals_table.drawOn(p, margin_left, totals_y)

    p.setFont("Helvetica-Oblique", 12)
    p.drawCentredString(width / 2, 20 * mm, "Thank you for your business!")

    p.showPage()
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
