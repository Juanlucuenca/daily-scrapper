from fastapi import FastAPI
from app.routers import financial_data
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Financial Data Scraper API",
    description="API para obtener valores financieros diarios (UVA, Dólar Mayorista, Dólar MEP)",
    version="1.0.0"
)

app.include_router(financial_data.router, tags=["financial-data"])

# Scheduler solo en ambientes no-serverless
@app.on_event("startup")
async def startup_event():
    """Inicia el scheduler solo si no es Vercel"""
    # Vercel es serverless, no soporta background tasks
    is_vercel = os.getenv("VERCEL") == "1"

    if not is_vercel:
        from app.services.scheduler import start_scheduler
        logger.info("Starting scheduler...")
        start_scheduler()
        logger.info("Scheduler started successfully")
    else:
        logger.info("Running on Vercel - Scheduler disabled. Use external cron service.")

@app.get("/")
async def root():
    return {
        "message": "Financial Data Scraper API",
    }
