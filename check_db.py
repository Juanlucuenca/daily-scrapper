from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database_models import Base, DolarMayorista

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URL = "sqlite:///./cotizaciones.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear una sesión
db = SessionLocal()

# Verificar si la tabla existe
try:
    # Contar registros en la tabla dolar_mayorista
    count = db.query(DolarMayorista).count()
    print(f"Registros en la tabla dolar_mayorista: {count}")
    
    # Mostrar los primeros 5 registros
    records = db.query(DolarMayorista).order_by(DolarMayorista.fecha).limit(5).all()
    print("\nPrimeros 5 registros:")
    for record in records:
        print(f"ID: {record.id}, Fecha: {record.fecha}, Valor: {record.valor}")
except Exception as e:
    print(f"Error al verificar la base de datos: {str(e)}")
finally:
    db.close() 