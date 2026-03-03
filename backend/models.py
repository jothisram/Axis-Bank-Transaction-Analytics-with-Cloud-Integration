from pydantic import BaseModel
from typing import Optional

class CustomerLogin(BaseModel):
    account_number: str
    name: str
    ifsc_code: str

class ManagementRegister(BaseModel):
    name: str
    branch: str
    password: str

class ManagementLogin(BaseModel):
    name: str
    branch: str
    password: str

class AdminLogin(BaseModel):
    username: str
    password: str
    totp_code: Optional[str] = None   # TOTP 6-digit code (required after setup)

class AdminTOTPVerify(BaseModel):
    username: str
    totp_code: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str
    extra: Optional[dict] = None