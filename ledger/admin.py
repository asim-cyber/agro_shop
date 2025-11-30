from django.contrib import admin
from .models import Ledger

@admin.register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    list_display = ('customer', 'date', 'entry_type', 'debit', 'credit', 'balance')
    search_fields = ('customer__name',)
