import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal
from models import FutureLabInput


excel_path = "Data_Ingestion_Logic_Diet_Delights (3).xlsx"
df = pd.read_excel(excel_path, sheet_name="Future_Lab_Inputs")

# Normalize column names
df.rename(columns={
    'ID': 'id',
    'Source': 'source',
    'Conditions Supported': 'condition_supported',
    'Test Type': 'test_type',
    'Format': 'format',
    'Validation': 'validation',
    'Unit': 'unit',
    'Database Field Name': 'database_field_name',

}, inplace=True)

session: Session = SessionLocal()

for _, row in df.iterrows():
    try:
        entry = FutureLabInput(
            source=row['source'],
            condition_supported=row['Condition Supported'],
            test_type=row['Feature Captured'],
            format=row['Expected Format'],
            unit=row['Unit / Scale'],
            validation=row['Validation Rule'],
            database_field_name=row['database_field_name'],

        )
        session.add(entry)
    except Exception as e:
        print(f" Error: {e}")

session.commit()
session.close()
print("✅ Data inserted into future_lab_inputs table.")
