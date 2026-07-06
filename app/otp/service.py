import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.enums import OTPPurpose
from app.core.security import hash_password, verify_password
from app.models.otp_verification import OTPVerification
from app.services.email import send_email

OTP_EXPIRY_MINUTES = 5


def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


def create_otp(
    email: str,
    purpose: OTPPurpose,
    db: Session,
):
    # Invalidate previous unused OTPs
    (
        db.query(OTPVerification)
        .filter(
            OTPVerification.email == email,
            OTPVerification.purpose == purpose,
            OTPVerification.verified_at.is_(None),
        )
        .update(
            {
                OTPVerification.verified_at: datetime.now(timezone.utc)
            },
            synchronize_session=False,
        )
    )

    db.commit()

    otp = generate_otp()

    otp_record = OTPVerification(
        email=email,
        otp_hash=hash_password(otp),
        purpose=purpose,
        expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )

    db.add(otp_record)
    db.commit()
    db.refresh(otp_record)

    if purpose == OTPPurpose.EMAIL_VERIFICATION:
        subject = "Verify your Dormly account"

        text_body = f"""
Dormly Email Verification

Your verification code is:

{otp}

This code expires in {OTP_EXPIRY_MINUTES} minutes.

If you didn't create this account, you can safely ignore this email.

— Dormly Team
"""

        html_body = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f5f7fb;font-family:Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
<tr>
<td align="center">

<table width="600" cellpadding="0" cellspacing="0"
style="background:#ffffff;border-radius:14px;padding:40px;">

<tr>
<td align="center">

<h1 style="margin:0;color:#2563eb;">
Dormly
</h1>

<p style="font-size:22px;font-weight:bold;margin-top:30px;">
Verify your email
</p>

<p style="color:#666;font-size:15px;line-height:1.6;">
Welcome to Dormly!
Use the verification code below to activate your account.
</p>

<div style="
margin:35px auto;
background:#eef4ff;
border:1px solid #dbeafe;
border-radius:12px;
padding:20px;
width:240px;
font-size:34px;
font-weight:bold;
letter-spacing:8px;
color:#2563eb;
text-align:center;
">
{otp}
</div>

<p style="color:#666;">
This code expires in
<b>{OTP_EXPIRY_MINUTES} minutes</b>.
</p>

<hr style="margin:35px 0;border:none;border-top:1px solid #eee;">

<p style="font-size:13px;color:#999;">
If you didn't create a Dormly account,
you can safely ignore this email.
</p>

</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""

    else:
        subject = "Dormly Password Reset"

        text_body = f"""
Dormly Password Reset

Your password reset code is:

{otp}

This code expires in {OTP_EXPIRY_MINUTES} minutes.

If you didn't request this, you can safely ignore this email.

— Dormly Team
"""

        html_body = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f5f7fb;font-family:Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
<tr>
<td align="center">

<table width="600" cellpadding="0" cellspacing="0"
style="background:#ffffff;border-radius:14px;padding:40px;">

<tr>
<td align="center">

<h1 style="margin:0;color:#2563eb;">
Dormly
</h1>

<p style="font-size:22px;font-weight:bold;margin-top:30px;">
Reset your password
</p>

<p style="color:#666;font-size:15px;line-height:1.6;">
Use the code below to reset your Dormly password.
</p>

<div style="
margin:35px auto;
background:#fff7ed;
border:1px solid #fed7aa;
border-radius:12px;
padding:20px;
width:240px;
font-size:34px;
font-weight:bold;
letter-spacing:8px;
color:#ea580c;
text-align:center;
">
{otp}
</div>

<p style="color:#666;">
This code expires in
<b>{OTP_EXPIRY_MINUTES} minutes</b>.
</p>

<hr style="margin:35px 0;border:none;border-top:1px solid #eee;">

<p style="font-size:13px;color:#999;">
If you didn't request this password reset,
you can safely ignore this email.
</p>

</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""

    try:
        send_email(
            to_email=email,
            subject=subject,
            text_body=text_body,
            html_body=html_body,
        )
    except Exception:
        db.delete(otp_record)
        db.commit()
        raise

    return otp


def verify_otp(
    email: str,
    otp: str,
    purpose: OTPPurpose,
    db: Session,
) -> bool:
    otp_record = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.email == email,
            OTPVerification.purpose == purpose,
            OTPVerification.verified_at.is_(None),
        )
        .order_by(OTPVerification.created_at.desc())
        .first()
    )

    if otp_record is None:
        return False

    if otp_record.expires_at < datetime.now(timezone.utc):
        return False

    if not verify_password(otp, otp_record.otp_hash):
        return False

    otp_record.verified_at = datetime.now(timezone.utc)

    db.commit()

    return True