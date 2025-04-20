import pandas as pd
from datetime import datetime
from typing import Literal
from sqlmodel import Session
from models.database_models import DolarMEP, UVA, DolarMayorista

TableType = Literal["dolar_mep", "uva", "dolar_mayorista"]

def parse_date(date_str: str) -> datetime:
    """Convierte una fecha en formato DD-MM-YY a objeto datetime."""
    return datetime.strptime(date_str, "%d-%m-%y")

def import_historical_data(csv_path: str, table_type: TableType, engine) -> None:
    """
    Importa datos históricos desde un archivo CSV.
    
    Args:
        csv_path: Ruta al archivo CSV
        table_type: Tipo de tabla ('dolar_mep', 'uva', 'dolar_mayorista')
        engine: SQLAlchemy engine
    
    El CSV debe tener las columnas:
    - fecha: en formato DD-MM-YY (ej: 01-01-24)
    - valor: número decimal
    """
    # Mapeo de tipos de tabla a modelos
    model_map = {
        "dolar_mep": DolarMEP,
        "uva": UVA,
        "dolar_mayorista": DolarMayorista
    }
    
    # Leer CSV
    df = pd.read_csv(csv_path)
    
    # Verificar columnas requeridas
    required_columns = {'fecha', 'valor'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"El CSV debe contener las columnas: {required_columns}")
    
    # Convertir fechas
    df['fecha'] = df['fecha'].apply(parse_date)
    
    # Crear objetos del modelo correspondiente
    model_class = model_map[table_type]
    records = [
        model_class(fecha=row['fecha'], valor=float(row['valor']))
        for _, row in df.iterrows()
    ]
    
    # Guardar en la base de datos
    with Session(engine) as session:
        # Verificar si ya existen registros para esas fechas
        existing_dates = {
            date[0].date() for date in 
            session.query(model_class.fecha).all()
        }
        
        # Filtrar solo registros nuevos
        new_records = [
            record for record in records
            if record.fecha.date() not in existing_dates
        ]
        
        if new_records:
            session.add_all(new_records)
            session.commit()
            print(f"Se importaron {len(new_records)} registros nuevos para {table_type}")
        else:
            print(f"No se encontraron registros nuevos para importar en {table_type}") 