# MySQL Python App

## Description

This project is a Python application that connects to a MySQL database. It provides an API for interacting with the database.

## Installation

1.  Clone the repository:

    ```bash
    git clone <repository_url>
    cd mysql_python_app
    ```

2.  Install Docker and Docker Compose.

3.  Create the environment files:

    ```bash
    cp env/db/.env.example env/db/.env
    cp env/backend/.env.example env/backend/.env
    ```

    Modify the environment files with your specific settings.

4.  Start the application using Docker Compose:

    ```bash
    docker-compose up -d
    ```

## Usage

The API is accessible at `http://localhost:8080`.

## Configuration

The application is configured using environment variables. The following environment variables are used:

*   **MySQL Database:**
    *   `MYSQL_ROOT_PASSWORD`
    *   `MYSQL_DATABASE`
    *   `MYSQL_USER`
    *   `MYSQL_PASSWORD`
*   **API:**
    *   `SECRET_KEY`

## Contributing

Contributions are welcome! Please open a pull request with your changes.

## License

[License]

---

## create a new repository on the command line
- echo "# mysql_python_app" >> README.md
- git init
- git add README.md
- git commit -m "first commit"
- git branch -M main
- git remote add origin https://github.com/PadmaDey/mysql_python_app.git
- git push -u origin main



## push an existing repository from the command line
- git remote add origin https://github.com/PadmaDey/mysql_python_app.git
- git branch -M main
- git push -u origin main


## create new branch
- git branch padma
- git checkout -b padma(when I am in main branch and want to switch to another branch)
- git switch -c padma

## to check MySQL  is working properly
- docker exec -it db mysql -u root -p
- password
- show databases;
- use    ;
- show tables;
- select * from    ;
