from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Numeric
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

class WalletTable(Base):
    __tablename__ = "wallets"
    id = Column(UUID(as_uuid=True), primary_key=True)
    balance = Column(Numeric(15, 2), nullable=False, default=0.00)

DATABASE_URL = "postgresql+asyncpg://walletuser:walletpassword@db:5432/walletdb"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)