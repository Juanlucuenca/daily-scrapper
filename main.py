from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import pandas as pd
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from typing import List

from models.database_models import SessionLocal, UVA, DolarMEP, DolarMayorista
from models.schemas import CotizacionResponse
from utils.date_utils import process_csv_data
from utils.scraping_utils import get_uva_value, get_dolar_mep, get_dolar_mayorista

app = FastAPI(title="Cotizaciones API")

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/import/{table_type}")
async def import_data(table_type: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    if table_type not in ["uva", "dolar_mep", "dolar_mayorista"]:
        raise HTTPException(status_code=400, detail="Tipo de tabla inválido")
    
    try:
        # Leer el archivo CSV
        df = pd.read_csv(file.file)
        
        # Verificar columnas requeridas
        if not all(col in df.columns for col in ['fecha', 'valor']):
            raise HTTPException(status_code=400, detail="El CSV debe contener las columnas 'fecha' y 'valor'")
        
        # Mapeo de tipos de tabla a modelos
        model_map = {
            "uva": UVA,
            "dolar_mep": DolarMEP,
            "dolar_mayorista": DolarMayorista
        }
        
        model = model_map[table_type]
        
        # Procesar cada fila
        for _, row in df.iterrows():
            fecha = datetime.strptime(row['fecha'], '%d-%m-%y').date()
            valor = float(row['valor'])
            
            # Verificar si ya existe un registro para esa fecha
            existing = db.query(model).filter(model.fecha == fecha).first()
            if existing:
                existing.valor = valor
            else:
                new_record = model(fecha=fecha, valor=valor)
                db.add(new_record)
        
        db.commit()
        return {"message": "Datos importados exitosamente"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/uva", response_model=List[CotizacionResponse])
def get_uva_history(db: Session = Depends(get_db)):
    records = db.query(UVA).order_by(UVA.fecha).all()
    if not records:
        # Si no hay registros, crear un DataFrame vacío
        df = pd.DataFrame(columns=['fecha', 'valor'])
    else:
        df = pd.DataFrame([{"fecha": r.fecha, "valor": r.valor} for r in records])
    return process_csv_data(df)

@app.get("/dolar-mep", response_model=List[CotizacionResponse])
def get_dolar_mep_history(db: Session = Depends(get_db)):
    records = db.query(DolarMEP).order_by(DolarMEP.fecha).all()
    if not records:
        # Si no hay registros, crear un DataFrame vacío
        df = pd.DataFrame(columns=['fecha', 'valor'])
    else:
        df = pd.DataFrame([{"fecha": r.fecha, "valor": r.valor} for r in records])
    return process_csv_data(df)

@app.get("/dolar-mayorista", response_model=List[CotizacionResponse])
def get_dolar_mayorista_history(db: Session = Depends(get_db)):
    records = db.query(DolarMayorista).order_by(DolarMayorista.fecha).all()
    if not records:
        # Si no hay registros, crear un DataFrame vacío
        df = pd.DataFrame(columns=['fecha', 'valor'])
    else:
        df = pd.DataFrame([{"fecha": r.fecha, "valor": r.valor} for r in records])
    return process_csv_data(df)

def update_daily_quotes():
    """Actualiza las cotizaciones diarias."""
    print("Actualizando cotizaciones diarias")
    db = SessionLocal()
    try:
        today = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).date()
        
        # Actualizar UVA
        uva_value = get_uva_value()
        if uva_value:
            # Verificar si ya existe un registro para hoy
            existing_uva = db.query(UVA).filter(UVA.fecha == today).first()
            if existing_uva:
                existing_uva.valor = uva_value
            else:
                uva_record = UVA(fecha=today, valor=uva_value)
                db.add(uva_record)
        
        # Actualizar Dólar MEP
        mep_value = get_dolar_mep()
        if mep_value:
            # Verificar si ya existe un registro para hoy
            existing_mep = db.query(DolarMEP).filter(DolarMEP.fecha == today).first()
            if existing_mep:
                existing_mep.valor = mep_value
            else:
                mep_record = DolarMEP(fecha=today, valor=mep_value)
                db.add(mep_record)
        
        # Actualizar Dólar Mayorista
        mayorista_value = get_dolar_mayorista()
        if mayorista_value:
            # Verificar si ya existe un registro para hoy
            existing_mayorista = db.query(DolarMayorista).filter(DolarMayorista.fecha == today).first()
            if existing_mayorista:
                existing_mayorista.valor = mayorista_value
            else:
                mayorista_record = DolarMayorista(fecha=today, valor=mayorista_value)
                db.add(mayorista_record)
        
        db.commit()
    except Exception as e:
        print(f"Error actualizando cotizaciones: {str(e)}")
    finally:
        db.close()

# Configurar el scheduler para ejecutar la actualización diaria
scheduler = BackgroundScheduler()
scheduler.add_job(update_daily_quotes, 'cron', hour=16, timezone='America/Argentina/Buenos_Aires')
scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

@app.get("/test-update")
def test_update_daily_quotes():
    """
    Endpoint para probar la función update_daily_quotes.
    Devuelve los valores actualizados de las cotizaciones.
    """
    try:
        # Ejecutar la actualización
        update_daily_quotes()
        
        # Obtener la fecha actual
        today = datetime.now(pytz.timezone('America/Argentina/Buenos_Aires')).date()
        
        # Crear una sesión para consultar los valores actualizados
        db = SessionLocal()
        try:
            # Obtener los valores actualizados
            uva = db.query(UVA).filter(UVA.fecha == today).first()
            mep = db.query(DolarMEP).filter(DolarMEP.fecha == today).first()
            mayorista = db.query(DolarMayorista).filter(DolarMayorista.fecha == today).first()
            
            # Preparar la respuesta
            response = {
                "fecha": today.strftime("%d-%m-%Y"),
                "cotizaciones": {
                    "uva": uva.valor if uva else None,
                    "dolar_mep": mep.valor if mep else None,
                    "dolar_mayorista": mayorista.valor if mayorista else None
                }
            }
            
            return response
        finally:
            db.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar las cotizaciones: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
