from datetime import datetime, timedelta
from typing import List
import pandas as pd

def parse_date(date_str: str) -> datetime:
    """Convierte una fecha en formato DD-MM-YY a objeto datetime."""
    return datetime.strptime(date_str, "%d-%m-%y")

def format_date(date: datetime) -> str:
    """Convierte un objeto datetime a formato DD-MM-YY."""
    return date.strftime("%d-%m-%y")

def generate_future_dates(start_date: datetime, years: int = 10) -> List[datetime]:
    """Genera fechas futuras desde una fecha inicial hasta 10 años adelante."""
    end_date = start_date + timedelta(days=years*365)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    return [date.to_pydatetime() for date in date_range]

def process_csv_data(df: pd.DataFrame) -> List[dict]:
    """Procesa los datos del CSV y genera las fechas futuras."""
    # Verificar si el DataFrame está vacío
    if df.empty:
        # Si está vacío, crear un DataFrame con la fecha actual y 10 años de fechas futuras
        today = datetime.now()
        future_dates = generate_future_dates(today)
        df = pd.DataFrame({
            'fecha': future_dates,
            'valor': 1.0
        })
    else:
        # Verificar si la columna 'fecha' existe
        if 'fecha' not in df.columns:
            # Si no existe, crear un DataFrame con la fecha actual y 10 años de fechas futuras
            today = datetime.now()
            future_dates = generate_future_dates(today)
            df = pd.DataFrame({
                'fecha': future_dates,
                'valor': 1.0
            })
        else:
            # Convertir la columna de fecha al formato correcto
            df['fecha'] = pd.to_datetime(df['fecha'], format='%d-%m-%y')
            
            # Obtener la última fecha del DataFrame
            last_date = df['fecha'].max()
            
            # Generar fechas futuras
            future_dates = generate_future_dates(last_date)
            
            # Crear DataFrame con fechas futuras
            future_df = pd.DataFrame({
                'fecha': future_dates,
                'valor': 1.0
            })
            
            # Combinar datos históricos con futuros
            df = pd.concat([df, future_df])
            
            # Eliminar duplicados manteniendo los valores históricos
            df = df.drop_duplicates(subset=['fecha'], keep='first')
            
            # Ordenar por fecha
            df = df.sort_values('fecha')
    
    # Convertir a formato requerido
    result = []
    for _, row in df.iterrows():
        result.append({
            'fecha': format_date(row['fecha']),
            'valor': float(row['valor'])
        })
    
    return result 