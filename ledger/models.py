from django.db import models
from customers.models import Customer
from decimal import Decimal


class Ledger(models.Model):
    ENTRY_TYPE_CHOICES = [
        ('debit', 'Debit'),
        ('credit', 'Credit'),
        ('installment', 'Installment'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    entry_type = models.CharField(max_length=15, choices=ENTRY_TYPE_CHOICES, blank=True, null=True)

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        """Automatically detect entry type and update running balance."""
        if self.debit > 0 and self.credit == 0:
            self.entry_type = 'debit'
        elif self.credit > 0 and self.debit == 0:
            self.entry_type = 'credit'
        elif self.debit > 0 and self.credit > 0:
            self.entry_type = 'installment'
        else:
            self.entry_type = None

        last_entry = (
            Ledger.objects.filter(customer=self.customer)
            .exclude(pk=self.pk)
            .order_by('-date', '-id')
            .first()
        )

        previous_balance = last_entry.balance if last_entry else Decimal('0.00')
        self.balance = previous_balance + Decimal(self.debit) - Decimal(self.credit)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.name if self.customer else 'Unknown'} - {self.entry_type}: {self.balance}"
