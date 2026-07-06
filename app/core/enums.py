from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class ListingCondition(str, Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class ListingStatus(str, Enum):
    ACTIVE = "active"
    RESERVED = "reserved"
    SOLD = "sold"
    REMOVED = "removed"

class ListingSort(str, Enum):
    NEWEST = "newest"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"

class OTPPurpose(str, Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
