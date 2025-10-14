from django.urls import path
from . import views

app_name = "ledger"

urlpatterns = [
    path("add/", views.add_ledger, name="add_ledger"),  # normal add ledger
    path("add/<int:customer_id>/", views.add_ledger, name="add_ledger_with_customer"),  # from customer
    path("list/", views.list_ledger, name="list_ledger"),
    path("", views.list_ledger, name="list_ledger"),
    path("pay/", views.pay_ledger, name="pay_ledger"),
    path("customer/<int:customer_id>/", views.open_add_ledger, name="customer_ledger"),  # ledger button link
]
