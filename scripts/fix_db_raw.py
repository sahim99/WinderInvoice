import sqlite3

def fix_db():
    try:
        conn = sqlite3.connect('gst_billing.db')
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(invoice_items)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"Columns: {columns}")
        
        if 'no_of_pkts' not in columns:
            print("Adding no_of_pkts column...")
            cursor.execute("ALTER TABLE invoice_items ADD COLUMN no_of_pkts INTEGER DEFAULT 0")
            conn.commit()
            print("Column added successfully.")
        else:
            print("no_of_pkts already exists.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_db()
