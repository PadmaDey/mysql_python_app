import mysql.connector as mysql_conn
from getpass import getpass

while True:
    host = input("Enter your MySQL host name (e.g., localhost): ").strip()
    user = input("Enter your MySQL Username: ").strip()
    # password = getpass("Enter MySQL password: ").strip()
    password = input("Enter MySQL password: ").strip()
    print("Password entered sucurely.")

    conn = mysql_conn.connect(
        host=host,
        user=user,
        password=password
    )

    if conn.is_connected():
        print("Successfully connected to MySQL")

        cursor = conn.cursor()

        cursor.execute("show databases;")
        all_db = cursor.fetchall()
        print("All existing databases are -\n", all_db)

        db_name = input("Enter the name of the database you want to create: ").strip()
        # cursor.execute(f"drop database if exists `{db_name}`;")
        cursor.execute(f"create database if not exists `{db_name}`;")
        cursor.execute(f"use `{db_name}`;")

        cursor.execute("show tables;")
        all_tbl = cursor.fetchall()
        print("All exixting tables are - \n", all_tbl)

        table_name = input("Enter the name of the table you want to create: ").strip()
        # cursor.execute(f"drop table if exists `{db_name}`.`{table_name}`;")
        cursor.execute(f"create table if not exists `{table_name}` (emp_id varchar(10), emp_name varchar(50), emp_designation varchar(50));")

        values = input("Enter comma seperated values for ('emp_id', 'emp_name', 'emp_designation'): ")
        values = [v.strip() for v in values.split(',')]

        insert_query = f"insert into `{table_name}` (`emp_id`, `emp_name`, `emp_designation`) values ('{values[0]}', '{values[1]}', '{values[2]}');"
        cursor.execute(insert_query)
        print("Values inserted successfully")

        query = input("Entry your SQL query: ").strip()
        cursor.execute(query)
        result = cursor.fetchall()
        print("Executed query output: \n", result)



        conn.commit()
 
