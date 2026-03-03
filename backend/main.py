from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.database import query, execute, init_auth_tables
from backend.auth import (
    verify_password, create_token, hash_password,
    generate_totp_secret, get_totp_uri, verify_totp
)
from backend.models import (
    CustomerLogin, ManagementRegister, ManagementLogin,
    AdminLogin, AdminTOTPVerify
)
from backend.routers import customer, management, admin
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64

app = FastAPI(title="Axis Bank Analytics API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(customer.router)
app.include_router(management.router)
app.include_router(admin.router)

@app.on_event("startup")
def startup():
    init_auth_tables()

# ── AUTH: CUSTOMER ─────────────────────────────────────────────────

@app.post("/auth/customer/login")
def customer_login(body: CustomerLogin):
    """Login with account_number + name + ifsc_code"""
    acc = query("""
        SELECT account_number, account_holder, ifsc_code, branch
        FROM accounts
        WHERE account_number = %s
          AND LOWER(TRIM(account_holder)) = LOWER(TRIM(%s))
          AND ifsc_code = %s
    """, (body.account_number, body.name, body.ifsc_code), fetchone=True)
    if not acc:
        raise HTTPException(401, "Invalid credentials. Check Account Number, Name and IFSC Code.")
    token = create_token({
        "role": "customer",
        "account_number": acc["account_number"],
        "name": acc["account_holder"],
        "branch": acc["branch"],
    })
    return {"access_token": token, "token_type": "bearer",
            "role": "customer", "name": acc["account_holder"]}

# ── AUTH: MANAGEMENT ───────────────────────────────────────────────

@app.post("/auth/management/register")
def management_register(body: ManagementRegister):
    """New manager submits registration — goes to pending until admin approves."""
    existing = query(
        "SELECT id FROM managers WHERE LOWER(name)=LOWER(%s) AND LOWER(branch)=LOWER(%s)",
        (body.name, body.branch), fetchone=True
    )
    if existing:
        raise HTTPException(400, "A registration for this name + branch already exists.")
    hashed = hash_password(body.password)
    execute(
        "INSERT INTO managers (name, branch, hashed_password, status) VALUES (%s,%s,%s,'pending')",
        (body.name, body.branch, hashed)
    )
    return {"message": "Registration submitted. Awaiting admin approval."}

@app.post("/auth/management/login")
def management_login(body: ManagementLogin):
    """Login only works if admin has approved the registration."""
    mgr = query(
        "SELECT * FROM managers WHERE LOWER(name)=LOWER(%s) AND LOWER(branch)=LOWER(%s)",
        (body.name, body.branch), fetchone=True
    )
    if not mgr:
        raise HTTPException(401, "No registration found for this name and branch.")
    if mgr["status"] == "pending":
        raise HTTPException(403, "Your registration is pending admin approval.")
    if mgr["status"] == "blocked":
        raise HTTPException(403, "Your access has been blocked by admin.")
    if not verify_password(body.password, mgr["hashed_password"]):
        raise HTTPException(401, "Incorrect password.")
    token = create_token({
        "role": "management",
        "manager_id": mgr["id"],
        "name": mgr["name"],
        "branch": mgr["branch"],
    })
    return {"access_token": token, "token_type": "bearer",
            "role": "management", "name": mgr["name"], "branch": mgr["branch"]}

# ── AUTH: ADMIN ────────────────────────────────────────────────────

@app.post("/auth/admin/login")
def admin_login(body: AdminLogin):
    """2-step admin login: password + TOTP (if TOTP is enabled)."""
    admin_row = query(
        "SELECT * FROM admin WHERE username = %s", (body.username,), fetchone=True
    )
    if not admin_row or not verify_password(body.password, admin_row["hashed_password"]):
        raise HTTPException(401, "Invalid admin credentials.")

    totp_enabled = admin_row.get("totp_enabled", False)

    if totp_enabled:
        if not body.totp_code:
            raise HTTPException(403, "TOTP_REQUIRED")
        if not verify_totp(admin_row["totp_secret"], body.totp_code):
            raise HTTPException(401, "Invalid or expired TOTP code.")

    token = create_token({"role": "admin", "name": body.username})
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": "admin",
        "name": body.username,
        "totp_enabled": totp_enabled,
    }

@app.post("/auth/admin/totp/setup")
def admin_totp_setup(body: AdminLogin):
    """Generate TOTP secret + QR code for admin. Call with just username+password."""
    admin_row = query(
        "SELECT * FROM admin WHERE username = %s", (body.username,), fetchone=True
    )
    if not admin_row or not verify_password(body.password, admin_row["hashed_password"]):
        raise HTTPException(401, "Invalid admin credentials.")

    # Generate new secret
    secret = generate_totp_secret()
    uri    = get_totp_uri(secret, body.username)

    # Save temporarily (not enabled yet — enabled on first verify)
    execute(
        "UPDATE admin SET totp_secret=%s WHERE username=%s",
        (secret, body.username)
    )

    # Generate QR code as base64 PNG
    qr  = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#97144D", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return {
        "secret": secret,
        "qr_code_base64": qr_b64,
        "uri": uri,
        "message": "Scan QR code with Google Authenticator, then call /auth/admin/totp/verify"
    }

@app.post("/auth/admin/totp/verify")
def admin_totp_verify(body: AdminTOTPVerify):
    """Verify TOTP code and enable MFA for admin account."""
    admin_row = query(
        "SELECT * FROM admin WHERE username = %s", (body.username,), fetchone=True
    )
    if not admin_row or not admin_row.get("totp_secret"):
        raise HTTPException(400, "No TOTP secret found. Call /auth/admin/totp/setup first.")
    if not verify_totp(admin_row["totp_secret"], body.totp_code):
        raise HTTPException(401, "Invalid TOTP code.")
    execute(
        "UPDATE admin SET totp_enabled=TRUE WHERE username=%s",
        (body.username,)
    )
    return {"message": "✅ TOTP enabled successfully. MFA is now active for your admin account."}

@app.get("/")
def root():
    return {"status": "Axis Bank Analytics API v2.0 is running"}