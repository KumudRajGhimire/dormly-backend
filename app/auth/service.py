from sqlalchemy.orm import Session

from app.models.campus import Campus


def get_campus_from_email(email: str, db: Session) -> Campus | None:
    domain = email.split("@", 1)[1].strip().lower()

    return (
        db.query(Campus)
        .filter(Campus.email_domain == domain)
        .first()
    )