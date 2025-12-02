"""
Database Migration Script for Settings System
Adds new columns to users and shops tables
Creates new tables: bank_details, notification_preferences, branches, api_tokens, audit_logs
"""
import sqlite3
from pathlib import Path

# Database path
DB_PATH = "gst_billing.db"

def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("🔄 Starting database migration...")
    
    try:
        # ========== ADD COLUMNS TO USERS TABLE ==========
        print("\n📝 Adding columns to users table...")
        
        user_columns = [
            ("full_name", "TEXT"),
            ("phone", "TEXT"),  # Note: UNIQUE constraint will be enforced at application level
            ("phone_verified", "INTEGER DEFAULT 0"),
            ("avatar_path", "TEXT"),
            ("language", "TEXT DEFAULT 'English'"),
            ("timezone", "TEXT DEFAULT 'Asia/Kolkata'"),
            ("created_at", "TIMESTAMP"),  # Will be set by application
            ("updated_at", "TIMESTAMP"),  # Will be set by application
        ]
        
        for col_name, col_type in user_columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"  ✓ Added users.{col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"  ⊙ users.{col_name} already exists")
                else:
                    raise
        
        # ========== ADD COLUMNS TO SHOPS TABLE ==========
        print("\n📝 Adding columns to shops table...")
        
        shop_columns = [
            ("pan", "TEXT"),
            ("business_email", "TEXT"),
            ("business_phone", "TEXT"),
            ("category", "TEXT"),
            ("address_line1", "TEXT"),
            ("address_line2", "TEXT"),
            ("place_of_supply", "TEXT"),
            ("invoice_prefix", "TEXT DEFAULT 'WINV-'"),
            ("next_invoice_number", "INTEGER DEFAULT 1"),
            ("logo_path", "TEXT"),
            ("signature_path", "TEXT"),
            ("created_at", "TIMESTAMP"),  # Will be set by application
            ("updated_at", "TIMESTAMP"),  # Will be set by application
        ]
        
        for col_name, col_type in shop_columns:
            try:
                cursor.execute(f"ALTER TABLE shops ADD COLUMN {col_name} {col_type}")
                print(f"  ✓ Added shops.{col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"  ⊙ shops.{col_name} already exists")
                else:
                    raise
        
        # ========== CREATE BANK_DETAILS TABLE ==========
        print("\n📝 Creating bank_details table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bank_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shop_id INTEGER NOT NULL,
                account_holder TEXT NOT NULL,
                bank_name TEXT NOT NULL,
                account_number_encrypted TEXT NOT NULL,
                ifsc TEXT,
                branch_name TEXT,
                upi_id TEXT,
                qr_code_path TEXT,
                payment_note TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (shop_id) REFERENCES shops(id)
            )
        """)
        print("  ✓ Created bank_details table")
        
        # ========== CREATE NOTIFICATION_PREFERENCES TABLE ==========
        print("\n📝 Creating notification_preferences table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                invoice_email INTEGER DEFAULT 1,
                invoice_whatsapp INTEGER DEFAULT 0,
                monthly_gst_summary INTEGER DEFAULT 1,
                payment_alerts INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("  ✓ Created notification_preferences table")
        
        # ========== CREATE BRANCHES TABLE ==========
        print("\n📝 Creating branches table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS branches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shop_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                address TEXT,
                city TEXT,
                state TEXT,
                pincode TEXT,
                gstin TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (shop_id) REFERENCES shops(id)
            )
        """)
        print("  ✓ Created branches table")
        
        # ========== CREATE API_TOKENS TABLE ==========
        print("\n📝 Creating api_tokens table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT,
                token_hash TEXT NOT NULL,
                scopes TEXT,
                revoked INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("  ✓ Created api_tokens table")
        
        # ========== CREATE AUDIT_LOGS TABLE ==========
        print("\n📝 Creating audit_logs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                object_type TEXT,
                object_id INTEGER,
                details TEXT,
                ip_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("  ✓ Created audit_logs table")
        
        # ========== CREATE INDEXES ==========
        print("\n📝 Creating indexes...")
        indexes = [
            ("idx_bank_details_shop_id", "bank_details", "shop_id"),
            ("idx_bank_details_ifsc", "bank_details", "ifsc"),
            ("idx_notification_prefs_user_id", "notification_preferences", "user_id"),
            ("idx_branches_shop_id", "branches", "shop_id"),
            ("idx_api_tokens_user_id", "api_tokens", "user_id"),
            ("idx_audit_logs_user_id", "audit_logs", "user_id"),
            ("idx_audit_logs_created_at", "audit_logs", "created_at"),
        ]
        
        for idx_name, table_name, column_name in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({column_name})")
                print(f"  ✓ Created index {idx_name}")
            except sqlite3.OperationalError as e:
                print(f"  ⊙ Index {idx_name} already exists or error: {e}")
        
        # Commit all changes
        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("\n📊 Database schema updated with:")
        print("   - New columns on users table (8 columns)")
        print("   - New columns on shops table (13 columns)")
        print("   - bank_details table")
        print("   - notification_preferences table")
        print("   - branches table")
        print("   - api_tokens table")
        print("   - audit_logs table")
        print("   - 7 new indexes")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    run_migration()
