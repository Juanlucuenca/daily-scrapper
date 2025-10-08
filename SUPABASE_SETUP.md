# Configuración de Supabase - Guía Paso a Paso

## 📋 Paso 1: Crear Proyecto en Supabase

1. Ve a https://supabase.com
2. **Sign up** o **Login**
3. Click en **"New Project"**
4. Completa:
   - **Name**: `daily-scrapper`
   - **Database Password**: (crea una contraseña fuerte y guárdala)
   - **Region**: selecciona la más cercana
5. Click en **"Create new project"** (tarda ~2 minutos)

---

## 📋 Paso 2: Crear la Tabla

1. Una vez creado el proyecto, ve a **SQL Editor** (menú lateral)
2. Click en **"New query"**
3. Copia y pega el contenido de `supabase_schema.sql`
4. Click en **"Run"** o presiona `Ctrl+Enter`
5. Deberías ver: ✅ Success. No rows returned

---

## 📋 Paso 3: Obtener la Connection String

1. Ve a **Settings** (ícono de engranaje en el menú lateral)
2. Click en **"Database"**
3. Busca la sección **"Connection string"**
4. Selecciona **"URI"**
5. Copia la URL que se ve así:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```
6. Reemplaza `[YOUR-PASSWORD]` con tu contraseña real

---

## 📋 Paso 4: Configurar Variable de Entorno (Local)

Crea un archivo `.env` en la raíz del proyecto:

```bash
SUPABASE_DB_URL=postgresql://postgres:TU_PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

---

## 📋 Paso 5: Migrar Datos de CSV a Supabase

Ejecuta el script de migración:

```bash
# Asegúrate de tener la variable de entorno configurada
python migrate_csv_to_db.py
```

Deberías ver:
```
🚀 Starting CSV to Database migration...

Initializing database...

📄 Processing uva...
  ✅ Inserted XXX records for uva

📄 Processing dolar_mayorista...
  ✅ Inserted XXX records for dolar_mayorista

📄 Processing dolar_mep...
  ✅ Inserted XXX records for dolar_mep

🎉 Migration completed! Total records inserted: XXX
```

---

## 📋 Paso 6: Verificar Datos en Supabase

1. Ve a **Table Editor** en Supabase
2. Selecciona la tabla `financial_data`
3. Deberías ver todos tus registros

---

## 📋 Paso 7: Configurar Variable de Entorno en Vercel

1. Ve a tu proyecto en Vercel: https://vercel.com
2. Selecciona tu proyecto `daily-scrapper`
3. Ve a **Settings** → **Environment Variables**
4. Agrega:
   - **Key**: `SUPABASE_DB_URL`
   - **Value**: `postgresql://postgres:TU_PASSWORD@db.xxxxx.supabase.co:5432/postgres`
   - **Environments**: selecciona Production, Preview, Development
5. Click en **"Save"**
6. **Redeploy** tu aplicación para que tome la nueva variable

---

## 📋 Paso 8: Probar

1. Llama a tu endpoint: `https://tu-app.vercel.app/uva`
2. Deberías ver los datos desde Supabase
3. Prueba el health check: `https://tu-app.vercel.app/health`
4. Ejecuta manualmente: `POST https://tu-app.vercel.app/scheduler/run-now`
5. Verifica que se agregó el nuevo registro en Supabase

---

## ✅ Listo!

Ahora tu aplicación:
- ✅ Usa Supabase para almacenar datos
- ✅ Los datos persisten entre deployments
- ✅ EasyCron actualiza la DB diariamente a las 16:10
- ✅ Funciona perfectamente en Vercel

---

## 🔧 Comandos Útiles

### Ver datos en Supabase SQL Editor:
```sql
SELECT * FROM financial_data WHERE tipo = 'uva' ORDER BY fecha DESC LIMIT 10;
```

### Contar registros por tipo:
```sql
SELECT tipo, COUNT(*) FROM financial_data GROUP BY tipo;
```

### Limpiar tabla (si necesitas):
```sql
DELETE FROM financial_data;
```
