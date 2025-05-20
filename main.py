import re
from dotenv import load_dotenv
import mysql.connector as mysql_conn
from getpass import getpass
from log_config import logger

def get_connection():
    load_dotenv()
    try:
        host = input("Enter your MySQL Hostname (e.g., localhost): ").strip()
        user = input("Enter your MySQL Username (e.g., root): ").strip()
        port_input = input("Enter your port where MySQL Server is running (e.g., 3306): ")
        if not port_input.isdigit():
            raise ValueError("Port must be a number.")
        port = int(port_input)
        password = getpass("Enter your MySQL Password: ").strip()
        # password = input("Enter your MySQL Password: ").strip()

        # host = os.getenv("host")
        # user = os.getenv("user")
        # port = int(os.getenv("port", 3306))
        # password = os.getenv("password")

    except ValueError as ve:
        logger.warning("Port must be a number.: %s", ve)
        print(f"Port must be a number.: {ve}")
        raise
    except mysql_conn.Error as err:
        logger.error("Failed to connect with MySQL: %s", err)
        print(f"Failed to connect with MySQL: {err}")
        raise
    except Exception as e:
        logger.error("Failed to connect with MySQL: %s", e)
        print(f"Failed to connect with MySQL: {e}")
        raise


    try:    
        if not all([host, user, password]):
            raise ValueError()
    
        conn = mysql_conn.connect(
            host=host,
            user=user,
            port =port,
            password=password
        )

        if conn.is_connected():
            logger.info(f"Successfully Connected to MySQL")
            print(f"Successfully Connected to MySQL\n")
            return conn
        
    except ValueError as ve:
        logger.warning("Missing required environment variables: host, user, or password: %s", ve)
        print(f"Missing required environment variables: host, user, or password: {ve}")
        raise
    except mysql_conn.Error as err:
        logger.error("Failed to connect with MySQL: %s", err)
        print(f"Failed to connect with MySQL: {err}")
        raise
    except Exception as e:
        logger.error("Failed to connect with MySQL: %s", e)
        print(f"Failed to connect with MySQL: {e}")
        raise
 
def show_databases(cursor):
    try:
        cursor.execute("show databases;")
        databases = cursor.fetchall()
        if not databases:
            logger.warning("No databases found.")
            print("No databases found.")
        else:
            logger.info("All existing databases: - ")
            print("All existing databases: - ")
            for db in databases:
                print(f"- {db[0]}")

    except mysql_conn.Error as err:
        logger.error("MySQL Error while fetching databases: %s", err)
        print(f"MySQL Error while fetching databases: {err}")
    except Exception as e:
        logger.error("Unexpected error while displaying databases: %s", e)
        print(f"Unexpected error while displaying databases: {e}")

def create_database(cursor):
    try:
        db_name = input("\nEnter the name of the database you want to create: ").strip()
        if not re.match(r"[A-Za-z_][A-Za-z0-9_]*$", db_name):
            raise ValueError("Invalid database name. Use only letters, numbers, and underscores, and it must not start with a number.")
        
        query = f"create database if not exists {db_name};"
        cursor.execute(query)
        
        logger.info("Database %s created or already exists.", db_name)
        print(f"Database {db_name} created or already exists.")
        return db_name
    
    except mysql_conn.Error as err:
        logger.error("MySQL error while creating database %s: %s", db_name, err)
        print(f"MySQL error while creating database {db_name}: {err}")
    except Exception as e:
        logger.error("General error while creating database %s: %s", db_name, e)
        print(f"General error while creating database{db_name}: {e}")

def use_database(cursor, db_name):
    try:
        cursor.execute(f"use {db_name};")
        logger.info("Switched to database: %s", db_name)
        print(f"Switched to database: {db_name}")
    
    except mysql_conn.Error as err:
        logger.error("MySQL Error while switching to database %s: %s", db_name, err)
        print(f"MySQL Error while switching to database '{db_name}': {err}")
    except Exception as e:
        logger.error("Unexpected error while switching to database %s: %s", db_name, e)
        print(f"Unexpected error while switching to database '{db_name}': {e}")

def show_tables(cursor):
    try:
        cursor.execute("show tables;")
        tables = cursor.fetchall()
        if tables:
            logger.info("All exixting tables:")
            print("All exixting tables: -")
            for table in tables:
                print(f"- {table[0]}")
        else:
            logger.warning("No tables found in the current database.")
            print("No tables found in the current database.")

    except mysql_conn.Error as err:
        logger.error("MySQL Error while fetching tables: %s", err)
        print(f"MySQL Error while fetching tables: {err}")
    except Exception as e:
        logger.error("Unexpected error while displaying tables: %s", e)
        print(f"Unexpected error while displaying tables: {e}")

