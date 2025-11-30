from django.db import models
from django.utils import timezone


class Category(models.Model):
    """Product Category"""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Main Product Model"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity = models.PositiveIntegerField(default=0)
    available_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="product_images/", blank=True, null=True)
    added_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def update_stock(self):
        """Update available_quantity automatically based on StockIn and StockOut"""
        stock_in = sum(s.quantity for s in self.stockins.all())
        stock_out = sum(s.quantity for s in self.stockouts.all())
        self.total_quantity = stock_in
        self.available_quantity = stock_in - stock_out
        self.save()

    @property
    def is_in_stock(self):
        """Check product availability"""
        return self.available_quantity > 0


class StockIn(models.Model):
    """When product stock is added (Purchase)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stockins")
    quantity = models.PositiveIntegerField()
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    selling_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Selling % margin"
    )
    buying_price_per_item = models.DecimalField(max_digits=10, decimal_places=2)
    buying_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Buying % margin"
    )
    order_date = models.DateField(default=timezone.now)

    @property
    def total_amount(self):
        return self.quantity * self.price_per_item

    @property
    def total_buying_amount(self):
        return self.quantity * self.buying_price_per_item

    def save(self, *args, **kwargs):
        """Auto-update product stock when stock-in is added"""
        super().save(*args, **kwargs)
        self.product.update_stock()

    def __str__(self):
        return f"{self.product.name} - {self.quantity} added"


class StockOut(models.Model):
    """When product stock is sold or removed"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stockouts")
    quantity = models.PositiveIntegerField()
    date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        """Auto-update product stock when stock-out is created"""
        super().save(*args, **kwargs)
        self.product.update_stock()

    def __str__(self):
        return f"{self.product.name} - {self.quantity} out"
