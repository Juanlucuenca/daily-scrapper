# Financial Data Scraper API

Sistema de scraping automático de valores financieros (UVA, Dólar Mayorista y Dólar MEP) con API REST desarrollado en FastAPI.

## Características

- **Scraping Automático**: Actualiza automáticamente los valores a las 16:00 y 22:00 (horario de Argentina)
- **API REST**: Endpoints para consultar datos históricos y proyecciones
- **Proyecciones Mockeadas**: Genera 10 años de datos futuros con valor 1
- **Health Check**: Endpoint para verificar el correcto funcionamiento del scraping

## Estructura del Proyecto

```
daily-scrapper/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicación FastAPI principal
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Modelos Pydantic
│   ├── routers/
│   │   ├── __init__.py
│   │   └── financial_data.py   # Endpoints de la API
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scraper.py          # Lógica de scraping
│   │   └── scheduler.py        # Tareas programadas
│   └── utils/
│       ├── __init__.py
│       └── csv_handler.py      # Manejo de archivos CSV
├── data/
│   ├── uva.csv
│   ├── dolar_mayorista.csv
│   └── dolar_mep.csv
├── requirements.txt
└── README.md
```

## Instalación

1. Clonar el repositorio:
```bash
git clone <repository-url>
cd daily-scrapper
```

2. Crear entorno virtual:
```bash
python -m venv venv
```

3. Activar entorno virtual:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Ejecución

Iniciar el servidor:
```bash
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

## Endpoints de la API

### 1. Obtener datos de UVA
```
GET /api/uva
```
Retorna datos históricos de UVA + 10 años de proyecciones

### 2. Obtener datos de Dólar Mayorista
```
GET /api/dolar-mayorista
```
Retorna datos históricos de Dólar Mayorista + 10 años de proyecciones

### 3. Obtener datos de Dólar MEP
```
GET /api/dolar-mep
```
Retorna datos históricos de Dólar MEP + 10 años de proyecciones

### 4. Health Check
```
GET /api/health
```
Verifica que el scraping de los tres valores esté funcionando correctamente.

Respuesta de ejemplo:
```json
{
  "status": "healthy",
  "uva_scraping": true,
  "dolar_mayorista_scraping": true,
  "dolar_mep_scraping": true,
  "uva_value": 1555.16,
  "dolar_mayorista_value": 1429.00,
  "dolar_mep_value": 1541.00,
  "errors": []
}
```

## Formato de Respuesta

Todos los endpoints de datos financieros retornan el siguiente formato:

```json
{
  "data": [
    {
      "fecha": "01-01-24",
      "valor": 463.40
    },
    {
      "fecha": "02-01-24",
      "valor": 463.40
    }
  ],
  "total_records": 3650
}
```

## Tareas Programadas

El sistema ejecuta automáticamente el scraping de los tres valores en los siguientes horarios (zona horaria de Argentina):

- **16:00** (4 PM)
- **22:00** (10 PM)

Los valores scraped se actualizan automáticamente en los archivos CSV correspondientes.

## Documentación Interactiva

FastAPI genera documentación automática:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Fuentes de Datos

- **UVA**: https://prestamos.ikiwi.net.ar/api/v1/engine/uva/valores/
- **Dólar Mayorista**: https://es.investing.com/currencies/usd-ars
- **Dólar MEP**: https://www.dolarhoy.com/

## Notas Técnicas

- Los datos históricos se almacenan en archivos CSV en la carpeta `data/`
- Las proyecciones mockeadas tienen valor constante de 1
- El formato de fecha en los CSV es `dd-mm-yy`
- El sistema maneja reintentos automáticos con backoff exponencial para el scraping
