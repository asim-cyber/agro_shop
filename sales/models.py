from django.db import models, transaction
from django.utils import timezone
from decimal import Decimal
from customers.models import Customer
from products.models import Product

class Invoice(models.Model):
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('credit', 'Credit'),
        ('installment', 'Installment'),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    total_quantity = models.PositiveIntegerField(default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    receiving_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.name}"

    def update_totals(self):
        """Recalculate totals from related items safely"""
        items = self.items.all()
        self.total_quantity = sum(item.quantity for item in items)
        self.grand_total = sum(item.total for item in items)
        self.remaining_amount = max(self.grand_total - self.receiving_amount, 0)
        self.save()

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        """Automatically calculate total and reduce product stock"""
        self.total = self.quantity * self.price

        # Check stock and reduce it only on creation
        if not self.pk:
            if self.product.available_quantity < self.quantity:
                raise ValueError(f"Not enough stock for {self.product.name}")
            self.product.available_quantity -= self.quantity
            self.product.save()

        super().save(*args, **kwargs)

        # Update invoice totals
        self.invoice.update_totals()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"



class InvoiceInstallment(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="installments", on_delete=models.CASCADE)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Installment for Invoice #{self.invoice.id} - {self.amount}"


class Ledger(models.Model):
    """Ledger entry for customer outstanding balances."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="ledgers")
    invoice = models.ForeignKey("Invoice", on_delete=models.CASCADE, related_name="ledger_entries")
    date = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255, default="Outstanding balance from invoice")
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # Amount owed
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Amount paid
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Ledger - {self.customer.name} (Invoice #{self.invoice.id})"
