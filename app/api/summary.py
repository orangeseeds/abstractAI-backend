from app import schemas, models
from sqlalchemy.orm import Session
from fastapi import (
    Depends,
    HTTPException,
    status,
    APIRouter,
    Response,
)
from app.database import get_db
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_bearer import get_auth_user
from app.ml.model import summarize_text

router = APIRouter()


@router.get("/", dependencies=[Depends(JWTBearer())])
def get_summaries(
    db: Session = Depends(get_db),
    limit: int = 10,
    page: int = 1,
    domain: str = "",
):
    skip = (page - 1) * limit

    domain_summaries = (
        db.query(models.Summary)
        .filter(models.Summary.domain == domain)
        .order_by(models.Summary.createdAt.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )
    return {
        "status": "success",
        "results": len(domain_summaries),
        "summaries": domain_summaries,
    }


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(JWTBearer())],
)
def generate_summary(
    payload: schemas.SummaryRequestSchema,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_auth_user),
):
    new_summary = models.Summary(**payload.dict(), user_id=user_id)
    # call the ML model and put the response here!!
    # this summarize_text function simulates the call to the ml model
    new_summary.response = summarize_text(payload.request)
    db.add(new_summary)
    db.commit()
    db.refresh(new_summary)
    return {"status": "success", "summary": new_summary}


@router.patch("/{summaryId}", dependencies=[Depends(JWTBearer())])
def update_summary(
    summaryId: str,
    payload: schemas.SummaryBaseSchema,
    db: Session = Depends(get_db),
):
    summary_query = db.query(models.Summary).filter(
        models.Summary.id == summaryId
    )
    db_summary = summary_query.first()

    if not db_summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No summary with this id: {summaryId} found",
        )
    update_data = payload.dict(exclude_unset=True)
    summary_query.filter(models.Summary.id == summaryId).update(
        update_data, synchronize_session=False
    )
    db.commit()
    db.refresh(db_summary)
    return {"status": "success", "summary": db_summary}


@router.get("/{summaryId}", dependencies=[Depends(JWTBearer())])
def get_post(summaryId: str, db: Session = Depends(get_db)):
    summary = (
        db.query(models.Summary)
        .filter(models.Summary.id == summaryId)
        .first()
    )
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No summary with this id: {id} found",
        )
    return {"status": "success", "summary": summary}


@router.delete("/{summaryId}", dependencies=[Depends(JWTBearer())])
def delete_post(summaryId: str, db: Session = Depends(get_db)):
    summary_query = db.query(models.Summary).filter(
        models.summary.id == summaryId
    )
    summary = summary_query.first()
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No summary with this id: {id} found",
        )
    summary_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
