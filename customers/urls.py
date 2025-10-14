from django.urls import path
from . import views

app_name = "customers"

urlpatterns = [
    path("list/", views.list_customers, name="list_customers"),
    path("add/", views.add_customer, name="add_customer"),
    path("update/<int:customer_id>/", views.update_customer, name="update_customer"),
]
