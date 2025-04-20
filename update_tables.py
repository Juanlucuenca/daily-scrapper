import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from models.database_models import Base, UVA, DolarMEP, DolarMayorista
from sqlalchemy.orm import sessionmaker

# Configuración de la base de datos
DATABASE_URL = "sqlite:///cotizaciones.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def update_table(csv_path: str, model_class, table_name: str):
    """
    Actualiza una tabla específica con datos del CSV.
    
    Args:
        csv_path: Ruta al archivo CSV
        model_class: Clase del modelo SQLAlchemy
        table_name: Nombre de la tabla para mensajes
    """
    print(f"\nActualizando tabla {table_name}...")
    
    # Leer el CSV
    df = pd.read_csv(csv_path)
    print(f"Registros en CSV {table_name}: {len(df)}")
    
    # Convertir fechas
    df['fecha'] = pd.to_datetime(df['fecha'], format='%d-%m-%y')
    
    # Crear sesión de base de datos
    db = SessionLocal()
    
    try:
        # Verificar registros existentes
        existing_dates = set(date[0] for date in db.query(model_class.fecha).all())
        print(f"Fechas existentes en la base de datos: {len(existing_dates)}")
        
        # Verificar específicamente la fecha 30-06-24
        target_date = datetime.strptime('30-06-24', '%d-%m-%y').date()
        target_row = df[df['fecha'].dt.date == target_date]
        
        if not target_row.empty:
            print(f"\nEncontrada fecha objetivo {target_date} en CSV con valor: {target_row['valor'].iloc[0]}")
            existing_target = db.query(model_class).filter(model_class.fecha == target_date).first()
            if existing_target:
                print(f"La fecha {target_date} ya existe en la base de datos con valor: {existing_target.valor}")
            else:
                print(f"La fecha {target_date} NO existe en la base de datos y será insertada")
        
        # Procesar cada fila
        for _, row in df.iterrows():
            fecha = row['fecha'].date()
            valor = float(row['valor'])
            
            # Verificar si ya existe un registro para esa fecha
            existing = db.query(model_class).filter(model_class.fecha == fecha).first()
            
            if existing:
                if existing.valor != valor:
                    print(f"Actualizando {table_name} para fecha {fecha}: {valor} (valor anterior: {existing.valor})")
                    existing.valor = valor
            else:
                print(f"Insertando nuevo registro en {table_name} para fecha {fecha}: {valor}")
                new_record = model_class(fecha=fecha, valor=valor)
                db.add(new_record)
        
        # Guardar cambios
        db.commit()
        
        # Verificar registros después de la actualización
        final_count = db.query(model_class).count()
        print(f"Total de registros en {table_name} después de la actualización: {final_count}")
        
        # Verificar específicamente si la fecha objetivo fue insertada
        if not target_row.empty:
            final_target = db.query(model_class).filter(model_class.fecha == target_date).first()
            if final_target:
                print(f"Verificación final: La fecha {target_date} está en la base de datos con valor: {final_target.valor}")
            else:
                print(f"¡ALERTA! La fecha {target_date} NO está en la base de datos después de la actualización")
        
    except Exception as e:
        print(f"Error actualizando {table_name}: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Función principal que actualiza todas las tablas."""
    print("Iniciando actualización de tablas...")
    
    try:
        # Actualizar cada tabla
        update_table("mayorista_lo_q_falta.csv", DolarMayorista, "dolar_mayorista")
        update_table("mep.csv", DolarMEP, "dolar_mep")
        update_table("uva.csv", UVA, "uva")
        
        print("\nProceso de actualización completado exitosamente")
    except Exception as e:
        print(f"\nError durante la actualización: {str(e)}")
        raise

if __name__ == "__main__":
    main() 