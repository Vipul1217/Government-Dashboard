from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/otp/request")
def request_otp(payload: schemas.OtpRequestIn, db: Session = Depends(get_db)):
    code = "123456"
    return {"message": "OTP sent", "demo_code": code}


@router.post("/otp/verify", response_model=schemas.TokenOut)
def verify_otp(payload: schemas.OtpVerifyIn, db: Session = Depends(get_db)):
    if payload.code != "123456":
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    officer = db.query(models.Officer).filter(models.Officer.phone == payload.phone).first()
    if not officer:
        officer = models.Officer(name="Scheme Officer", phone=payload.phone)
        db.add(officer)
        db.commit()
        db.refresh(officer)

    token = auth.create_access_token({
        "sub": officer.id,
        "phone": officer.phone,
        "role": officer.role
    })
    return schemas.TokenOut(access_token=token)


@router.get("/me", response_model=schemas.OfficerOut)
def get_me(officer: models.Officer = Depends(auth.get_current_officer)):
    return officer