import uuid
import json
from locust import HttpUser, task, between
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from wallet.database import WalletTable

# Настройка синхронного подключения к базе данных
DATABASE_URL = "postgresql://walletuser:walletpassword@db:5432/walletdb"  # Хост "db" для Docker
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)
Session = sessionmaker(bind=engine)

def create_wallet_sync():
    wallet_id = uuid.uuid4()
    with Session() as session:
        session.execute(insert(WalletTable).values(id=wallet_id, balance=1000.00))
        session.commit()
    return str(wallet_id)

class WalletUser(HttpUser):
    wait_time = between(1, 5)  # Задержка между задачами (в секундах)

    def on_start(self):
        # Создаём кошелёк синхронно при старте каждого пользователя
        self.wallet_id = create_wallet_sync()

    @task(3)  # Вес 3: чаще проверяем баланс
    def get_balance(self):
        self.client.get(f"/api/v1/wallets/{self.wallet_id}/", name="Get Balance")

    @task(2)  # Вес 2: депозиты
    def deposit(self):
        payload = {"operationType": "DEPOSIT", "amount": 500}
        self.client.post(
            f"/api/v1/wallets/{self.wallet_id}/operation",
            json=payload,
            name="Deposit",
            headers={"Content-Type": "application/json"}
        )

    @task(1)  # Вес 1: вывод средств
    def withdraw(self):
        payload = {"operationType": "WITHDRAW", "amount": 200}
        self.client.post(
            f"/api/v1/wallets/{self.wallet_id}/operation",
            json=payload,
            name="Withdraw",
            headers={"Content-Type": "application/json"}
        )
