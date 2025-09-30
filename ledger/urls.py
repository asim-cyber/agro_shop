from django.urls import path
from . import views

app_name = "ledger"  # important

urlpatterns = [
    path("add/", views.add_ledger, name="add_ledger"),          # ✅ add ledger entry
    path("list/", views.list_ledger, name="list_ledger"),       # ✅ ledger list
    path("", views.list_ledger, name="list_ledger"),            # optional: root shows list too
    path("pay/", views.pay_ledger, name="pay_ledger"), 
]

