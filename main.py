import os
import sys
from dotenv import load_dotenv
import mysql.connector as mysql_conn
from getpass import getpass

def get_connection():
    try:
        # host = input("Enter your MySQL Hostname (e.g., localhost): ").strip()
        # user = input("Enter your MySQL Username (e.g., root): ").strip()
        # port = int(input("Enter your port where MySQL Server is running (e.g., 3306): "))
        # password = getpass("Enter your MySQL Password: ").strip()
        # # password = input("Enter your MySQL Password: ").strip()
        load_dotenv()
        host = os.getenv("host")
        user = os.getenv("user")
        port = os.getenv("port")
        password = os.getenv("password")
        print("Password Entered Successfully...")
    except Exception as e:
        print(f"Invalid Input: {e}")
        sys.exit()

    try:
        conn = mysql_conn.connect(
            host=host,
            user=user,
            port =port,
            password=password
        )

        if conn.is_connected():
            print(f"Successfully Connected to MySQL\n")
            return conn
        
    except mysql_conn.Error as err:
        print(f"Failed to connect with MySQL: {err}")
        sys.exit()
    except Exception as e:
        print(f"Failed to connect with MySQL: {e}")
        sys.exit()
    
def show_databases(cursor):
    try:
        cursor.execute("show databases;")
        all_dbs = cursor.fetchall()
        # print("All existing databases: - \n", all_dbs)
        print("All existing databases: - ")
        for db in all_dbs:
            print(f"- {db[0]}")

    except mysql_conn.Error as err:
        raise Exception(f"Error occured while displaying existing databases: {err}")
    except Exception as e:
        print(f"Error occured to display existing databases: {e}")

def create_database(cursor):
    try:
        db_name = input("\nEnter the name of the database you want to create: ").strip()
        # cursor.execute(f"drop database if exists `{db_name}`;")
        cursor.execute(f"create database if not exists {db_name};")
        print(f"Database {db_name} created successfully")
        return db_name
    
    except mysql_conn.Error as err:
        raise Exception(f"Error occured while creating or use database: {err}")
    except Exception as e:
        print(f"Error occured while creating or use database: {e}")

def use_database(cursor, db_name):
    try:
        cursor.execute(f"use {db_name};")
        print(f"Using Database: {db_name}")
    
    except mysql_conn.Error as err:
        raise Exception(f"Error occured while creating or use database: {err}")
    except Exception as e:
        print(f"Error occured while creating or use database: {e}")

def show_tables(cursor):
    try:
        cursor.execute("show tables;")
        all_tbls = cursor.fetchall()
        print("All exixting tables: - \n", all_tbls)

    except mysql_conn.Error as err:
        raise Exception(f"Error occured while displaying existing databases: {err}")
    except Exception as e:
        print(f"Error occured while displaying existing databases: {e}")

def create_table(cursor):
    try:
        table_name = input("Enter the name of the table you would like to create: ").strip()
        col_nm_dt = input("Enter column names and datatypes (e.g., emp_id int, emp_name varchar(50)): ").strip()
        cursor.execute(f"create table if not exists {table_name} ({col_nm_dt});")
        print(f"Table {table_name} created with columns: {col_nm_dt}")
        return table_name

    except mysql_conn.Error as err:
        raise Exception(f"Error occured while creating table: {err}")
    except Exception as e:
        print(f"Error occured while creating table: {e}")

def insert_data(cursor, table_name):
    try:
        cursor.execute(f"describe {table_name};")
        columns = [col[0] for col in cursor.fetchall()]
        print(f"Table columns are - {columns}")
        
        values_input = input(f"Enter comma-separated values for {columns}: ")
        values = [v.strip() for v in values_input.split(',')]
        values_str = "', '".join(values)

        cursor.execute(f"insert into {table_name} ({', '.join(columns)}) values ('{values_str}');")
        print("Values inserted successfully.")

    except mysql_conn.Error as err:
        raise Exception(f"Error occured while data insertion happen: {err}")
    except Exception as e:
        print(f"Error occured while data insertion happen: {e}")

def update_data(cursor, table_name):
    try:
        columns = input("Enter column names to update (comma-separated): ").strip().split(",")
        values = input("Enter corresponding values (comma-separated): ").strip().split(",")
        condition = input("Enter the 'where' condition (e.g., id=1): ").strip()

        if len(columns) != len(values):
            raise ValueError("The number of columns and values must match.")

        set_clause = ", ".join([f"{col.strip()} = %s" for col in columns])
        query = f"update {table_name} set {set_clause} where {condition};"
        cursor.execute(query, [val.strip() for val in values])
        print("Update successful.")
        
    except mysql_conn.Error as err:
        raise Exception(f"MySQL Error during update: {err}")
    except Exception as e:
        raise Exception(f"Unexpected error during update: {e}")

def alter_data(cursor, table_name):
    try:
        operation = input("Enter the 'alter' operation (add/drop column/modify column): ").strip().upper()
        column_def = input("Enter the column name and datatype (e.g., age int): ").strip()
        cursor.execute (f"alter table {table_name} {operation} {column_def};")
        print("Table altered successfully.")

    except mysql_conn.Error as err:
        raise Exception(f"MySQL Error during alter: {err}")
    except Exception as e:
        raise Exception(f"Unexpected error during alter: {e}")

def delete_data(cursor, table_name):
    try:
        condition = input("Enter the 'where' condition for deletion (e.g., id=5): ").strip()
        query = f"delete from {table_name} where {condition};"
        cursor.execute(query)
        print("Deletion successful.")

    except mysql_conn.Error as err:
        raise Exception(f"MySQL Error during delete: {err}")
    except Exception as e:
        raise Exception(f"Unexpected error during delete: {e}")
    
def drop_db_table(cursor):
    try:
        obj_type = input("Enter what you want to drop ('table' or 'database'): ").strip()
        obj_name = input(f"Enter the name of the {obj_type} to drop: ").strip()

        if obj_type not in ('table', 'database'):
            raise ValueError("Invalid object type. Must be 'table' or 'database'.")

        cursor.execute(f"drop {obj_type} {obj_name};")
        print(f"{obj_type} {obj_name} dropped successfully.")

    except mysql_conn.Error as err:
        raise Exception(f"MySQL Error during drop: {err}")
    except Exception as e:
        raise Exception(f"Unexpected error during drop: {e}")

def execute_custom_query(cursor):
    try:
        query = input("Enter your custom SQL query to perform custom operations (e.g., DQL[select], DCL[grant, revoke], TCL[commit, rollback] etc.): ").strip()
        cursor.execute(query)
        output = cursor.fetchall()
        print(f"Custom query output: \n{output}")
    except mysql_conn.Error as err:
        raise Exception(f"Error occured while executing custom query: {err}")
    except Exception as e:
        print(f"Error occured while executing custom query: {e}")


def main():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        conn.commit()
    except mysql_conn.Error as err:
        print(f"Error: {err}")
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
            print(f"Unexpected Event happened: {e}")

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
        print("Successfully MySQL connection closed")
    



if __name__ == "__main__":
    main()
    
    print("\nTest print to check main.py script is running properly...")