import logging
from jsonrpcserver import method, Result, Success, Error as RPCError
from django.utils import timezone
from .models import Card, Transfer, Error
from .utils import generate_otp, send_message, calculate_exchange, get_transfer_by_ext_id

logger = logging.getLogger(__name__)

def get_error_msg(code, lang='en'):
    """Получает текст ошибки из БД"""
    err = Error.objects.filter(code=code).first()
    if err:
        return getattr(err, lang, err.en)
    return "Unknown Error"

# --- 1. TRANSFER CREATE ---
@method(name="transfer.create")
def transfer_create(ext_id, sender_card_number, sender_card_expiry, receiver_card_number, sending_amount, currency):
    try:
        if get_transfer_by_ext_id(ext_id):
            return RPCError(32701, get_error_msg(32701))

        if currency not in [643, 840]:
            return RPCError(32707, get_error_msg(32707))

        sender = Card.objects.filter(card_number=sender_card_number, expire=sender_card_expiry).first()
        if not sender:
            return RPCError(32704, get_error_msg(32704))
        if sender.status != 'active':
            return RPCError(32705, get_error_msg(32705))
        if sender.balance < sending_amount:
            return RPCError(32702, get_error_msg(32702))
        if not sender.phone:
            return RPCError(32703, get_error_msg(32703))

        receiver = Card.objects.filter(card_number=receiver_card_number).first()
        if not receiver:
            return RPCError(32706, "Receiver card not found in system")

        otp_code = generate_otp()
        receiving_amount = calculate_exchange(sending_amount, currency)

        Transfer.objects.create(
            ext_id=ext_id,
            sender_card_number=sender_card_number,
            receiver_card_number=receiver_card_number,
            sender_card_expiry=sender_card_expiry,
            sender_phone=sender.phone,
            receiver_phone=receiver.phone,
            sending_amount=sending_amount,
            currency=currency,
            receiving_amount=receiving_amount,
            otp=otp_code,
            state='created'
        )

        # Отправляем OTP в Telegram
        send_message(f"🔒 Код подтверждения перевода: {otp_code}", sender.phone)
        logger.info(f"Transfer {ext_id} created. OTP sent to {sender.phone}")

        return Success({"ext_id": ext_id, "state": "created", "otp_sent": True})

    except Exception as e:
        logger.error(f"Transfer Create Error: {str(e)}")
        return RPCError(32706, get_error_msg(32706))


# --- 2. TRANSFER CONFIRM ---
@method(name="transfer.confirm")
def transfer_confirm(ext_id, otp):
    transfer = get_transfer_by_ext_id(ext_id)
    if not transfer:
        return RPCError(32714, "Transfer not found")

    if transfer.state != 'created':
        return RPCError(32713, "Transfer is already processed or cancelled")

    if transfer.try_count >= 3:
        return RPCError(32711, get_error_msg(32711))

    if transfer.otp != str(otp):
        transfer.try_count += 1
        transfer.save()
        left_tries = 3 - transfer.try_count
        if left_tries == 0:
            return RPCError(32711, get_error_msg(32711))
        return RPCError(32712, f"Incorrect OTP. Attempts left: {left_tries}")

    # Успешное подтверждение
    transfer.state = 'confirmed'
    transfer.confirmed_at = timezone.now()
    transfer.save()

    # Здесь в реальном проекте списываются/зачисляются деньги с карт

    return Success({"ext_id": ext_id, "state": "confirmed"})


# --- 3. TRANSFER CANCEL ---
@method(name="transfer.cancel")
def transfer_cancel(ext_id):
    transfer = get_transfer_by_ext_id(ext_id)
    if not transfer:
        return RPCError(32714, "Transfer not found")

    if transfer.state != 'created':
        return RPCError(32713, "Can only cancel 'created' transfers")

    transfer.state = 'cancelled'
    transfer.cancelled_at = timezone.now()
    transfer.save()

    return Success({"state": "cancelled"})


# --- 4. TRANSFER STATE ---
@method(name="transfer.state")
def transfer_state(ext_id):
    transfer = get_transfer_by_ext_id(ext_id)
    if not transfer:
        return RPCError(32714, "Transfer not found")

    return Success({"ext_id": ext_id, "state": transfer.state})


# --- 5. TRANSFER HISTORY ---
@method(name="transfer.history")
def transfer_history(card_number, start_date, end_date, status):
    transfers = Transfer.objects.filter(
        sender_card_number=card_number,
        state=status,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )

    result_list = []
    for t in transfers:
        result_list.append({
            "ext_id": t.ext_id,
            "sending_amount": float(t.sending_amount),
            "state": t.state,
            "created_at": t.created_at.isoformat()
        })

    return Success(result_list)