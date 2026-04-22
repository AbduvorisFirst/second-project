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

class Error(models.Model):
    code = models.IntegerField(unique=True)
    en = models.CharField(max_length=255)
    ru = models.CharField(max_length=255)
    uz = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.code} - {self.en}"

class Transfer(models.Model):
    STATE_CHOICES = (
        ('created', 'Created'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    ext_id = models.CharField(max_length=100, unique=True)
    sender_card_number = models.CharField(max_length=16)
    receiver_card_number = models.CharField(max_length=16)
    sender_card_expiry = models.CharField(max_length=10)
    sender_phone = models.CharField(max_length=20, null=True, blank=True)
    receiver_phone = models.CharField(max_length=20, null=True, blank=True)
    sending_amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.IntegerField() # 643 (RUB), 840 (USD)
    receiving_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='created')
    try_count = models.IntegerField(default=0)
    otp = models.CharField(max_length=6, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transfer {self.ext_id} ({self.state})"


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
        max_digits=18,
        decimal_places=2,
        default=0
    )

    def clean(self):
        """Barcha maydonlarni validatsiya qilish"""
        errors = {}

        #  Karta raqamini Luhn algoritmi bo'yicha tekshirish
        # if self.card_number:
        #     if not is_luhn_valid(self.card_number):
        #         errors['card_number'] = f"Karta raqami xato: {self.card_number}"

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

    # def save(self, *args, **kwargs):
    #     self.full_clean()
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.card_number} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Karta"
        verbose_name_plural = "Kartalar"
