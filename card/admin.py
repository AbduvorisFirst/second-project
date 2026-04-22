from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from import_export.formats.base_formats import XLSX, CSV
import openpyxl

from .models import Card
from .utils import format_card, format_phone, card_mask, phone_mask
from .resource import CardRecource


@admin.register(Card)
class CardAdmin(ImportExportModelAdmin):  # ← вот здесь было admin.ModelAdmin
    resource_classes = (CardRecource,)

    list_display = ['get_masked_card', 'get_masked_phone', 'formatted_balance', 'colored_status', 'expire']
    list_filter = ['status', 'expire']
    search_fields = ['card_number', 'phone']
    list_per_page = 20

    formats = [XLSX, CSV]

    change_list_template = "admin/card/card/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-excel/', self.admin_site.admin_view(self.custom_import_excel), name='import_excel'),
        ]
        return custom_urls + urls

    def custom_import_excel(self, request):
        if request.method == "POST":
            excel_file = request.FILES.get("excel_file")
            if not excel_file:
                messages.error(request, "Файл не выбран!")
                return redirect("..")
            try:
                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active
                created_count = 0
                errors = []

                for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                    try:
                        raw_card   = row[0]
                        raw_expire = row[1]
                        raw_phone  = row[2]
                        raw_status = str(row[3]).lower().strip() if row[3] else 'inactive'
                        raw_balance = row[4]

                        clean_card  = format_card(raw_card)
                        clean_phone = format_phone(raw_phone)

                        if len(clean_card) != 16:
                            raise ValueError(f"Неверная длина карты: {clean_card}")

                        if raw_status not in ['active', 'inactive', 'expired']:
                            raw_status = 'inactive'

                        from decimal import Decimal, ROUND_DOWN
                        clean_balance = Decimal(str(raw_balance).replace(',', '')).quantize(
                            Decimal('0.01'), rounding=ROUND_DOWN
                        ) if raw_balance else Decimal('0.00')

                        Card.objects.update_or_create(
                            card_number=clean_card,
                            defaults=dict(
                                expire=raw_expire,
                                phone=clean_phone,
                                status=raw_status,
                                balance=clean_balance,
                            )
                        )
                        created_count += 1
                    except Exception as e:
                        errors.append(f"Строка {row_idx}: {str(e)}")

                if errors:
                    messages.warning(request, f"Импорт завершен с ошибками ({len(errors)} строк).")
                    for err in errors[:5]:
                        messages.error(request, err)
                if created_count > 0:
                    messages.success(request, f"✅ Успешно импортировано: {created_count} карт.")
                return redirect("..")
            except Exception as e:
                messages.error(request, f"Критическая ошибка: {str(e)}")
                return redirect("..")

        context = dict(self.admin_site.each_context(request), title="Импорт карт из Excel")
        return render(request, "admin/excel_form.html", context)

    @admin.display(description="Karta raqami")
    def get_masked_card(self, obj):
        return card_mask(obj.card_number)

    @admin.display(description="Telefon")
    def get_masked_phone(self, obj):
        return phone_mask(obj.phone)

    @admin.display(description='Balans (UZS)', ordering='balance')
    def formatted_balance(self, obj):
        if obj.balance is not None:
            return f"{obj.balance:,.2f}".replace(',', ' ')
        return "0.00"

    @admin.display(description='Status', ordering='status')
    def colored_status(self, obj):
        colors = {'active': 'green', 'expired': 'red', 'inactive': 'orange'}
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.status.upper())