def create_table(cursor):
    try:
        table_name = input("Enter the name of the table you would like to create: ").strip()
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table_name):
            raise ValueError("Invalid table name. It must start with a letter or underscore and contain only alphanumeric characters or underscores.")
        
        column_definitions = input("Enter column definitions (e.g., emp_id int, emp_name varchar(50)): ").strip()
        if not column_definitions:
            raise ValueError("Column definitions cannot be empty.")
        
        query = f"create table if not exists {table_name} ({column_definitions});"
        cursor.execute(query)
        logger.info("Table %s created (or already exists) with columns: %s", table_name, column_definitions)
        print(f"Table '{table_name}' created (or already exists) with columns: {column_definitions}")
        return table_name

    except mysql_conn.Error as err:
        logger.error("MySQL error while creating table %s: %s", table_name, err)
        print(f"MySQL error while creating table '{table_name}': {err}")
    except ValueError as ve:
        logger.error("Input validation error: %s", ve)
        print(f"Input validation error: {ve}")
    except Exception as e:
        logger.error("Unexpected error while creating table %s: %s", table_name, e)
        print(f"Unexpected error while creating table '{table_name}': {e}")

def insert_data(cursor, table_name):
    try:
        cursor.execute(f"describe {table_name};")
        columns = [col[0] for col in cursor.fetchall()]
        if not columns:
            raise ValueError(f"Table '{table_name}' has no columns to insert data into.")

        logger.info("Table columns: %s", columns)
        print(f"Table columns: {columns}")
        
        values_input = input(f"Enter comma-separated values for {columns}: ").strip()
        values = [v.strip() for v in values_input.split(',')]
        if len(values) != len(columns):
            raise ValueError(f"Expected {len(columns)} values, but got {len(values)}.")

        placeholders = ", ".join(["%s"] * len(values))
        query = f"insert into {table_name} ({', '.join(columns)}) values ({placeholders});"
        
        cursor.execute(query, values)
        logger.info("Data inserted successfully into table: %s", table_name)
        print(f"Data inserted successfully into table: {table_name}")

    except mysql_conn.Error as err:
        logger.error("MySQL Error during insertion into %s: %s", table_name, err)
        print(f"MySQL Error during insertion into '{table_name}': {err}")
    except ValueError as ve:
        logger.error("Input Error: %s", ve)
        print(f"Input Error: {ve}")
    except Exception as e:
        logger.error("Unexpected Error while inserting data into %s: %s", table_name, e)
        print(f"Unexpected Error while inserting data into '{table_name}': {e}")

def update_data(cursor, table_name):
    try:
        columns_input = input("Enter column names to update (comma-separated): ").strip()
        values_input = input("Enter corresponding values (comma-separated): ").strip()
        condition = input("Enter the WHERE condition (e.g., id=1): ").strip()

        columns = [col.strip() for col in columns_input.split(",")]
        values = [val.strip() for val in values_input.split(",")]

        if not columns or not values or not condition:
            raise ValueError("Column names, values, and condition are all required.")

        if len(columns) != len(values):
            raise ValueError("Mismatch: Number of columns and values must be the same.")

        set_clause = ", ".join([f"{col} = %s" for col in columns])
        query = f"update {table_name} set {set_clause} where {condition};"
        cursor.execute(query, values)
        logger.info("Successfully updated records in %s where %s", table_name, condition)
        print(f"Successfully updated records in '{table_name}' where {condition}")

    except mysql_conn.Error as err:
        logger.error("MySQL Error during update: %s", err)
        print(f"MySQL Error during update: {err}")
    except ValueError as ve:
        logger.warning("Input Error: %s", ve)
        print(f"Input Error: {ve}")
    except Exception as e:
        logger.error("Unexpected error during update: %s", e)
        print(f"Unexpected error during update: {e}")

def alter_data(cursor, table_name):
    try:
        operation = input("Enter the 'alter' operation (add/drop column/modify column): ").strip()
        column_def = input("Enter the column name and datatype (e.g., age int): ").strip()

        allowed_ops = ['add', 'drop column', 'modify column']
        if operation not in allowed_ops:
            raise ValueError(f"Unsupported alter operation. Allowed operations: {', '.join(allowed_ops)}")
        
        query = f"alter table {table_name} {operation} {column_def};"
        cursor.execute (query)
        logger.info(f"Table '{table_name}' altered successfully with operation: {operation}")
        print(f"Table '{table_name}' altered successfully with operation: {operation}")

    except mysql_conn.Error as err:
        logger.error(f"MySQL Error during alter: {err}")
        print(f"MySQL Error during alter: {err}")
    except ValueError as ve:
        logger.error(f"Input Error: {ve}")
        print(f"Input Error: {ve}")
    except Exception as e:
        logger.error(f"Unexpected error during alter operation: {e}")
        print(f"Unexpected error during alter operation: {e}")

