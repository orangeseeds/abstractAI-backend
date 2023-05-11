from app import schemas, models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter
from app.database import get_db
from app.auth.auth_handler import signJWT
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_bearer import get_auth_user

router = APIRouter()


@router.post("/signup")
async def create_user(
    payload: schemas.UserSchema, db: Session = Depends(get_db)
):
    new_user = models.User(**payload.dict())
    new_user.password = models.get_password_hash(new_user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "jwt": signJWT(str(new_user.id))}


@router.post("/login")
async def user_login(
    payload: schemas.UserLoginSchema, db: Session = Depends(get_db)
):
    user_query = db.query(models.User).filter(
        models.User.email == payload.email
    )
    db_user = user_query.first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user with this email: {payload.email} found",
        )

    if not models.verify_password(payload.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provided email and password didnot match",
        )

    return {
        "status": "success",
        "jwt": signJWT(str(db_user.id)),
    }


@router.post(
    "/refresh",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(JWTBearer())],
)
def refresh_token(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_auth_user),
):
    return {"status": "success", "jwt": signJWT(user_id)}
