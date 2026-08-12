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

# Schema to trigger the forgot password workflow
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

# Schema to submit the new password using the email token
class ResetPasswordSubmit(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

# Schema for updating password when logged in
class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

