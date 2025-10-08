# api/v1/auth_routes.py
from http.client import HTTPException
from fastapi import APIRouter, Depends, HTTPException, Header # type: ignore
from dependencies import get_user_repository
from repositories.sqlalchemy_user_repository import SqlAlchemyUserRepository
from services.user_service import UserService
from models.schemas.user import UserCreate, UserRead
from datetime import datetime, timedelta
from jose import jwt, JWTError # type: ignore

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ✅ Use the repository dependency you already defined
def get_user_service(
    repo: SqlAlchemyUserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(repo)

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, service: UserService = Depends(get_user_service)):
    return service.register_user(user.email, user.password)

@router.post("/login")
def login(user: UserCreate, service: UserService = Depends(get_user_service)):
    db_user = service.authenticate_user(user.email, user.password)
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"sub": db_user.email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/validate-token")
def validate_token(authorization: str = Header(...)):
    """
    Validates the provided JWT access token.
    Returns success if still valid, otherwise raises 401.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")

        if exp is None or datetime.utcnow().timestamp() > exp:
            raise HTTPException(status_code=401, detail="Token expired")

        return {"valid": True, "email": payload.get("sub")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
