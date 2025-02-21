from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sqlalchemy import select
from .models import Wallet
from .database import async_session, WalletTable
import json
from decimal import Decimal
from asgiref.sync import sync_to_async

async def update_balance(wallet_id, amount, operation_type):
    async with async_session() as session:
        async with session.begin():
            stmt = select(WalletTable).where(WalletTable.id == wallet_id).with_for_update()
            result = await session.execute(stmt)
            wallet = result.scalar_one_or_none()

            if not wallet:
                return {"error": "Wallet not found"}, 404

            if operation_type == "DEPOSIT":
                wallet.balance += amount
            elif operation_type == "WITHDRAW":
                if wallet.balance >= amount:
                    wallet.balance -= amount
                else:
                    return {"error": "Insufficient funds"}, 400
            else:
                return {"error": "Invalid operation type"}, 400

            await session.commit()
            return {"wallet_id": str(wallet.id), "balance": float(wallet.balance)}, 200

@csrf_exempt
async def get_wallet_balance(request, wallet_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    wallet = await sync_to_async(Wallet.objects.filter(id=wallet_id).first)()
    if not wallet:
        return JsonResponse({"error": "Wallet not found"}, status=404)

    return JsonResponse({"wallet_id": str(wallet.id), "balance": float(wallet.balance)}, status=200)

@csrf_exempt
async def wallet_operation(request, wallet_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        operation_type = data.get("operationType")
        amount = Decimal(str(data.get("amount", 0)))
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON or amount"}, status=400)

    if amount <= 0:
        return JsonResponse({"error": "Amount must be positive"}, status=400)

    result, status = await update_balance(wallet_id, amount, operation_type)
    return JsonResponse(result, status=status)