from django.urls import path
from . import views

app_name = "banks"

urlpatterns = [
    path('add/', views.add_bank, name='add_bank'),
    path('list/', views.list_banks, name='list_banks'),
]
