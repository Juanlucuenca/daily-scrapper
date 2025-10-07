from fastapi import FastAPI
from app.routers import financial_data
from app.services.scheduler import start_scheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Financial Data Scraper API",
    description="API para obtener valores financieros diarios (UVA, Dólar Mayorista, Dólar MEP)",
    version="1.0.0"
)

app.include_router(financial_data.router, prefix="/api", tags=["financial-data"])

@app.on_event("startup")
async def startup_event():
    """Inicia el scheduler cuando la aplicación arranca"""
    logger.info("Starting scheduler...")
    start_scheduler()
    logger.info("Scheduler started successfully")

@app.get("/")
async def root():
    return {
        "message": "Financial Data Scraper API",
        "endpoints": {
            "uva": "/api/uva",
            "dolar_mayorista": "/api/dolar-mayorista",
            "dolar_mep": "/api/dolar-mep",
            "health": "/api/health"
        }
    }
