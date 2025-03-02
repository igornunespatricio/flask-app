# Flask Application with Docker

This is a Flask-based application for managing users, clients, and payments. It is containerized using Docker for ease of deployment and environment consistency.

## Project Structure

```bash
project_test/
│
├── app.py                        # The main Flask application file
├── db.py                         # Functions for interacting with the databases
├── requirements.txt              # Python dependencies required for the project
├── .dockerignore                 # Specifies which files to ignore when building Docker image
├── Dockerfile                    # The configuration file for building the Docker image
├── docker-compose.yml            # The Docker Compose file for container orchestration
├── entrypoint.sh                 # Entrypoint script for starting the application
├── users.db                      # SQLite database for storing user login data
│
├── databases/                    # Directory for user-specific databases (clients and payments data)
│   ├── user1.db                  # Example user-specific database
│   ├── user2.db                  # Example user-specific database
│   └── ...                       # Other user databases
│
├── static/                       # Directory for static files (CSS, JS, images)
│   ├── style.css                 # Example CSS file for the frontend
│   └── ...                       # Other static files
│
├── templates/                    # Directory for HTML template files
│   ├── home.html                 # Home page template
│   ├── clients.html              # Template for viewing/adding clients
│   ├── payments.html             # Template for viewing/adding payments
│   └── ...                       # Other HTML templates
```

## Data Persistence

- **users.db**: This database contains login credentials for all users of the application. It stores usernames, emails, and passwords for user authentication.
  
- **User-specific databases**: For each registered user, a separate SQLite database is created inside the `databases` folder. These user-specific databases store the **clients** and **payments** tables for that specific user. Each user has isolated data, and only the respective user can access their own client and payment information.

## Functionality

### Authentication
- Users can register and log in to the application.
- Passwords are securely hashed before being stored in the `users.db` file.

### Clients Management
- Once logged in, users can view, add, edit, or delete client information.
- Each user has a separate `clients` table in their own database.

### Payments Management
- Users can view and add payments related to their clients.
- Payments are stored in the `payments` table in each user-specific database.

### Data Isolation
- All data is isolated by user. Each user has their own SQLite database within the `databases` directory, and they can only access their own data.

## How to Run

1. **Clone the repository**:

    ```bash
    git clone <repository-url>
    cd project_test
    ```

2. **Install dependencies** (for local development without Docker):

    ```bash
    pip install -r requirements.txt
    ```

3. **Build the Docker image**:

    ```bash
    docker-compose build
    ```

4. **Run the application**:

    ```bash
    docker-compose up
    ```

    The application will be accessible at `http://localhost:5000`.

## Docker

### Building the Docker Image

The `Dockerfile` is set up to create an image for this Flask application. It installs dependencies, sets environment variables, and exposes port 5000.

### Docker Compose

The `docker-compose.yml` file simplifies the management of the application, including creating volumes for data persistence and exposing necessary ports.

## Notes

- The application uses **Docker volumes** to persist data across container restarts. The user-specific data is stored in the `databases` directory and will remain intact even if the container stops.
- The app runs in **production mode**, automatically selecting **Gunicorn** or **Waitress** based on the operating system.
- **Gunicorn** is used for Linux/macOS, and **Waitress** is used for Windows to ensure compatibility.

