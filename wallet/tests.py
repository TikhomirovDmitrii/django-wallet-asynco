import pytest
import json
import uuid
import asyncio
from django.urls import reverse
import aiohttp
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import insert
from .database import WalletTable

# Создаём engine для тестов
DATABASE_URL = "postgresql+asyncpg://walletuser:walletpassword@db:5432/walletdb"
test_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Фикстура для единого event loop
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Фикстура для создания сессии
@pytest.fixture(scope="function")
async def async_session():
    async with AsyncSession(test_engine, expire_on_commit=False) as session:
        yield session

# Фикстура для создания кошелька с изоляцией
@pytest.fixture(scope="function")
async def create_wallet(async_session):
    wallet_id = uuid.uuid4()
    await async_session.execute(insert(WalletTable).values(id=wallet_id, balance=1000.00))
    await async_session.commit()
    return str(wallet_id)

# Фикстура для HTTP-клиента
@pytest.fixture(scope="function")
async def client(event_loop):
    async with aiohttp.ClientSession() as session:
        yield session

# Фикстура для очистки соединений с БД
@pytest.fixture(scope="function", autouse=True)
async def cleanup():
    yield
    await test_engine.dispose()
    await asyncio.sleep(0.1)

@pytest.mark.asyncio
async def test_get_wallet_balance_success(client, create_wallet):
    wallet_id = create_wallet
    url = f"http://localhost:8000{reverse('get_wallet_balance', args=[wallet_id])}"
    async with client.get(url) as response:
        assert response.status == 200
        data = await response.json()
        assert data["wallet_id"] == wallet_id
        assert data["balance"] == 1000.0

@pytest.mark.asyncio
async def test_get_wallet_balance_not_found(client):
    url = f"http://localhost:8000{reverse('get_wallet_balance', args=['550e8400-e29b-41d4-a716-446655440000'])}"
    async with client.get(url) as response:
        assert response.status == 404
        data = await response.json()
        assert data["error"] == "Wallet not found"

@pytest.mark.asyncio
async def test_wallet_deposit_success(client, create_wallet):
    wallet_id = create_wallet
    url = f"http://localhost:8000{reverse('wallet_operation', args=[wallet_id])}"
    payload = {"operationType": "DEPOSIT", "amount": 500}
    async with client.post(url, json=payload) as response:
        assert response.status == 200
        data = await response.json()
        assert data["wallet_id"] == wallet_id
        assert data["balance"] == 1500.0

@pytest.mark.asyncio
async def test_wallet_withdraw_success(client, create_wallet):
    wallet_id = create_wallet
    url = f"http://localhost:8000{reverse('wallet_operation', args=[wallet_id])}"
    payload = {"operationType": "WITHDRAW", "amount": 300}
    async with client.post(url, json=payload) as response:
        assert response.status == 200
        data = await response.json()
        assert data["wallet_id"] == wallet_id
        assert data["balance"] == 700.0

@pytest.mark.asyncio
async def test_wallet_withdraw_insufficient_funds(client, create_wallet):
    wallet_id = create_wallet
    url = f"http://localhost:8000{reverse('wallet_operation', args=[wallet_id])}"
    payload = {"operationType": "WITHDRAW", "amount": 2000}
    async with client.post(url, json=payload) as response:
        assert response.status == 400
        data = await response.json()
        assert data["error"] == "Insufficient funds"

@pytest.mark.asyncio
async def test_wallet_operation_invalid_type(client, create_wallet):
    wallet_id = create_wallet
    url = f"http://localhost:8000{reverse('wallet_operation', args=[wallet_id])}"
    payload = {"operationType": "INVALID", "amount": 500}
    async with client.post(url, json=payload) as response:
        assert response.status == 400
        data = await response.json()
        assert data["error"] == "Invalid operation type"

@pytest.mark.asyncio
async def test_wallet_operation_invalid_json(client, create_wallet):
    wallet_id = create_wallet
    url = f"http://localhost:8000{reverse('wallet_operation', args=[wallet_id])}"
    async with client.post(url, data="invalid json", headers={"Content-Type": "application/json"}) as response:
        assert response.status == 400
        data = await response.json()
        assert data["error"] == "Invalid JSON or amount"

@pytest.mark.asyncio
async def test_wallet_operation_negative_amount(client, create_wallet):
    wallet_id = create_wallet
    url = f"http://localhost:8000{reverse('wallet_operation', args=[wallet_id])}"
    payload = {"operationType": "DEPOSIT", "amount": -100}
    async with client.post(url, json=payload) as response:
        assert response.status == 400
        data = await response.json()
        assert data["error"] == "Amount must be positive"
