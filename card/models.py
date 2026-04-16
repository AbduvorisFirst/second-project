from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import date
from card.utility import is_luhn_valid, validate_phone, format_expire

# Holatlar uchun konstantalar
ACTIVE = 'active'
EXPIRE = 'expired'
INACTIVE = 'inactive'

class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username


class Card(models.Model):
    STATUS_CHOICES = (
        (ACTIVE, 'active'),
        (EXPIRE, 'expired'),
        (INACTIVE, 'inactive')
    )

    card_number = models.CharField(max_length=20, unique=True)
    expire = models.CharField(max_length=20, help_text="Format: MM/YY, YYYY-MM yoki MM.YYYY")
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    balance = models.DecimalField(
        max_digits=16,
        decimal_places=2,
        default=0
    )

    def clean(self):
        """Barcha maydonlarni validatsiya qilish"""
        errors = {}

        #  Karta raqamini Luhn algoritmi bo'yicha tekshirish
        if self.card_number:
            if not is_luhn_valid(self.card_number):
                errors['card_number'] = f"Karta raqami xato: {self.card_number}"

        if self.phone:
            try:
                self.phone = validate_phone(self.phone)
            except ValidationError:
                errors['phone'] = "Telefon raqami formati noto'g'ri (Masalan: 998901234567)"

        # if self.expire:
        #     expiry_date_obj = format_expire(self.expire)
        #     if expiry_date_obj:
        #         self.expire = expiry_date_obj.strftime("%m/%y")
                
        #         today = date.today().replace(day=1)
        #         if expiry_date_obj < today:
        #             self.status = EXPIRE
        #     else:
        #         errors['expire'] = "Muddati noto'g'ri formatda! (Masalan: 12/25)"

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.card_number} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Karta"
        verbose_name_plural = "Kartalar"
