# api/auth.py
from fastapi import APIRouter, Depends
from auth import (
    create_access_token,
    get_current_user,
)  # 👈 добавляем сюда get_current_user

router = APIRouter()


@router.post("/token")
def issue_token():
    """
    ВРЕМЕННО: выдаём токен без проверки пользователя.
    Потом заменишь на реальную проверку логина/пароля.
    """
    token = create_access_token({"sub": "user1"})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(current: dict = Depends(get_current_user)):
    """Вернуть информацию о текущем пользователе из токена"""
    return current