def delete_data(cursor, table_name):
    try:
        condition = input("Enter the 'where' condition for deletion (e.g., id=5): ").strip()
        if not condition in ["","1=1", "true"]:
            raise ValueError("Deletion aborted: A valid where condition is required to prevent mass deletion.")
        
        query = f"delete from {table_name} where {condition};"
        cursor.execute(query)
        logger.info("Deletion successful.")
        print("Deletion successful.")

    except ValueError as ve:
        logger.warning("Input error: %s", ve)
        print(f"Input error: {ve}")
    except mysql_conn.Error as err:
        logger.error("MySQL Error during delete: %s", err)
        print(f"MySQL Error during delete: {err}")
    except Exception as e:
        logger.error("Unexpected error during delete: %s", e)
        print(f"Unexpected error during delete: {e}")
    
def drop_db_table(cursor):
    try:
        obj_type = input("Enter what you want to drop ('table' or 'database'): ").strip()
        if obj_type not in ('table', 'database'):
            raise ValueError("Invalid object type. Must be 'table' or 'database'.")
        
        obj_name = input(f"Enter the name of the {obj_type} to drop: ").strip()

        confirmation = input(f"Are you sure you want to drop the {obj_type} '{obj_name}'? This action is irreversible. (yes/no): ").strip().lower()
        if confirmation != 'yes':
            logger.info("Drop operation canceled.")
            print("Drop operation canceled.")
            return

        query = f"drop {obj_type} {obj_name};"
        cursor.execute(query)
        logger.info("%s %s dropped successfully.", obj_type, obj_name)
        print(f"{obj_type} {obj_name} dropped successfully.")

    except mysql_conn.Error as err:
        logger.error("MySQL Error during %s drop: %s", obj_type, err)
        print(f"MySQL Error during {obj_type} drop: {err}")
    except ValueError as ve:
        logger.error("Input Validation Error: %s", ve)
        print(f"Input Validation Error: {ve}")
    except Exception as e:
        logger.error("Unexpected error during %s drop: %s", obj_type, e)
        print(f"Unexpected error during {obj_type} drop: {e}")

def execute_custom_query(cursor):
    try:
        query = input("Enter your custom SQL query to perform custom operations (e.g., DQL[select], DCL[grant, revoke], TCL[commit, rollback] etc.): ").strip()
        if not query:
            logger.warning("No query entered. Operation aborted.")
            print("No query entered. Operation aborted.")
            return
        
        cursor.execute(query)

        if query.lower().startswith("select"):
            rows = cursor.fetchall()
            if rows:
                logger.info("Query Results: ")
                print("Query Results: ")
                for row in rows:
                    logger.info('%s', row)
                    print(row)
            else:
                logger.warning("Query executed successfully, but no rows returned.")
                print("Query executed successfully, but no rows returned.")
        else:
            logger.info("Query executed successfully.")
            print("Query executed successfully.")

    except mysql_conn.Error as err:
        logger.error("MySQL Error during query execution: %s", err)
        print(f"MySQL Error during query execution: {err}")
    except Exception as e:
        logger.error("Unexpected error during query execution: %s", e)
        print(f"Unexpected error during query execution: {e}")

def main():
    conn = None
    cursor = None

    try:
        conn = get_connection()
        if not conn:
            logger.warning("MySQL connection failed. Exiting.")
            print("MySQL connection failed. Exiting.")
            return

        cursor = conn.cursor()
        logger.info("MySQL connection established.")
        print("MySQL connection established.\n")

    except mysql_conn.Error as mysql_err:
        logger.error("MySQL Error during connection: %s", mysql_err)
        print(f"MySQL Error during connection: {mysql_err}")

    except Exception as e:
        logger.error("Unexpected error during setup: %s", e)
        print(f"Unexpected error during setup: {e}")

    else:
        try:
            show_databases(cursor)
            create_database(cursor)
            conn.commit()

            db_name = input("Enter the database name you want to insert data into: ").strip()
            use_database(cursor, db_name)

            show_tables(cursor)
            create_table(cursor)
            conn.commit()

            show_tables(cursor)
            table_name = input("Enter the table name you want to insert data into: ").strip()
            insert_data(cursor, table_name)
            conn.commit()

            show_tables(cursor)
            table_name = input("Enter the table name you want to update data: ").strip()
            update_data(cursor, table_name)
            conn.commit()

            show_tables(cursor)
            table_name = input("Enter the table name you want to alter: ").strip()
            alter_data(cursor, table_name)
            conn.commit()

            show_tables(cursor)
            table_name = input("Enter the table name from where you want to delete data: ").strip()
            delete_data(cursor, table_name)
            conn.commit()

            drop_db_table(cursor)
            conn.commit()

            execute_custom_query(cursor)
            conn.commit()

        except Exception as e:
            logger.error("Error during DB operations: %s", e)
            print(f"Error during DB operations: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("MySQL connection closed.")
        print("\nMySQL connection closed.")



if __name__ == "__main__":
    main()
    
    print("\nTest print to check main.py script is running properly...")