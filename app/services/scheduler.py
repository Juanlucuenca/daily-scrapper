from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.scraper import FinancialScraper
from app.utils.csv_handler import CSVHandler
import logging
import pytz
from datetime import datetime

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
csv_handler = CSVHandler()

def update_financial_data():
    """
    Tarea programada que actualiza los tres valores financieros en los CSVs
    """
    logger.info("Starting scheduled financial data update...")

    try:
        # Scrape UVA
        uva_data = FinancialScraper.scrape_uva()
        csv_handler.update_csv_value('uva', uva_data['valor'])
        logger.info(f"UVA updated: {uva_data['valor']}")

    except Exception as e:
        logger.error(f"Failed to update UVA: {e}")

    try:
        # Scrape Dólar Mayorista
        dolar_mayorista_data = FinancialScraper.scrape_dolar_mayorista()
        csv_handler.update_csv_value('dolar_mayorista', dolar_mayorista_data['valor'])
        logger.info(f"Dólar Mayorista updated: {dolar_mayorista_data['valor']}")

    except Exception as e:
        logger.error(f"Failed to update Dólar Mayorista: {e}")

    try:
        # Scrape Dólar MEP
        dolar_mep_data = FinancialScraper.scrape_dolar_mep()
        csv_handler.update_csv_value('dolar_mep', dolar_mep_data['valor'])
        logger.info(f"Dólar MEP updated: {dolar_mep_data['valor']}")

    except Exception as e:
        logger.error(f"Failed to update Dólar MEP: {e}")

    logger.info("Scheduled financial data update completed")

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
