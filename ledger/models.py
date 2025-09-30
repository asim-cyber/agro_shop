from django.db import models
from customers.models import Customer


class Ledger(models.Model):
    ENTRY_TYPE_CHOICES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE , null=True, blank=True)
    date = models.DateField(auto_now_add=True, null=True, blank=True)   # Entry date
    description = models.CharField(max_length=255, null=True, blank=True)  # Short note
    entry_type = models.CharField(max_length=6, choices=ENTRY_TYPE_CHOICES, null=True, blank=True)  # debit/credit
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  # money value
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, null=True, blank=True)  # running balance
    debit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    credit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.description} ({self.entry_type}: {self.amount})"
