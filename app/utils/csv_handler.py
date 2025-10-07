import csv
import os
from typing import List, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CSVHandler:
    def __init__(self, base_path: str = "data"):
        self.base_path = base_path
        self.files = {
            "uva": os.path.join(base_path, "uva.csv"),
            "dolar_mayorista": os.path.join(base_path, "dolar_mayorista.csv"),
            "dolar_mep": os.path.join(base_path, "dolar_mep.csv")
        }

    def read_csv(self, financial_type: str) -> List[Dict[str, str]]:
        """Lee un archivo CSV y retorna una lista de diccionarios"""
        if financial_type not in self.files:
            raise ValueError(f"Invalid financial type: {financial_type}")

        file_path = self.files[financial_type]

        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return []

        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    data.append(row)
            logger.info(f"Read {len(data)} records from {file_path}")
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            raise

        return data

    def update_csv_value(self, financial_type: str, new_value: float, date_str: str = None) -> bool:
        """Actualiza el CSV con un nuevo valor para la fecha actual"""
        if financial_type not in self.files:
            raise ValueError(f"Invalid financial type: {financial_type}")

        file_path = self.files[financial_type]

        # Si no se proporciona fecha, usar la actual
        if date_str is None:
            date_str = datetime.now().strftime("%d-%m-%y")

        try:
            # Leer todos los datos existentes
            data = self.read_csv(financial_type)

            # Verificar si ya existe un registro para esta fecha
            found = False
            for row in data:
                if row['fecha'] == date_str:
                    row['valor'] = str(new_value)
                    found = True
                    logger.info(f"Updated existing record for {date_str}: {new_value}")
                    break

            # Si no existe, agregar nuevo registro
            if not found:
                data.append({'fecha': date_str, 'valor': str(new_value)})
                logger.info(f"Added new record for {date_str}: {new_value}")

            # Escribir de vuelta al CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['fecha', 'valor']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

            logger.info(f"Successfully updated {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error updating {file_path}: {e}")
            return False

    def get_latest_value(self, financial_type: str) -> Dict[str, str] | None:
        """Obtiene el último valor registrado"""
        data = self.read_csv(financial_type)
        if not data:
            return None
        return data[-1]

    def get_data_with_projections(self, financial_type: str, years: int = 10) -> List[Dict[str, str]]:
        """
        Retorna los datos reales del CSV más proyecciones mockeadas hacia adelante.

        Args:
            financial_type: Tipo de dato financiero
            years: Cantidad de años hacia adelante a proyectar

        Returns:
            Lista de diccionarios con fecha y valor
        """
        # Obtener datos reales
        real_data = self.read_csv(financial_type)

        if not real_data:
            return []

        # Parsear la última fecha
        last_record = real_data[-1]
        last_date_str = last_record['fecha']

        # Parsear la fecha (formato: dd-mm-yy)
        try:
            last_date = datetime.strptime(last_date_str, "%d-%m-%y")
        except ValueError:
            # Intentar formato alternativo (dd-mm-yyyy)
            last_date = datetime.strptime(last_date_str, "%d-%m-%Y")

        # Generar fechas futuras
        projected_data = []
        current_date = last_date + timedelta(days=1)
        end_date = last_date + timedelta(days=365 * years)

        while current_date <= end_date:
            projected_data.append({
                'fecha': current_date.strftime("%d-%m-%y"),
                'valor': '1'
            })
            current_date += timedelta(days=1)

        logger.info(f"Generated {len(projected_data)} projected records for {financial_type}")

        # Combinar datos reales con proyectados
        return real_data + projected_data
