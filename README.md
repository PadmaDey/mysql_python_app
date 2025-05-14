docker run --name mysql -e MYSQL_ROOT_HOST=localhost -e MYSQL_ROOT_PASSWORD=Klizos@123 -e MYSQL_ROOT_USER=root -d mysql:9.3


docker compose build
docker compose up -d mysql_app