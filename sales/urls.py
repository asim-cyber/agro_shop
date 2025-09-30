from django.urls import path
from . import views

app_name = "sales"

urlpatterns = [
    path("create/", views.create_invoice, name="create_invoice"),
    path("list/", views.list_invoices, name="list_invoices"),
    path("<int:invoice_id>/", views.invoice_detail, name="invoice_detail"),
    path('<int:invoice_id>/print/', views.print_invoice, name='print_invoice'),

]



