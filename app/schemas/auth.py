from pydantic import BaseModel, EmailStr, Field

class LoginCreate(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class LogoutRequest(BaseModel):
    refresh_token: str

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str

class ResendOTPRequest(BaseModel):
    email: EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8)

class RefreshTokenRequest(BaseModel):
    refresh_token: str 
