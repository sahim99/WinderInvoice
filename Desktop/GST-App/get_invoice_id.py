import sqlite3
try:
    conn = sqlite3.connect('gst_billing.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM invoices WHERE invoice_no='INV-0025'")
    row = cursor.fetchone()
    print(f"Invoice ID: {row[0] if row else 'Not Found'}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
