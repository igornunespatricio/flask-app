from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from db import UsersDatabase, UserSpecificDatabase

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session and flashing messages

# Initialize the global users database
users_db = UsersDatabase()

# Directory to store user-specific databases
databases_dir = "databases"
os.makedirs(databases_dir, exist_ok=True)


@app.route("/")
def index():
    """Redirect the root URL to the login page."""
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Authenticate the user
        if users_db.authenticate_user(email, password):
            # Store the user's email in the session after successful login
            session["user_email"] = email
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "error")

    return render_template("login.html")


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Create a new user-specific database
        user_db_path = os.path.join(databases_dir, f"{email}_db.sqlite")
        user_db = UserSpecificDatabase(user_db_path)

        # Add user to the UsersDatabase
        if users_db.add_user(email, password, user_db_path):
            flash("Account created successfully!", "success")
            return redirect(url_for("login"))
        else:
            flash("Email already exists!", "error")

    return render_template("create_account.html")


# Route for the home page (requires login)
@app.route("/home")
def home():
    if "user_email" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    return render_template("home.html", user_email=session["user_email"])


# Route for logging out
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/clients", methods=["GET"])
def clients():
    if "user_email" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    # Render a page for clients (you can customize this page)
    return render_template("clients.html")


import sqlite3


@app.route("/payments", methods=["GET"])
def payments():
    if "user_email" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    # Get the user-specific database path
    user_email = session["user_email"]
    user_db_path = os.path.join(databases_dir, f"{user_email}_db.sqlite")

    # Connect to the user-specific database
    try:
        db_connection = sqlite3.connect(user_db_path)
        cursor = db_connection.cursor()

        # Example query to fetch payment data
        query = """
        SELECT payments.id, clients.name AS client_name, payments.amount, payments.payment_date
        FROM payments
        JOIN clients ON payments.client_id = clients.id;
        """
        cursor.execute(query)
        payments = [
            {
                "id": row[0],
                "client_name": row[1],
                "amount": row[2],
                "payment_date": row[3],
            }
            for row in cursor.fetchall()
        ]
        db_connection.close()

        return render_template("payments.html", payments=payments)

    except sqlite3.Error as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
