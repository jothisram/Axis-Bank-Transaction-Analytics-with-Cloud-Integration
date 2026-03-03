from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import pyotp
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "axisbank_secret")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")
EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# pbkdf2_sha256 is the active scheme; bcrypt is kept as deprecated so old
# manager passwords (hashed before the scheme switch) still verify correctly.
pwd_ctx = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated=["bcrypt"])

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

import bcrypt

def verify_password(plain: str, hashed: str) -> bool:
    """Verify password with support for both modern pbkdf2 and legacy bcrypt."""
    try:
        # If it's a legacy bcrypt hash ($2b$ or $2a$), use bcrypt lib directly.
        # passlib 1.7.4 has a bug with bcrypt 5.0.0 that throws ValueError.
        if hashed.startswith(("$2b$", "$2a$")):
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        
        # Otherwise use passlib (for pbkdf2_sha256)
        return pwd_ctx.verify(plain, hashed)
    except Exception as e:
        print(f"Auth error during verification: {e}")
        return False

def create_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=EXPIRE_MIN)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# ── TOTP helpers ──────────────────────────────────────────────────

def generate_totp_secret() -> str:
    """Generate a new Base32 TOTP secret."""
    return pyotp.random_base32()

def get_totp_uri(secret: str, username: str) -> str:
    """Build otpauth:// URI for QR code generation."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=username, issuer_name="Axis Bank Admin")

def verify_totp(secret: str, code: str) -> bool:
    """Verify a 6-digit TOTP code (±1 window tolerance)."""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)