# Financial Data Scraper API

Sistema de scraping automático de valores financieros argentinos (UVA, Dólar Mayorista y Dólar MEP) con API REST desarrollado en FastAPI y almacenamiento en Supabase PostgreSQL.

## Características

- **Scraping Automático**: Actualiza valores diariamente a las 16:10 (horario de Argentina) vía EasyCron
- **Base de Datos Persistente**: Almacenamiento en Supabase PostgreSQL
- **API REST**: Endpoints para consultar datos históricos y proyecciones
- **Proyecciones Mockeadas**: Genera 10 años de datos futuros con valor 1
- **Anti-Bot Protection**: Usa ScraperAPI para evitar bloqueos
- **Serverless Ready**: Optimizado para Vercel
- **Health Check**: Endpoints para verificar el funcionamiento del scraping

## Estructura del Proyecto

```
daily-scrapper/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación FastAPI principal
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py         # Configuración SQLAlchemy y modelos
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Modelos Pydantic para API
│   ├── routers/
│   │   ├── __init__.py
│   │   └── financial_data.py   # Endpoints de la API
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scraper.py          # Lógica de scraping
│   │   └── scheduler.py        # Tareas programadas
│   └── utils/
│       ├── __init__.py
│       └── db_handler.py       # Operaciones de base de datos
├── data/                       # CSVs originales (solo referencia)
│   ├── uva.csv
│   ├── dolar_mayorista.csv
│   └── dolar_mep.csv
├── requirements.txt
├── supabase_schema.sql         # Schema de la base de datos
├── migrate_csv_to_db.py        # Script de migración
├── SUPABASE_SETUP.md          # Guía de configuración
└── README.md
```

## Stack Tecnológico

- **Backend**: FastAPI (Python)
- **Base de Datos**: Supabase (PostgreSQL)
- **ORM**: SQLAlchemy
- **Scraping**: BeautifulSoup4, lxml, ScraperAPI
- **Scheduling**: APScheduler + EasyCron (external)
- **Deployment**: Vercel (serverless)

## Instalación Local

1. **Clonar el repositorio**:
```bash
git clone https://github.com/Juanlucuenca/daily-scrapper.git
cd daily-scrapper
```

2. **Crear entorno virtual**:
```bash
python -m venv venv
```

3. **Activar entorno virtual**:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

5. **Configurar Supabase** (ver `SUPABASE_SETUP.md`):
- Crear proyecto en https://supabase.com
- Ejecutar `supabase_schema.sql` en SQL Editor
- Configurar variable de entorno en `.env`:
```bash
SUPABASE_DB_URL=postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:6543/postgres
```

6. **Migrar datos**:
```bash
python migrate_csv_to_db.py
```

## Ejecución Local

```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

## Endpoints de la API

### Datos Financieros

#### GET `/uva`
Retorna datos históricos de UVA + 10 años de proyecciones

**Respuesta**:
```json
[
  {
    "fecha": "01-01-24",
    "valor": 463.40
  },
  {
    "fecha": "02-01-24",
    "valor": 463.40
  }
]
```

#### GET `/dolar-mayorista`
Retorna datos históricos de Dólar Mayorista + 10 años de proyecciones

#### GET `/dolar-mep`
Retorna datos históricos de Dólar MEP + 10 años de proyecciones

### Monitoreo y Control

#### GET `/health`
Verifica que el scraping de los tres valores funcione correctamente

**Respuesta**:
```json
{
  "status": "healthy",
  "uva_scraping": true,
  "dolar_mayorista_scraping": true,
  "dolar_mep_scraping": true,
  "uva_value": 1603.52,
  "dolar_mayorista_value": 1429.00,
  "dolar_mep_value": 1499.00,
  "errors": []
}
```

#### GET `/scheduler/status`
Muestra el estado del scheduler y próxima ejecución

**Respuesta**:
```json
{
  "scheduler_running": false,
  "current_time_argentina": "2025-10-07 20:56:07 -03",
  "timezone": "America/Argentina/Buenos_Aires",
  "jobs": [],
  "total_jobs": 0
}
```

#### POST `/scheduler/run-now`
Ejecuta manualmente la actualización de datos (útil para testing)

**Respuesta**:
```json
{
  "status": "success",
  "message": "Financial data update completed successfully"
}
```

## Scraping Automático

El sistema está configurado para actualizar automáticamente los datos:

- **Horario**: 16:10 (4:10 PM) horario de Argentina
- **Frecuencia**: Diario
- **Método**: Cron job externo (EasyCron) que llama a `POST /scheduler/run-now`

### Configuración EasyCron

1. Registrarse en https://www.easycron.com
2. Crear cron job:
   - **URL**: `https://tu-app.vercel.app/scheduler/run-now`
   - **Método**: POST
   - **Schedule**: `10 16 * * *`
   - **Timezone**: America/Buenos_Aires

