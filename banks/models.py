from django.db import models

class Bank(models.Model):
    name = models.CharField(max_length=150, unique=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name
