from django.urls import path
from . import views

app_name = "expenses"

urlpatterns = [
    path("add/", views.add_expense, name="add_expense"),
    path("list/", views.list_expenses, name="list_expenses"),
    path("update/<int:pk>/", views.update_expense, name="update_expense"),  # 👈
    path("delete/<int:pk>/", views.delete_expense, name="delete_expense"),  # 👈
]
