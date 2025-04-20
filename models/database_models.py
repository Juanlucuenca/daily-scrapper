from sqlalchemy import Column, Integer, Float, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class UVA(Base):
    __tablename__ = "uva"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, unique=True, index=True)
    valor = Column(Float)

class DolarMEP(Base):
    __tablename__ = "dolar_mep"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, unique=True, index=True)
    valor = Column(Float)

class DolarMayorista(Base):
    __tablename__ = "dolar_mayorista"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, unique=True, index=True)
    valor = Column(Float)

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URL = "sqlite:///./cotizaciones.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear todas las tablas
Base.metadata.create_all(bind=engine) 