## Deploy en Vercel

### Configuración

1. **Conectar repositorio** en Vercel
2. **Agregar variable de entorno**:
   - Key: `SUPABASE_DB_URL`
   - Value: Tu connection string de Supabase
3. **Deploy**

### Nota importante

Vercel es serverless, por lo que:
- ✅ El scheduler interno NO funciona (normal)
- ✅ Usa EasyCron para ejecutar tareas programadas
- ✅ Los datos persisten en Supabase (no en filesystem)

## Documentación Interactiva

FastAPI genera documentación automática:

- **Swagger UI**: `https://tu-app.vercel.app/docs`
- **ReDoc**: `https://tu-app.vercel.app/redoc`

## Fuentes de Datos

- **UVA**: https://prestamos.ikiwi.net.ar/api/v1/engine/uva/valores/
- **Dólar Mayorista**: https://es.investing.com/currencies/usd-ars (vía ScraperAPI)
- **Dólar MEP**: https://www.dolarhoy.com/

## Base de Datos

### Schema

```sql
CREATE TABLE financial_data (
    id BIGSERIAL PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,  -- 'uva', 'dolar_mayorista', 'dolar_mep'
    fecha VARCHAR(20) NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(tipo, fecha)
);
```

### Consultas útiles

Ver datos recientes:
```sql
SELECT * FROM financial_data
WHERE tipo = 'uva'
ORDER BY fecha DESC
LIMIT 10;
```

Contar registros por tipo:
```sql
SELECT tipo, COUNT(*)
FROM financial_data
GROUP BY tipo;
```

## Tecnologías Anti-Bot

El scraping de Investing.com usa **ScraperAPI** para evitar bloqueos:
- Plan gratuito: 1,000 requests/mes
- Suficiente para 1 request diario (~30/mes)

## Variables de Entorno

```bash
# Requerida
SUPABASE_DB_URL=postgresql://postgres:PASSWORD@db.xxxxx.supabase.co:6543/postgres

# Opcional (detectada automáticamente en Vercel)
VERCEL=1
```

## Desarrollo

### Agregar nuevo endpoint

1. Crear función en `app/routers/financial_data.py`
2. Definir schema en `app/models/schemas.py` si es necesario
3. Testear localmente

### Modificar schema de BD

1. Editar `supabase_schema.sql`
2. Ejecutar en SQL Editor de Supabase
3. Actualizar modelo en `app/db/database.py`

## Troubleshooting

### Scheduler no funciona en Vercel
**Normal**. Vercel es serverless. Usa EasyCron configurado externamente.

### Datos no se guardan
Verifica que `SUPABASE_DB_URL` esté configurada en variables de entorno de Vercel.

### ScraperAPI falla
Verifica que tengas créditos disponibles en tu plan gratuito (1,000/mes).

## Licencia

MIT

## Autor

Juan Lucuenca

---

**Repositorio**: https://github.com/Juanlucuenca/daily-scrapper
