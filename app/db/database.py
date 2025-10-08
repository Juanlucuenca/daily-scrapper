import os
from sqlalchemy import create_engine, Column, String, Float, Integer, DECIMAL, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import logging

logger = logging.getLogger(__name__)

# Obtener DATABASE_URL de variables de entorno
DATABASE_URL = os.getenv("SUPABASE_DB_URL")

# Si no hay DATABASE_URL, usar SQLite local (para desarrollo)
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./financial_data.db"
    logger.warning("No SUPABASE_DB_URL found, using SQLite for development")
else:
    # Supabase requiere postgresql en lugar de postgres
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelos
class FinancialData(Base):
    __tablename__ = "financial_data"

    id = Column(BigInteger, primary_key=True, index=True)
    tipo = Column(String(50), index=True, nullable=False)  # 'uva', 'dolar_mayorista', 'dolar_mep'
    fecha = Column(String(20), index=True, nullable=False)
    valor = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

def init_db():
    """Crea las tablas si no existen"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")

def get_db():
    """Dependency para obtener sesión de DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
