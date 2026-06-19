from app.db.session import sessionLocal

import app.db.base_model

from app.models.category import Category
from app.models.campus import Campus
from app.models.hostel import Hostel


def seed_categories(db):
    categories = [
        ("Electronics", "electronics"),
        ("Books", "books"),
        ("Furniture", "furniture"),
        ("Cycles", "cycles"),
        ("Fashion", "fashion"),
        ("Gaming", "gaming"),
        ("Notes", "notes"),
        ("Others", "others"),
    ]

    for name, slug in categories:
        exists = (
            db.query(Category)
            .filter(Category.slug == slug)
            .first()
        )

        if not exists:
            db.add(
                Category(
                    name=name,
                    slug=slug
                )
            )


def seed_campuses(db):
    campuses = [
        ("BMS College of Engineering", "bmsce", "Bangalore", "Karnataka"),
        ("RV College of Engineering", "rvce", "Bangalore", "Karnataka"),
        ("PES University", "pes", "Bangalore", "Karnataka"),
        ("MS Ramaiah Institute of Technology", "msrit", "Bangalore", "Karnataka"),
    ]

    for name, slug, city, state in campuses:
        exists = (
            db.query(Campus)
            .filter(Campus.slug == slug)
            .first()
        )

        if not exists:
            db.add(
                Campus(
                    name=name,
                    slug=slug,
                    city=city,
                    state=state
                )
            )

    db.commit()


def seed_hostels(db):
    bmsce = db.query(Campus).filter(
        Campus.slug == "bmsce"
    ).first()

    rvce = db.query(Campus).filter(
        Campus.slug == "rvce"
    ).first()

    pes = db.query(Campus).filter(
        Campus.slug == "pes"
    ).first()

    msrit = db.query(Campus).filter(
        Campus.slug == "msrit"
    ).first()

    hostels = [
        (bmsce.id, "Boys Hostel A", "boys-a"),
        (bmsce.id, "Boys Hostel B", "boys-b"),
        (bmsce.id, "Girls Hostel", "girls"),

        (rvce.id, "Boys Hostel", "boys"),
        (rvce.id, "Girls Hostel", "girls"),

        (pes.id, "Boys Hostel", "boys"),
        (pes.id, "Girls Hostel", "girls"),

        (msrit.id, "Boys Hostel", "boys"),
        (msrit.id, "Girls Hostel", "girls"),
    ]

    for campus_id, name, slug in hostels:
        exists = (
            db.query(Hostel)
            .filter(
                Hostel.campus_id == campus_id,
                Hostel.slug == slug
            )
            .first()
        )

        if not exists:
            db.add(
                Hostel(
                    campus_id=campus_id,
                    name=name,
                    slug=slug
                )
            )


def main():
    db = sessionLocal()

    try:
        seed_categories(db)
        seed_campuses(db)
        seed_hostels(db)

        db.commit()

        print("Seed completed successfully")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()