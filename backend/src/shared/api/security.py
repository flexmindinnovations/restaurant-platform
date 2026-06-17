from typing import Any

import jwt


def decode_token(token: str, secret_key: str, algorithm: str) -> dict[str, Any]:
    """Decode and verify a JWT token.

    Returns the token payload if valid, otherwise raises a jwt.PyJWTError.
    """
    return jwt.decode(token, secret_key, algorithms=[algorithm])


def create_token(payload: dict[str, Any], secret_key: str, algorithm: str) -> str:
    """Encode a payload into a JWT token."""
    return jwt.encode(payload, secret_key, algorithm=algorithm)
