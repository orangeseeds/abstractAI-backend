from . import schemas, models
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from .database import get_db
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT
router = APIRouter()


@router.post("/user/signup", tags=["user"])
async def create_user(payload: schemas.UserSchema, db: Session = Depends(get_db)):
    # replace with db call, making sure to hash the password first
    new_user = models.User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "status": "success",
        "jwt": signJWT(new_user.email)
    }


@router.post("/user/login", tags=["user"])
async def user_login(payload: schemas.UserLoginSchema, db: Session = Depends(get_db)):

    user_query = db.query(models.User).filter(
        models.User.email == payload.email)
    db_user = user_query.first()

    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No user with this email: {payload.email} found')

    hashed_password = payload.password
    if not db_user.password == hashed_password:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Provided email and password didnot match')

    return {
        "status": "success",
        "jwt": signJWT(db_user.email),
    }


@router.get('/', dependencies=[Depends(JWTBearer())])
def get_summaries(db: Session = Depends(get_db), limit: int = 10, page: int = 1, search: str = ''):
    skip = (page - 1) * limit

    summaries = db.query(models.Summary).filter(
        models.Summary.domain.contains(search)).limit(limit).offset(skip).all()
    return {'status': 'success', 'results': len(summaries), 'summaries': summaries}


@router.post('/', status_code=status.HTTP_201_CREATED, dependencies=[Depends(JWTBearer())])
def generate_summary(payload: schemas.SummaryRequestSchema, db: Session = Depends(get_db)):
    new_summary = models.Summary(**payload.dict())

    # call the ML model and put the response here!!
    new_summary.response = "generated response"
    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)
    return {"status": "success", "summary": new_summary}


@router.patch('/{summaryId}', dependencies=[Depends(JWTBearer())])
def update_note(summaryId: str, payload: schemas.SummaryBaseSchema, db: Session = Depends(get_db)):
    summary_query = db.query(models.Summary).filter(
        models.Summary.id == summaryId)
    db_summary = summary_query.first()

    if not db_summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No note with this id: {summaryId} found')
    update_data = payload.dict(exclude_unset=True)
    summary_query.filter(models.Note.id == summaryId).update(update_data,
                                                             synchronize_session=False)
    db.commit()
    db.refresh(db_summary)
    return {"status": "success", "summary": db_summary}


@router.get('/{summaryId}', dependencies=[Depends(JWTBearer())])
def get_post(summaryId: str, db: Session = Depends(get_db)):
    summary = db.query(models.Summary).filter(
        models.Summary.id == summaryId).first()
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No summary with this id: {id} found")
    return {"status": "success", "summary": summary}


@router.delete('/{noteId}', dependencies=[Depends(JWTBearer())])
def delete_post(noteId: str, db: Session = Depends(get_db)):
    note_query = db.query(models.Note).filter(models.Note.id == noteId)
    note = note_query.first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No note with this id: {id} found')
    note_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
