from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.database import FinancialData, SessionLocal
from typing import List, Dict
from datetime import datetime, timedelta
import logging
import pytz

logger = logging.getLogger(__name__)

class DBHandler:
    """Maneja operaciones de base de datos para datos financieros"""

    def __init__(self):
        pass

    def get_session(self):
        """Obtiene una sesión de base de datos"""
        return SessionLocal()

    def read_data(self, financial_type: str) -> List[Dict[str, str]]:
        """Lee datos de la base de datos ordenados por ID (más viejo a más nuevo)"""
        db = self.get_session()
        try:
            records = db.query(FinancialData).filter(
                FinancialData.tipo == financial_type
            ).order_by(FinancialData.id.asc()).all()

            data = [
                {'fecha': record.fecha, 'valor': str(float(record.valor))}
                for record in records
            ]

            logger.info(f"Read {len(data)} records for {financial_type}")
            return data

        except Exception as e:
            logger.error(f"Error reading data for {financial_type}: {e}")
            return []
        finally:
            db.close()

    def update_value(self, financial_type: str, new_value: float, date_str: str = None) -> bool:
        """Actualiza o inserta un valor en la base de datos"""
        if date_str is None:
            # Usar zona horaria de Argentina
            argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
            now_argentina = datetime.now(argentina_tz)
            date_str = now_argentina.strftime("%d-%m-%y")

        db = self.get_session()
        try:
            # Buscar registro existente
            existing = db.query(FinancialData).filter(
                and_(
                    FinancialData.tipo == financial_type,
                    FinancialData.fecha == date_str
                )
            ).first()

            if existing:
                # Actualizar
                existing.valor = new_value
                logger.info(f"Updated existing record for {financial_type} on {date_str}: {new_value}")
            else:
                # Insertar nuevo
                new_record = FinancialData(
                    tipo=financial_type,
                    fecha=date_str,
                    valor=new_value
                )
                db.add(new_record)
                logger.info(f"Added new record for {financial_type} on {date_str}: {new_value}")

            db.commit()
            return True

        except Exception as e:
            db.rollback()
            logger.error(f"Error updating {financial_type}: {e}")
            return False
        finally:
            db.close()

    def get_latest_value(self, financial_type: str) -> Dict[str, str] | None:
        """Obtiene el último valor registrado"""
        db = self.get_session()
        try:
            record = db.query(FinancialData).filter(
                FinancialData.tipo == financial_type
            ).order_by(FinancialData.fecha.desc()).first()

            if record:
                return {'fecha': record.fecha, 'valor': str(float(record.valor))}
            return None

        except Exception as e:
            logger.error(f"Error getting latest value for {financial_type}: {e}")
            return None
        finally:
            db.close()

    def get_data_with_projections(self, financial_type: str, years: int = 10) -> List[Dict[str, str]]:
        """
        Retorna los datos reales de la DB más proyecciones mockeadas hacia adelante
        """
        # Obtener datos reales
        real_data = self.read_data(financial_type)

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
            try:
                last_date = datetime.strptime(last_date_str, "%d-%m-%Y")
            except ValueError:
                logger.error(f"Could not parse date: {last_date_str}")
                return real_data

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
