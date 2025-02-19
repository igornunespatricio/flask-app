import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def connect(self):
        """Establish a connection to the database."""
        return sqlite3.connect(self.db_path)

    def execute_query(self, query, params=()):
        """Execute a query and commit changes."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def fetch_one(self, query, params=()):
        """Fetch a single record from the database."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result

    def fetch_all(self, query, params=()):
        """Fetch all records from the database."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results


import hashlib
import os


class UsersDatabase(DatabaseManager):
    def __init__(self):
        # Set a valid path for the users database
        db_path = os.path.join(os.getcwd(), "users.db")
        super().__init__(db_path)
        self._create_users_table()

    def _create_users_table(self):
        query = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                db_path TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """
        self.execute_query(query)

    def hash_password(self, password, salt):
        """Generate a hashed password using SHA-256 and a salt."""
        salted_password = salt + password
        return hashlib.sha256(salted_password.encode("utf-8")).hexdigest()

    def add_user(self, email, password, db_path):
        """Add a user to the database with a hashed password."""
        salt = os.urandom(16).hex()  # Generate a random salt
        password_hash = self.hash_password(password, salt)
        query = """
            INSERT INTO users (email, password_hash, salt, db_path)
            VALUES (?, ?, ?, ?)
        """
        try:
            self.execute_query(query, (email, password_hash, salt, db_path))
            return True
        except sqlite3.IntegrityError:  # Email already exists
            return False

    def authenticate_user(self, email, password):
        """Check if the email and password match an existing user."""
        query = """
            SELECT password_hash, salt FROM users WHERE email = ?
        """
        result = self.fetch_one(query, (email,))
        if result:
            stored_hash, salt = result
            input_hash = self.hash_password(password, salt)
            return input_hash == stored_hash
        return False


class UserSpecificDatabase(DatabaseManager):
    def __init__(self, db_path):
        super().__init__(db_path)
        self.init_user_db()

    def init_user_db(self):
        """Initialize the user-specific database with two tables: clients and payments."""
        self.execute_query(
            """CREATE TABLE IF NOT EXISTS clients (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                email TEXT NOT NULL,
                                status TEXT NOT NULL,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                            )"""
        )

        self.execute_query(
            """CREATE TABLE IF NOT EXISTS payments (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                client_id INTEGER NOT NULL,
                                amount REAL NOT NULL,
                                payment_date DATE NOT NULL,
                                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                                FOREIGN KEY (client_id) REFERENCES clients (id)
                            )"""
        )

    def add_client(self, name, email, status):
        """Add a new client."""
        self.execute_query(
            "INSERT INTO clients (name, email, status) VALUES (?, ?, ?)",
            (name, email, status),
        )

    def add_payment(self, client_id, amount, payment_date):
        """Add a new payment."""
        self.execute_query(
            "INSERT INTO payments (client_id, amount, payment_date) VALUES (?, ?, ?)",
            (client_id, amount, payment_date),
        )

    def get_clients(self):
        """Retrieve all clients."""
        return self.fetch_all("SELECT * FROM clients")

    def get_payments(self):
        """Retrieve all payments."""
        return self.fetch_all("SELECT * FROM payments")
