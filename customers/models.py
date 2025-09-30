from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    father_name = models.CharField(max_length=100, null=True, blank=True)
    cnic = models.CharField(max_length=15, null=True, blank=True, unique=True)
    mobile = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    resident = models.CharField(max_length=50, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.cnic})"



