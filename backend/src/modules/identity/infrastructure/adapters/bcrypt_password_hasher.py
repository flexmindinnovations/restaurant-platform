import bcrypt

from modules.identity.application.ports.password_hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode("utf-8")

    def verify(self, password: str, hashed: str) -> bool:
        password_bytes = password.encode("utf-8")
        hashed_bytes = hashed.encode("utf-8")
        try:
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            return False
