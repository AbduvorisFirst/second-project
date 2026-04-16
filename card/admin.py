from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .resource import CardRecource
from .models import Card

@admin.register(Card)
class CardAdmin(ImportExportModelAdmin):
    resource_classes = (CardRecource, )
    list_display = ['card_number', 'phone', 'balance','status','expire']
    list_filter = ['status', 'card_number', 'phone']


