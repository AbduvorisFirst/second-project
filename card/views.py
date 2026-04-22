from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from jsonrpcserver import dispatch
import json
from . import rpc # импортируем файл с методами, чтобы они зарегистрировались

@csrf_exempt
def api_endpoint(request):
    """Единая точка входа для всех JSON-RPC запросов"""
    if request.method == "POST":
        # Получаем сырой JSON из тела запроса
        request_data = request.body.decode()

        # Библиотека jsonrpcserver сама понимает, какой метод вызвать
        response = dispatch(request_data)

        # Возвращаем результат обратно клиенту
        if response:
            return JsonResponse(json.loads(response), safe=False)

    return JsonResponse({"error": "Only POST allowed"}, status=405)
