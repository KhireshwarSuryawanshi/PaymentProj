from werkzeug.security import generate_password_hash
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

mydb = mysql.connector.connect(
    host=os.getenv("MYSQL_ADDON_HOST"),       # <-- use this
    user=os.getenv("MYSQL_ADDON_USER"),       
    password=os.getenv("MYSQL_ADDON_PASSWORD"),
    database=os.getenv("MYSQL_ADDON_DB"),     
    port=int(os.getenv("MYSQL_ADDON_PORT", 3306))
)

cursor = mydb.cursor()

employee_ID = 102
name = "Khireshwar"
password = "Hellomoto"
hashed_password = generate_password_hash(password)

sql = "INSERT INTO employees ( employee_ID, name, password) VALUES (%s,%s,%s)"
cursor.execute(sql, (employee_ID, name, hashed_password))
mydb.commit()
cursor.close()
mydb.close()

print("employee added success")
