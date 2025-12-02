import sqlite3
import os

databases = ["gst_billing.db", "gst_billing_v2.db"]

columns_to_add = [
    ("contact_person", "VARCHAR(255)"),
    ("city", "VARCHAR(255)"),
    ("pincode", "VARCHAR(20)"),
    ("shipping_address", "TEXT"),
    ("pan", "VARCHAR(20)"),
    ("place_of_supply", "VARCHAR(255)"),
    ("price_category", "VARCHAR(50)")
]

for db_file in databases:
    if not os.path.exists(db_file):
        print(f"Skipping {db_file} (not found)")
        continue
        
    print(f"Attempting to update {db_file}...")
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        for col_name, col_type in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE customers ADD COLUMN {col_name} {col_type}")
                print(f"  Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e):
                    print(f"  Column {col_name} already exists.")
                else:
                    print(f"  Error adding {col_name}: {e}")
                    
        conn.commit()
        conn.close()
        print(f"Successfully updated {db_file}")
    except Exception as e:
        print(f"Failed to update {db_file}: {e}")
