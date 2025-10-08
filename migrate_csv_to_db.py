"""
Script para migrar datos de CSVs a Supabase
Ejecutar: python migrate_csv_to_db.py
"""
import csv
import os
from app.db.database import SessionLocal, FinancialData, init_db

def migrate_csv_to_db():
    """Migra los datos de los CSVs a la base de datos"""

    # Inicializar DB
    print("Initializing database...")
    init_db()

    db = SessionLocal()

    csv_files = {
        'uva': 'data/uva.csv',
        'dolar_mayorista': 'data/dolar_mayorista.csv',
        'dolar_mep': 'data/dolar_mep.csv'
    }

    total_records = 0

    for tipo, file_path in csv_files.items():
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_path}")
            continue

        print(f"\n📄 Processing {tipo}...")

        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            records_count = 0

            for row in csv_reader:
                if not row['fecha'] or not row['valor']:
                    continue

                try:
                    # Verificar si ya existe
                    existing = db.query(FinancialData).filter(
                        FinancialData.tipo == tipo,
                        FinancialData.fecha == row['fecha']
                    ).first()

                    if not existing:
                        record = FinancialData(
                            tipo=tipo,
                            fecha=row['fecha'],
                            valor=float(row['valor'])
                        )
                        db.add(record)
                        records_count += 1
                    else:
                        print(f"  Skipping existing record: {row['fecha']}")

                except Exception as e:
                    print(f"  ❌ Error processing row {row}: {e}")

            db.commit()
            print(f"  ✅ Inserted {records_count} records for {tipo}")
            total_records += records_count

    db.close()
    print(f"\n🎉 Migration completed! Total records inserted: {total_records}")

if __name__ == "__main__":
    print("🚀 Starting CSV to Database migration...\n")
    migrate_csv_to_db()
