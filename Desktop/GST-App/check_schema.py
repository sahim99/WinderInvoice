import sqlite3

# Check database schema
conn = sqlite3.connect('gst_billing.db')
cursor = conn.cursor()

print("=" * 60)
print("DATABASE SCHEMA VERIFICATION")
print("=" * 60)

# Check users table
cursor.execute('PRAGMA table_info(users)')
user_cols = [row[1] for row in cursor.fetchall()]
print(f"\n✓ Users table columns ({len(user_cols)}):")
for col in user_cols:
    print(f"  - {col}")

# Check shops table
cursor.execute('PRAGMA table_info(shops)')
shop_cols = [row[1] for row in cursor.fetchall()]
print(f"\n✓ Shops table columns ({len(shop_cols)}):")
for col in shop_cols:
    print(f"  - {col}")

# Check all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]
print(f"\n✓ All tables ({len(tables)}):")
for table in tables:
    print(f"  - {table}")

# Check for new tables
new_tables = ['bank_details', 'notification_preferences', 'branches', 'api_tokens', 'audit_logs']
print(f"\n✓ New tables check:")
for table in new_tables:
    exists = table in tables
    status = "✓" if exists else "✗"
    print(f"  {status} {table}")

conn.close()

print("\n" + "=" * 60)
print("SCHEMA CHECK COMPLETE")
print("=" * 60)
