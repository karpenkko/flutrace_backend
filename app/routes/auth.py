from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.hash import bcrypt
from app.deps import get_db
from app.models import User
from app.schemas import AuthRequest, TokenPair, UserOut, UserUpdate
from app.auth.jwt import create_access_token, create_refresh_token, decode_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenPair)
async def login_or_register(auth: AuthRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == auth.email))
    user = result.scalars().first()

    if user:
        if not bcrypt.verify(auth.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid password")
    else:
        user = User(
            email=auth.email,
            hashed_password=bcrypt.hash(auth.password)
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    payload = {"sub": str(user.id)}
    return TokenPair(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        user_id=user.id
    )

@router.post("/refresh", response_model=TokenPair)
async def refresh_token(refresh_token: str):
    try:
        payload = decode_token(refresh_token)
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    payload = {"sub": user_id}
    return TokenPair(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        user_id=user_id
    )

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserOut)
async def update_me(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.email and data.email != current_user.email:
        result = await db.execute(
            select(User).where(User.email == data.email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already in use")

        current_user.email = data.email

    if data.password:
        current_user.hashed_password = bcrypt.hash(data.password)

    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.delete("/me")
async def delete_me(
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    await db.delete(current_user)
    await db.commit()
    return {"detail": "User deleted"}
