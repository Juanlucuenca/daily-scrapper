import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.database_models import Base, DolarMayorista

# Configuración de la base de datos
SQLALCHEMY_DATABASE_URL = "sqlite:///./cotizaciones.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear una sesión
db = SessionLocal()

try:
    # Leer el archivo CSV
    df = pd.read_csv("dolar_mayorista.csv")
    print(f"Registros en el CSV: {len(df)}")
    
    # Verificar columnas requeridas
    if not all(col in df.columns for col in ['fecha', 'valor']):
        print("Error: El CSV debe contener las columnas 'fecha' y 'valor'")
        exit(1)
    
    # Procesar cada fila
    for _, row in df.iterrows():
        try:
            fecha = datetime.strptime(row['fecha'], '%d-%m-%y').date()
            valor = float(row['valor'])
            
            # Verificar si ya existe un registro para esa fecha
            existing = db.query(DolarMayorista).filter(DolarMayorista.fecha == fecha).first()
            if existing:
                existing.valor = valor
                print(f"Actualizado: {fecha} - {valor}")
            else:
                new_record = DolarMayorista(fecha=fecha, valor=valor)
                db.add(new_record)
                print(f"Agregado: {fecha} - {valor}")
        except Exception as e:
            print(f"Error procesando fila: {row} - {str(e)}")
    
    # Confirmar cambios
    db.commit()
    print("Cambios confirmados en la base de datos")
    
    # Verificar registros después de la importación
    count = db.query(DolarMayorista).count()
    print(f"Registros en la tabla dolar_mayorista después de la importación: {count}")
    
    # Mostrar los primeros 5 registros
    records = db.query(DolarMayorista).order_by(DolarMayorista.fecha).limit(5).all()
    print("\nPrimeros 5 registros después de la importación:")
    for record in records:
        print(f"ID: {record.id}, Fecha: {record.fecha}, Valor: {record.valor}")
    
except Exception as e:
    print(f"Error general: {str(e)}")
    db.rollback()
finally:
    db.close() 