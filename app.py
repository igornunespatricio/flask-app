from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from db import UsersDatabase, UserSpecificDatabase
import sqlite3
from utils import delete_file  # Import delete_file from utils.py

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

    try:
        if os.path.exists(user_db_path):
            # Explicitly close the database connection before deletion
            conn = sqlite3.connect(user_db_path)
            conn.close()  # ✅ Ensure the DB connection is closed first

            # Use delete_file() to terminate processes using the file and then delete it
            delete_file(user_db_path)

        # Delete the user's record from users.db
        users_db.execute_query("DELETE FROM users WHERE email = ?", (user_email,))

        # Clear session after successful deletion
        session.clear()

        flash("Your account and data have been successfully deleted.", "success")
    except Exception as e:
        flash(f"Error deleting account: {e}", "error")
        print(e)

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

    # Attempt to add the client
    message = user_db.add_client(name, email, status)

    # Display appropriate flash message
    if message == "Email is already registered.":
        flash(message, "error")  # Show error message if email exists
    else:
        flash(message, "success")  # Show success message if client is added

    return redirect(url_for("clients"))


@app.route("/delete_client", methods=["POST"])
def delete_client():
    if "user_email" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    # Get the client ID from the form
    client_id = request.form["client_id"]

    # Get the user-specific database path
    user_email = session["user_email"]
    user_db_path = os.path.join(databases_dir, f"{user_email}_db.sqlite")
    user_db = UserSpecificDatabase(user_db_path)

    # Delete the client
    user_db.delete_client(client_id)
    flash("Client deleted successfully!", "success")
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
        user_db = UserSpecificDatabase(user_db_path)

        # Fetch all payments and clients for the dropdown
        payments = (
            user_db.get_all_payments()
        )  # Retrieve payment details (client name, amount, date, etc.)
        clients = (
            user_db.get_clients_dropdown()
        )  # Retrieve client IDs and names for the dropdown

        # Render the payments page with both payments and clients data
        return render_template("payments.html", payments=payments, clients=clients)

    except sqlite3.Error as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for("home"))


@app.route("/add_payment", methods=["GET", "POST"])
def add_payment():
    if "user_email" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    # Get the user-specific database path
    user_email = session["user_email"]
    user_db_path = os.path.join(databases_dir, f"{user_email}_db.sqlite")
    user_db = UserSpecificDatabase(user_db_path)

    if request.method == "POST":
        # Extract form data
        client_id = request.form["client_id"]
        amount = float(request.form["amount"])
        payment_date = request.form["payment_date"]

        # Call the database method to add the payment
        user_db.add_payment(client_id, amount, payment_date)
        flash("Payment added successfully!", "success")

        # Redirect to the payments page
        return redirect(url_for("payments"))

    # Fetch clients for the dropdown list
    clients = user_db.get_clients_dropdown()  # Retrieves only (id, name)
    return render_template("add_payment.html", clients=clients)


@app.route("/delete_payment", methods=["POST"])
def delete_payment():
    if "user_email" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    # Get the user-specific database path
    user_email = session["user_email"]
    user_db_path = os.path.join(databases_dir, f"{user_email}_db.sqlite")
    user_db = UserSpecificDatabase(user_db_path)

    # Get the payment ID from the form
    payment_id = request.form["payment_id"]

    # Call the delete_payment function
    user_db.delete_payment(payment_id)
    flash("Payment deleted successfully!", "success")

    return redirect(url_for("payments"))


@app.route("/edit_client", methods=["POST"])
def edit_client():
    if "user_email" not in session:
        flash("Please log in to access this page.", "error")
        return redirect(url_for("login"))

    # Get the user-specific database path
    user_email = session["user_email"]
    user_db_path = os.path.join(databases_dir, f"{user_email}_db.sqlite")
    user_db = UserSpecificDatabase(user_db_path)

    # Get client data from form
    client_id = request.form["client_id"]
    name = request.form["name"]
    email = request.form["email"]
    status = request.form["status"]

    # Update the client in the database
    user_db.update_client(client_id, name, email, status)
    flash("Client updated successfully!", "success")
    return redirect(url_for("clients"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
