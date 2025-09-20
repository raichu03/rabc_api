from pydantic import BaseModel, Field

class HealthCheckResponse(BaseModel):
    """
    Response model for the API health check endpoint.
    """
    status: str = Field(..., example="OK")
    message: str = Field(..., example="The backend is live.")
    timestamp: str = Field(..., description="The current server time formatted as 'YYYY-MM-DD HH:MM:SS'.")

class UserDB(BaseModel):
    username: str
    passowrd: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None
    role: str | None = None

class Data(BaseModel):
    messsage: str