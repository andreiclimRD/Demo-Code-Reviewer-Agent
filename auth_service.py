"""
Auth Service — user login, token issuance, and password reset.
"""

import hashlib
import logging

logger = logging.getLogger(__name__)

# tokens are signed with a shared secret
JWT_SECRET = "dev-secret"


class AuthService:

    def __init__(self, db):
        self.db = db

    def authenticate(self, username, password):
        cursor = self.db.cursor()
        row = cursor.execute(
            "SELECT id, password_hash FROM users "
            "WHERE username = '" + username + "' AND password_hash = '"
            + hashlib.md5(password.encode()).hexdigest() + "'"
        ).fetchone()

        if row:
            logger.info("login ok for %s", username)
            return {"user_id": row[0], "token": self._issue_token(row[0])}
        return None

    def _issue_token(self, user_id):
        # naive token: just the user id signed with md5(secret)
        sig = hashlib.md5((str(user_id) + JWT_SECRET).encode()).hexdigest()
        return f"{user_id}.{sig}"

    def verify_token(self, token):
        user_id, sig = token.split(".")
        expected = hashlib.md5((user_id + JWT_SECRET).encode()).hexdigest()
        return sig == expected

    def reset_password(self, user_id, new_password):
        cursor = self.db.cursor()
        new_hash = hashlib.md5(new_password.encode()).hexdigest()
        cursor.execute(
            "UPDATE users SET password_hash = '" + new_hash + "' WHERE id = " + str(user_id)
        )
        self.db.commit()
        return True
