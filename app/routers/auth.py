import random
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.utils import send_email, hash_password

router = APIRouter()

# ----------------- FORGOT PASSWORD -----------------
@router.post("/auth/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = str(random.randint(100000, 999999))

    user.reset_code = otp
    user.reset_expires_at = datetime.utcnow() + timedelta(minutes=10)

    db.commit()

    send_email(
        to=email,
        subject="Your Password Reset Code",
        body=f"Your verification code is: {otp}"
    )

    return {"message": "Verification code sent to email"}

# ----------------- VERIFY OTP -----------------
@router.post("/auth/verify-otp")
def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.reset_code != otp:
        raise HTTPException(status_code=400, detail="Invalid code")

    if datetime.utcnow() > (user.reset_expires_at or datetime.utcnow()):
        raise HTTPException(status_code=400, detail="Code expired")

    # Mark the user as verified for reset
    user.reset_verified = True
    db.commit()

    return {"message": "OTP verified"}

# ----------------- RESET PASSWORD -----------------
@router.post("/auth/reset-password")
def reset_password(email: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Require OTP verification before resetting password
    if not getattr(user, "reset_verified", False):
        raise HTTPException(status_code=403, detail="OTP not verified")

    # Update password
    user.password = hash_password(new_password)

    # Clear reset fields
    user.reset_code = None
    user.reset_expires_at = None
    user.reset_verified = False

    db.commit()

    return {"message": "Password reset successful"}
