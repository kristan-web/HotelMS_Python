"""
Password Utility
=================
Provides bcrypt-based password hashing and verification.

Usage:
    from utils.password_utils import hash_password, verify_password
    hashed = hash_password("mypassword")
    ok = verify_password("mypassword", hashed)
"""

import bcrypt


def hash_password(plain_text: str) -> str:
    """Hash a plain-text password with bcrypt. Returns the hash as a string."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_text.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_text: str, hashed: str) -> bool:
    """Return True if plain_text matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_text.encode("utf-8"),
                              hashed.encode("utf-8"))
    except Exception:
        return False