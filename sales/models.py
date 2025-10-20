from django.db import models
from customers.models import Customer
from products.models import Product


class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    total_quantity = models.PositiveIntegerField(default=0)
    grand_total = models.FloatField(default=0)
    receiving_amount = models.FloatField(default=0)
    remaining_amount = models.FloatField(default=0)

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.name if self.customer else 'Unknown'}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(default=0)
    total = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        # ✅ Automatically calculate total for each item
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
