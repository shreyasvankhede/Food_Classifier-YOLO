import sqlite3
import hashlib
import os
from database import UserDB
AUTH_DB = "model/auth.sqlite"
os.makedirs("model", exist_ok=True)


class AuthManager:

    def __init__(self):
        self._init_db()

    # -------------------------
    # DB INITIALIZATION
    # -------------------------
    def _init_db(self):
        conn = sqlite3.connect(AUTH_DB)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    # -------------------------
    # PASSWORD HASHING
    # -------------------------
    def _hash(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    # -------------------------
    # REGISTER
    # -------------------------
    def register(self, username, password):
        username = username.strip().lower()
        password_hash = self._hash(password)
        user_hash=self._hash(username)

        conn = sqlite3.connect(AUTH_DB)
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            user=UserDB(user_hash)
            user.create_db()
            return True
        except sqlite3.IntegrityError:
            return False  # user already exists
        finally:
            conn.close()

    # -------------------------
    # LOGIN
    # -------------------------
    def login(self, username, password):
        username = username.strip().lower()
        password_hash = self._hash(password)

        conn = sqlite3.connect(AUTH_DB)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password_hash FROM users WHERE username=?",
            (username,)
        )
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return False

        return row[0] == password_hash

    # -------------------------
    # CHANGE PASSWORD
    # -------------------------
    def change_password(self, username, old_pass, new_pass):
        if not self.login(username, old_pass):
            return False

        new_hash = self._hash(new_pass)

        conn = sqlite3.connect(AUTH_DB)
        conn.execute(
            "UPDATE users SET password_hash=? WHERE username=?",
            (new_hash, username)
        )
        conn.commit()
        conn.close()
        return True
