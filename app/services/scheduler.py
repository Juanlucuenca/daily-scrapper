from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.scraper import FinancialScraper
from app.utils.db_handler import DBHandler
import logging
import pytz
from datetime import datetime

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
db_handler = DBHandler()

def update_financial_data():
    """
    Tarea programada que actualiza los tres valores financieros en la base de datos
    Returns: Dict con información de la actualización
    """
    logger.info("Starting scheduled financial data update...")

    # Obtener fecha y hora de Argentina
    argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
    now_argentina = datetime.now(argentina_tz)
    execution_date = now_argentina.strftime("%d-%m-%y")
    execution_time = now_argentina.strftime("%H:%M:%S")
    execution_datetime = now_argentina.strftime("%d-%m-%Y %H:%M:%S")

    results = {
        "execution_date": execution_date,
        "execution_time": execution_time,
        "execution_datetime": execution_datetime,
        "timezone": "America/Argentina/Buenos_Aires",
        "updates": {},
        "errors": []
    }

    # Scrape UVA
    try:
        uva_data = FinancialScraper.scrape_uva()
        db_handler.update_value('uva', uva_data['valor'])
        results["updates"]["uva"] = {
            "valor": float(uva_data['valor']),
            "status": "success"
        }
        logger.info(f"UVA updated: {uva_data['valor']}")
    except Exception as e:
        error_msg = f"Failed to update UVA: {str(e)}"
        results["errors"].append(error_msg)
        results["updates"]["uva"] = {
            "valor": None,
            "status": "error",
            "error": str(e)
        }
        logger.error(error_msg)

    # Scrape Dólar Mayorista
    try:
        dolar_mayorista_data = FinancialScraper.scrape_dolar_mayorista()
        db_handler.update_value('dolar_mayorista', dolar_mayorista_data['valor'])
        results["updates"]["dolar_mayorista"] = {
            "valor": float(dolar_mayorista_data['valor']),
            "status": "success"
        }
        logger.info(f"Dólar Mayorista updated: {dolar_mayorista_data['valor']}")
    except Exception as e:
        error_msg = f"Failed to update Dólar Mayorista: {str(e)}"
        results["errors"].append(error_msg)
        results["updates"]["dolar_mayorista"] = {
            "valor": None,
            "status": "error",
            "error": str(e)
        }
        logger.error(error_msg)

    # Scrape Dólar MEP
    try:
        dolar_mep_data = FinancialScraper.scrape_dolar_mep()
        db_handler.update_value('dolar_mep', dolar_mep_data['valor'])
        results["updates"]["dolar_mep"] = {
            "valor": float(dolar_mep_data['valor']),
            "status": "success"
        }
        logger.info(f"Dólar MEP updated: {dolar_mep_data['valor']}")
    except Exception as e:
        error_msg = f"Failed to update Dólar MEP: {str(e)}"
        results["errors"].append(error_msg)
        results["updates"]["dolar_mep"] = {
            "valor": None,
            "status": "error",
            "error": str(e)
        }
        logger.error(error_msg)

    logger.info("Scheduled financial data update completed")
    return results

def start_scheduler():
    """
    Inicia el scheduler con tarea programada para las 16:10 hora de Argentina
    """
    # Zona horaria de Argentina
    argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')

    # Programar tarea para las 16:10 (4:10 PM) hora de Argentina
    scheduler.add_job(
        update_financial_data,
        trigger=CronTrigger(hour=16, minute=10, timezone=argentina_tz),
        id='update_daily',
        name='Update financial data at 4:10 PM Argentina time',
        replace_existing=True
    )

    scheduler.start()
    logger.info("Scheduler started with daily job at 4:10 PM Argentina time")

def get_scheduler_status():
    """
    Obtiene el estado del scheduler y los jobs programados
    """
    argentina_tz = pytz.timezone('America/Argentina/Buenos_Aires')
    current_time = datetime.now(argentina_tz)

    jobs_info = []

    if scheduler.running:
        jobs = scheduler.get_jobs()
        for job in jobs:
            next_run = job.next_run_time
            jobs_info.append({
                'id': job.id,
                'name': job.name,
                'next_run': next_run.strftime('%Y-%m-%d %H:%M:%S %Z') if next_run else None,
                'trigger': str(job.trigger)
            })

    return {
        'scheduler_running': scheduler.running,
        'current_time_argentina': current_time.strftime('%Y-%m-%d %H:%M:%S %Z'),
        'timezone': 'America/Argentina/Buenos_Aires',
        'jobs': jobs_info,
        'total_jobs': len(jobs_info)
    }
