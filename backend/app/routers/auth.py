from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserOut, Token
from app.utils.security import hash_password, verify_password, create_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already taken")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        role="employee"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id, user.role)
    return {"access_token": token, "user": user}


@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong username or password")

    token = create_token(user.id, user.role)
    return {"access_token": token, "user": user}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
