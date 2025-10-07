from fastapi import APIRouter, HTTPException
from app.models.schemas import FinancialDataResponse, FinancialRecord, HealthCheckResponse, SchedulerStatusResponse
from app.utils.csv_handler import CSVHandler
from app.services.scraper import FinancialScraper
from app.services.scheduler import get_scheduler_status, update_financial_data
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
csv_handler = CSVHandler()

@router.get("/uva", response_model=List[FinancialRecord])
async def get_uva_data():
    """
    Obtiene los datos históricos de UVA más 10 años de proyecciones mockeadas
    """
    try:
        data = csv_handler.get_data_with_projections('uva', years=10)

        records = [
            FinancialRecord(fecha=row['fecha'], valor=float(row['valor']))
            for row in data
        ]

        return records
    except Exception as e:
        logger.error(f"Error getting UVA data: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving UVA data: {str(e)}")

@router.get("/dolar-mayorista", response_model=List[FinancialRecord])
async def get_dolar_mayorista_data():
    """
    Obtiene los datos históricos de Dólar Mayorista más 10 años de proyecciones mockeadas
    """
    try:
        data = csv_handler.get_data_with_projections('dolar_mayorista', years=10)

        records = [
            FinancialRecord(fecha=row['fecha'], valor=float(row['valor']))
            for row in data
        ]

        return records
    except Exception as e:
        logger.error(f"Error getting Dólar Mayorista data: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving Dólar Mayorista data: {str(e)}")

@router.get("/dolar-mep", response_model=List[FinancialRecord])
async def get_dolar_mep_data():
    """
    Obtiene los datos históricos de Dólar MEP más 10 años de proyecciones mockeadas
    """
    try:
        data = csv_handler.get_data_with_projections('dolar_mep', years=10)

        records = [
            FinancialRecord(fecha=row['fecha'], valor=float(row['valor']))
            for row in data
        ]

        return records
    except Exception as e:
        logger.error(f"Error getting Dólar MEP data: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving Dólar MEP data: {str(e)}")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Endpoint de health check que verifica que el scraping de los tres valores esté funcionando correctamente
    """
    errors = []
    uva_scraping = False
    dolar_mayorista_scraping = False
    dolar_mep_scraping = False
    uva_value = None
    dolar_mayorista_value = None
    dolar_mep_value = None

    # Test UVA scraping
    try:
        uva_data = FinancialScraper.scrape_uva()
        uva_value = uva_data['valor']
        uva_scraping = uva_value > 0
        if not uva_scraping:
            errors.append("UVA value is 0 or invalid")
    except Exception as e:
        errors.append(f"UVA scraping failed: {str(e)}")
        uva_scraping = False

    # Test Dólar Mayorista scraping
    try:
        dolar_mayorista_data = FinancialScraper.scrape_dolar_mayorista()
        dolar_mayorista_value = dolar_mayorista_data['valor']
        dolar_mayorista_scraping = dolar_mayorista_value > 0
        if not dolar_mayorista_scraping:
            errors.append("Dólar Mayorista value is 0 or invalid")
    except Exception as e:
        errors.append(f"Dólar Mayorista scraping failed: {str(e)}")
        dolar_mayorista_scraping = False

    # Test Dólar MEP scraping
    try:
        dolar_mep_data = FinancialScraper.scrape_dolar_mep()
        dolar_mep_value = dolar_mep_data['valor']
        dolar_mep_scraping = dolar_mep_value > 0
        if not dolar_mep_scraping:
            errors.append("Dólar MEP value is 0 or invalid")
    except Exception as e:
        errors.append(f"Dólar MEP scraping failed: {str(e)}")
        dolar_mep_scraping = False

    # Determinar status general
    all_working = uva_scraping and dolar_mayorista_scraping and dolar_mep_scraping
    status = "healthy" if all_working else "unhealthy"

    return HealthCheckResponse(
        status=status,
        uva_scraping=uva_scraping,
        dolar_mayorista_scraping=dolar_mayorista_scraping,
        dolar_mep_scraping=dolar_mep_scraping,
        uva_value=uva_value,
        dolar_mayorista_value=dolar_mayorista_value,
        dolar_mep_value=dolar_mep_value,
        errors=errors
    )

@router.get("/scheduler/status", response_model=SchedulerStatusResponse)
async def get_scheduler_info():
    """
    Obtiene información del scheduler y próxima ejecución del job
    """
    try:
        status = get_scheduler_status()
        return status
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving scheduler status: {str(e)}")

@router.post("/scheduler/run-now")
async def trigger_update_now():
    """
    Ejecuta manualmente el job de actualización (para testing)
    """
    try:
        logger.info("Manual trigger of financial data update requested")
        update_financial_data()
        return {
            "status": "success",
            "message": "Financial data update completed successfully"
        }
    except Exception as e:
        logger.error(f"Error executing manual update: {e}")
        raise HTTPException(status_code=500, detail=f"Error executing update: {str(e)}")
