# MySQL Python App

## Description

This project is a Python application that connects to a MySQL database using Python and FastAPI. It provides a RESTful API for interacting with the database, allowing users to perform CRUD operations on users and items. The application is designed to be scalable and maintainable, following best practices for Python development.

## Installation

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    cd mysql_python_app
    ```

2.  Install Docker and Docker Compose. Ensure that Docker is running on your system.

3.  Install Make using Chocolatey (if you don't have it already):

    ```powershell
    Set-ExecutionPolicy Bypass -Scope Process -Force; `
    [System.Net.ServicePointManager]::SecurityProtocol = `
    [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
    iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

    choco install make
    ```

4.  Create the environment files:

    ```bash
    cp env/db/.env.example env/db/.env
    cp env/backend/.env.example env/backend/.env
    ```

    Modify the environment files with your specific settings. Update the database credentials in `env/db/.env` and the API settings in `env/backend/.env`.

5.  Start the application using Docker Compose:

    ```bash
    docker-compose up -d
    ```

    This command builds and starts the Docker containers for the MySQL database and the FastAPI application.

## Usage

The API is accessible at `http://localhost:8080`. You can use any HTTP client to interact with the API.

## Configuration

The application is configured using environment variables. The following environment variables are used:

*   **MySQL Database:**
    *   `MYSQL_ROOT_PASSWORD`: The root password for the MySQL database.
    *   `MYSQL_DATABASE`: The name of the MySQL database.
    *   `MYSQL_USER`: The username for the MySQL database.
    *   `MYSQL_PASSWORD`: The password for the MySQL database.
*   **API:**
    *   `SECRET_KEY`: The secret key used for JWT authentication.

## Contributing

Contributions are welcome! Please open a pull request with your changes.

## License

[License]

---

## Project Structure

```
backend/
├── app/
│   ├── api/
││└──routes/     
│   │       └── users.py         # User-related API endpoints
│   ├── core/
│   │   └── auth/                 # Authentication logic
│   ├── db/                   # Database connection and models
│   ├── models/               # Database models
│   ├── schemas/              # Data validation schemas
│   ├── services/             # Business logic services
│   ├── utils/                # Utility functions
│   ├── main.py               # Main application entry point
│   └── .env.example          # Example environment variables
├── Dockerfile                # Dockerfile for the FastAPI application
└── requirements.txt          # Python dependencies
docker-compose.yaml           # Docker Compose configuration
README.md                     # Project documentation
```

## API Endpoints

*   `GET /users` - Get all users
    *   Returns a list of all users in the database.
*   `GET /users/{id}` - Get a user by ID
    *   Returns a specific user based on their ID.
*   `POST /users` - Create a new user
    *   Creates a new user with the provided information.
*   `PUT /users/{id}` - Update a user
    *   Updates an existing user with the provided information.
*   `DELETE /users/{id}` - Delete a user
    *   Deletes a user from the database.

## Database Schema

The database schema consists of the following tables:

*   `users`: Stores user information.
    *   `id`: User ID (INT, Primary Key)
    *   `username`: Username (VARCHAR)
    *   `email`: Email address (VARCHAR)
    *   `password`: Hashed password (VARCHAR)
*   `items`: Stores item information.
    *   `id`: Item ID (INT, Primary Key)
    *   `name`: Item name (VARCHAR)
    *   `description`: Item description (TEXT)
    *   `owner_id`: Foreign key to the `users` table (INT)
*   `jti_blacklist`: Stores blacklisted JWT tokens.
    *   `jti`: JWT ID (VARCHAR, Primary Key)
    *   `created_at`: Timestamp of when the token was blacklisted (DATETIME)

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Users must authenticate to access certain endpoints.

## Error Handling

The API returns error messages in JSON format with appropriate HTTP status codes.

## Testing

To run the tests, use the following command:

```bash
pytest
```

This command executes the test suite and reports any failures.

## Deployment

The application can be deployed using Docker Compose. Ensure that your Docker environment is properly configured.
