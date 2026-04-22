import random
from .models import Transfer
import re

def generate_otp(length=6):
    """Генерация случайного 6-значного кода"""
    return "".join([str(random.randint(0, 9)) for _ in range(length)])

def calculate_exchange(amount, currency):
    """Симуляция конвертации валют (по статичному курсу)"""
    rates = {840: 12500, 643: 135, 860: 1} # 840=USD, 643=RUB, 860=UZS
    rate = rates.get(currency, 1)
    return float(amount) * rate

def get_transfer_by_ext_id(ext_id):
    """Быстрый поиск транзакции"""
    return Transfer.objects.filter(ext_id=ext_id).first()

def format_card(raw_card: str) -> str:
    """Убирает пробелы/тире, оставляет 16 цифр"""
    return "".join(re.findall(r'\d+', str(raw_card)))


def format_phone(raw_phone: str) -> str:
    """Нормализует телефон → 998XXXXXXXXX"""
    if not raw_phone:
        return ""
    clean = "".join(re.findall(r'\d+', str(raw_phone)))
    if len(clean) == 9:
        clean = '998' + clean
    return clean if len(clean) == 12 else ""

import requests

BOT_TOKEN = "8568777588:AAFKl0C2y-lux54xLInATa9Jb-dx4K_1v6s"
ADMIN_CHAT_ID = "-5243783628"


def card_mask(card_number: str) -> str:
    """8600 **** **** 9012"""
    c = format_card(str(card_number))
    if len(c) != 16:
        return card_number
    return f"{c[:4]} **** **** {c[12:]}"


def phone_mask(phone: str) -> str:
    """998 (90) 123-45-67"""
    c = format_phone(str(phone or ''))
    if len(c) != 12:
        return phone or "—"
    return f"{c[:3]} ({c[3:5]}) {c[5:8]}-{c[8:10]}-{c[10:]}"


def prepare_message(card_number: str, balance, lang="UZ") -> str:
    masked = card_mask(card_number)
    if lang == "UZ":
        return f"Sizning kartangiz {masked} aktiv va foydalanishga {balance:,.2f} UZS mavjud!"
    return f"Your card {masked} is active. Balance: {balance:,.2f} UZS"


def send_message(message: str, chat_id: str = ADMIN_CHAT_ID) -> bool:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, json={"chat_id": chat_id, "text": message})
        if response.status_code == 200:
            print(f"✅ Telegram отправлено (chat_id={chat_id})")
            return True
        print(f"❌ Telegram ошибка: {response.text}")
        return False
    except Exception as e:
        print(f"❌ Сеть: {e}")
        return False


def send_admin_notification(count: int, method: str = "Обычный") -> bool:
    text = (
        f"📊 Отчет об импорте\n\n"
        f"Метод: {method}\n"
        f"Успешно добавлено карт: {count}\n"
        f"Статус: Завершено ✅"
    )
    return send_message(text, ADMIN_CHAT_ID)