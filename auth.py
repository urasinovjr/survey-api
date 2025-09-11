# auth.py (в корне проекта или в core/auth.py)
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from db.settings import Settings

settings = Settings()

# тянем секреты из .env (см. db/settings.py)
SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM: str = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# tokenUrl должен указывать на реальный эндпоинт получения токена
# если роутер будет подключён с prefix="/auth", то тут "auth/token"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Сгенерировать JWT. В payload ожидается как минимум "sub".
    """
    to_encode = data.copy()
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Декодирует токен и возвращает payload.
    Ожидаем, что при логине мы кладём в "sub" идентификатор/логин пользователя.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # sub по стандарту — строка; если у тебя int, можно привести через int(sub)
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        return {"sub": sub, **{k: v for k, v in payload.items() if k != "sub"}}
    except JWTError:
        raise credentials_exception
