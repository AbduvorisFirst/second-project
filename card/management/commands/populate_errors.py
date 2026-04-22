from django.core.management.base import BaseCommand
from card.models import Error

class Command(BaseCommand):
    help = 'Populate predefined error messages'

    def handle(self, *args, **kwargs):
        errors_data = [
            {"code": 32700, "en": "Ext id must be unique", "ru": "Ext id должен быть уникальным", "uz": "Ext id noyob bo'lishi kerak"},
            {"code": 32701, "en": "Ext id already exists", "ru": "Ext id уже существует", "uz": "Ext id allaqachon mavjud"},
            {"code": 32702, "en": "Balance is not enough", "ru": "Недостаточно средств", "uz": "Hisobda mablag‘ yetarli emas"},
            {"code": 32703, "en": "SMS service is not bind", "ru": "SMS сервис не подключен", "uz": "SMS xizmati ulanmagan"},
            {"code": 32704, "en": "Card expiry is not valid", "ru": "Срок действия карты недействителен", "uz": "Karta amal qilish muddati noto‘g‘ri"},
            {"code": 32705, "en": "Card is not active", "ru": "Карта неактивна", "uz": "Karta faol emas"},
            {"code": 32706, "en": "Unknown error occurred", "ru": "Произошла неизвестная ошибка", "uz": "Noma’lum xatolik yuz berdi"},
            {"code": 32707, "en": "Currency not allowed except 860, 643, 840", "ru": "Разрешены только валюты 860, 643, 840", "uz": "Faqat 860, 643, 840 valyutalari ruxsat etilgan"},
            {"code": 32708, "en": "Amount is greater than allowed", "ru": "Сумма превышает допустимую", "uz": "Miqdor ruxsat etilgan chegaradan katta"},
            {"code": 32709, "en": "Amount is small", "ru": "Сумма слишком мала", "uz": "Miqdor juda kichik"},
            {"code": 32710, "en": "OTP expired", "ru": "OTP истек", "uz": "OTP muddati tugagan"},
            {"code": 32711, "en": "Count of try is reached", "ru": "Превышено количество попыток", "uz": "Urinishlar soni tugadi"},
            {"code": 32712, "en": "OTP is wrong, left try count is 2", "ru": "Неверный OTP, осталось 2 попытки", "uz": "Noto‘g‘ri OTP, yana 2 urinish qoldi"},
            {"code": 32713, "en": "Method is not allowed", "ru": "Метод не разрешён", "uz": "Usulga ruxsat berilmagan"},
            {"code": 32714, "en": "Method not found", "ru": "Метод не найден", "uz": "Usul topilmadi"},
        ]

        count = 0
        for data in errors_data:
            obj, created = Error.objects.get_or_create(
                code=data['code'],
                defaults={'en': data['en'], 'ru': data['ru'], 'uz': data['uz']}
            )
            if created:
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully added {count} new error codes.'))