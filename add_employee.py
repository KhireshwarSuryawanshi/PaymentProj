from werkzeug.security import generate_password_hash
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="recharge_db"
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
