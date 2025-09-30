from django.db import models
from customers.models import Customer
from products.models import Product

class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=[("cash", "Cash"), ("bank", "Bank")], default="cash")
    total_quantity = models.PositiveIntegerField(default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    receiving_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer}"
    
    @property
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def grand_total(self):
        return sum(item.quantity * item.price for item in self.items.all())

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.price
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


   


