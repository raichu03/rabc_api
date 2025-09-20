import os
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status
import uvicorn
from fastapi.security import OAuth2PasswordRequestForm


from models import HealthCheckResponse, Token
from utils import get_users_db, get_user, verify_password, create_access_token
import endpoints

app = FastAPI(
    title='Just a APP',
    description='Role-Based Access control API for CRUD operations',
    responses={404: {"description": "Not found"}},
)

app.include_router(endpoints.router)

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint for user authentication."""
    users_db = get_users_db()
    user = get_user(users_db, form_data.username)
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]},
        expires_delta=3600
    )
    return {"access_token": access_token, "token_type": "bearer"}

### Health Check ###
@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a health check",
    response_model=HealthCheckResponse,
    response_description="Return HTTP Status Code 200 (OK)"
)
async def health_check() -> HealthCheckResponse:
    """
    Performs a simple health check to ensure the backend is running.
    
    Returns:
        A JSON object with a status, a message, and the current timestamp.
    """

    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return HealthCheckResponse(
        status="OK",
        message="The backend is running.",
        timestamp=current_time_str
    )


if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)