from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:wallet_id>/', views.get_wallet_balance, name='get_wallet_balance'),
    path('<uuid:wallet_id>/operation', views.wallet_operation, name='wallet_operation'),
]