from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from db import UsersDatabase, UserSpecificDatabase
import sqlite3

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
            # Store the user's email in the session
            session["user_email"] = email
            flash("Account created successfully! You are now logged in.", "success")
            return redirect(url_for("home"))
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


@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "user_email" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    user_email = session["user_email"]

    # Fetch the user-specific database path from users.db
    user_data = users_db.fetch_one(
        "SELECT db_path FROM users WHERE email = ?", (user_email,)
    )
    if not user_data:
        flash("User not found.", "error")
        return redirect(url_for("home"))

    user_db_path = user_data[0]

    # Delete the user's record from users.db
    users_db.execute_query("DELETE FROM users WHERE email = ?", (user_email,))

    # Delete the user-specific database file
    if os.path.exists(user_db_path):
        os.remove(user_db_path)

    # Clear session and notify the user
    session.clear()
    flash("Your account and data have been successfully deleted.", "success")
    return redirect(url_for("login"))


@app.route("/clients", methods=["GET"])
def clients():
    if "user_email" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    # Get the user-specific database path
    user_email = session["user_email"]
    user_db_path = os.path.join(databases_dir, f"{user_email}_db.sqlite")
    user_db = UserSpecificDatabase(user_db_path)

    # Get the list of clients
    clients = user_db.get_clients()

    return render_template("clients.html", clients=clients)


@app.route("/add_client", methods=["POST"])
def add_client():
    if "user_email" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    # Get form data
    name = request.form["name"]
    email = request.form["email"]
    status = request.form["status"]

    # Get the user-specific database path
    user_email = session["user_email"]
    user_db_path = os.path.join(databases_dir, f"{user_email}_db.sqlite")
    user_db = UserSpecificDatabase(user_db_path)

    # Add the new client
    user_db.add_client(name, email, status)
    flash("Client added successfully!", "success")
    return redirect(url_for("clients"))


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
