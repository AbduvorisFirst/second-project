
import re
from django.core.exceptions import ValidationError
from datetime import datetime


def is_luhn_valid(card_number):
    """
    Karta raqami Luhn algoritmi bo'yicha to'g'riligini tekshiradi.
    """
    # Karta raqamidan faqat raqamlarni olib qolamiz
    card_number = str(card_number).replace(" ", "").replace("-", "")
    
    if not card_number.isdigit():
        return False

    digits = [int(d) for d in card_number]
    
    # 1. O'ngdan chapga qarab, har ikkinchi raqamni 2 ga ko'paytiramiz
    for i in range(len(digits) - 2, -1, -2):
        multiplied = digits[i] * 2
        # 2. Agar ko'paytma 9 dan katta bo'lsa, uning raqamlari yig'indisini olamiz
        # (yoki shunchaki 9 ni ayirib tashlaymiz - natija bir xil bo'ladi)
        if multiplied > 9:
            multiplied -= 9
        digits[i] = multiplied
        
    # 3. Barcha raqamlar yig'indisi 10 ga qoldiqsiz bo'linishi kerak
    return sum(digits) % 10 == 0


def validate_phone(value):
    # Faqat raqamlarni qoldiramiz
    clean_phone = re.sub(r'\D', '', value)
    
    # O'zbekiston raqami formati: 998901234567 yoki 901234567
    if not re.match(r'^(998)?\d{9}$', clean_phone):
        raise ValidationError("Telefon raqami formati noto'g'ri!")
    return clean_phone



def format_expire(raw_expire):
    """
    Turli formatdagi expire matnlarini yagona sana (date) obyektiga o'tkazadi.
    Masalan: '12/24', '2024-12', '12.2024' -> 2024-12-01
    """
    if not raw_expire:
        return None

    raw_expire = str(raw_expire).strip()
    
    # Tekshiriladigan formatlar ro'yxati
    formats = [
        "%m/%y",   # 12/24
        "%Y-%m",   # 2024-12
        "%m.%Y",   # 12.2024
        "%m/%Y",   # 12/2024
        "%d.%m.%Y" # 15.12.2024 (agar kun bilan kelsa)
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(raw_expire, fmt)
            # Bizga faqat oy va yil muhim, shuning uchun kunni 1-sana qilib belgilaymiz
            return dt.date().replace(day=1)
        except ValueError:
            continue

    return None  # Agar hech bir formatga tushmasa

