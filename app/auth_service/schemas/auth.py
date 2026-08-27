from pydantic import BaseModel, EmailStr, Field

class UserRegister(BaseModel):
    email : EmailStr
    password : str = Field(..., min_length=8)

class UserLogin(BaseModel):
    email : EmailStr
    password: str

class Logout(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token : str
    refresh_token: str
    token_type: str = "bearer"

# Schema for the Refresh Token request
class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str
    reset_token: str


# Schema to submit the new password using the email token
class ResetPasswordSubmit(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str