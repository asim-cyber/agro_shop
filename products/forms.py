from django import forms
from .models import Category, Product, StockIn
from .models import StockOut


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class ProductForm(forms.ModelForm):
    added_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})  # 👈 shows a date picker in HTML
    )

    class Meta:   # ✅ moved inside ProductForm
        model = Product
        fields = [
            'category',
            'name',
            'price',
            'total_quantity',
            'available_quantity',
            'image',
            'added_date',
        ]


class StockInForm(forms.ModelForm):
    class Meta:
        model = StockIn
        fields = [
            "product",
            "quantity",
            "price_per_item",
            "selling_percentage",
            "buying_price_per_item",
            "buying_percentage",
            "order_date",
        ]
        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),  # user can select date
        }



class StockOutForm(forms.ModelForm):
    class Meta:
        model = StockOut
        fields = ["quantity", "date"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

