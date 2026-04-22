from django.urls import path
from card.views import api_endpoint

urlpatterns = [
    path('api/v1/rpc/', api_endpoint, name='rpc_endpoint'),
]