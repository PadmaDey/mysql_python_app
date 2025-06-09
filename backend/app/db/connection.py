from app.core.config import settings
from app.services.logger import logger
from mysql.connector import connect
from mysql.connector.connection import MySQLConnection


def connect_to_db():
    try:
        conn = connect(
            host=settings.MYSQL_HOST, 
            port=settings.MYSQL_PORT, 
            user=settings.MYSQL_USER, 
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
            auth_plugin='mysql_native_password'  # Ensures compatibility
            )

        if conn.is_connected():
            logger.info("Successfully connected to MySQL")
            return conn

    except Exception as e:
        logger.exception("Failed to connect to MySQL: %s", e)
        raise


def get_cursor(conn: MySQLConnection):
    try:
        return conn.cursor()
    except Exception as e:
        logger.exception("Failed to get cursor: %s", e)
        raise


conn = connect_to_db()
cursor = get_cursor(conn)
