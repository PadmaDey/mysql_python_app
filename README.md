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
C:\Program Files\MySQL\MySQL Server 8.0\bin
mysql -u root -p

from mysql.connector import Error

def show_databases(cursor):
    try:
        cursor.execute("SHOW DATABASES;")
        all_dbs = cursor.fetchall()
        print("All existing databases:\n")
        for db in all_dbs:
            print(f"- {db[0]}")
    except Error as e:
        print(f"MySQL error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


#### net stop MYSQL80
#### net start MYSQL80