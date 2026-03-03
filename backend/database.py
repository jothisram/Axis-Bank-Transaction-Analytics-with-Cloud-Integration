import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "dbname":   os.getenv("DB_NAME", "axisbank"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", ""),
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def query(sql, params=None, fetchone=False):
    conn = get_conn()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params or ())
    if fetchone:
        result = cur.fetchone()
    else:
        result = cur.fetchall()
    cur.close(); conn.close()
    return result

def execute(sql, params=None):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(sql, params or ())
    conn.commit()
    cur.close(); conn.close()

def init_auth_tables():
    """Ensure admin table has totp_secret column; seed admin user."""
    conn = get_conn()
    cur  = conn.cursor()

    # Add totp_secret column to admin table if missing
    cur.execute("""
        ALTER TABLE admin
        ADD COLUMN IF NOT EXISTS totp_secret VARCHAR(64) DEFAULT NULL,
        ADD COLUMN IF NOT EXISTS totp_enabled BOOLEAN DEFAULT FALSE;
    """)

    conn.commit()

    # Seed admin — Axis-admin / 0987654321
    from passlib.context import CryptContext
    pwd_ctx = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    hashed  = pwd_ctx.hash("0987654321")
    cur.execute("""
        INSERT INTO admin (username, hashed_password)
        VALUES ('Axis-admin', %s)
        ON CONFLICT (username) DO UPDATE SET hashed_password = EXCLUDED.hashed_password;
    """, (hashed,))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Auth tables ready | Admin seeded")

if __name__ == "__main__":
    init_auth_tables()