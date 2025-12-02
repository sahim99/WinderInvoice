from app.database import SessionLocal
from sqlalchemy import text

def check_column():
    session = SessionLocal()
    try:
        result = session.execute(text("PRAGMA table_info(invoice_items)")).fetchall()
        columns = [row[1] for row in result]
        print(f"Columns: {columns}")
        if 'no_of_pkts' in columns:
            print("no_of_pkts exists")
        else:
            print("no_of_pkts MISSING")
            # Try to add it
            try:
                print("Attempting to add column...")
                session.execute(text("ALTER TABLE invoice_items ADD COLUMN no_of_pkts INTEGER DEFAULT 0"))
                session.commit()
                print("Column added successfully")
            except Exception as e:
                print(f"Error adding column: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_column()
