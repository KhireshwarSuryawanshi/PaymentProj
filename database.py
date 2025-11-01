import mysql.connector
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
load_dotenv()
import os


class database():
    def connection(self):
        try:
            mydb = mysql.connector.connect(
                host=os.getenv("MYSQL_ADDON_HOST"),      
                user=os.getenv("MYSQL_ADDON_USER"),       
                password=os.getenv("MYSQL_ADDON_PASSWORD"),
                database=os.getenv("MYSQL_ADDON_DB"),     
                port=int(os.getenv("MYSQL_ADDON_PORT", 3306))  # convert to int
            )
            print("connection success. . . . . ")
            return mydb
        except mysql.connector.Error as error:
            print("Connection failed: ", error)
            return None

# TO SAVE USER DATA

    def user_savedata(self, username, phonum, email, password, deposit):
        mydb = self.connection()
        if mydb is None:
            print("No database connected...")
            return False
        cursor = mydb.cursor()
        sql = "INSERT INTO user(username, phone_no, email, password, deposit) VALUES (%s, %s, %s, %s, %s)"

        # Ensure deposit is integer
        try:
            deposit = int(deposit)
        except ValueError:
            deposit = 0

        val = (username, phonum, email, password, deposit)
        print("Inserting:", val)
        try:
            cursor.execute(sql, val)
            mydb.commit()
            print("Record inserted.")
            return True
        except mysql.connector.Error as err:
            print("Failed to insert record:", err)
            return False
        finally:
            cursor.close()
            mydb.close()


# TO LOGIN USER

    def validate_user(self, username, password):
        mydb = self.connection()
        if mydb is None:
            return False

        cursor = mydb.cursor(dictionary=True)

        cursor.execute(
            "SELECT password FROM user WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        mydb.close()

        if user and check_password_hash(user["password"], password):
            return True
        else:
            return False

# FOR MY PROFILE IN USER DASHBOARD
    def get_user_details(self, username):
        mydb = self.connection()
        if mydb is None:
            return None

        cursor = mydb.cursor(dictionary=True)  # return results as dictionary
        sql = "SELECT username, phone_no, email, deposit, password FROM user WHERE username = %s"
        cursor.execute(sql, (username,))       # <- execute the query
        user = cursor.fetchone()               # fetch one record
        cursor.close()
        mydb.close()
        return user


# TO VALIDAATE EMPLOYEE LOGIN


    def validate_employee(self, employee_ID, password):
        mydb = self.connection()
        if mydb is None:
            return False

        cursor = mydb.cursor(dictionary=True)
        cursor.execute(
            "SELECT password FROM employees WHERE employee_ID=%s", (employee_ID,))
        emp = cursor.fetchone()
        cursor.close()
        mydb.close()
        if emp and check_password_hash(emp["password"], password):
            return True
        return False

    def save_recharge(self, username, operator, phone_no, amount):
        try:
            mydb = self.connection()
            if mydb is None:
                return False

            cursor = mydb.cursor()
            sql = "INSERT INTO recharge_history (username, operator, phone_no, amount) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (username, operator, phone_no, amount))
            mydb.commit()
            cursor.close()
            mydb.close()
            print("Recharge saved successfully.")
            return True
        except Exception as e:
            print("Failed to save recharge:", e)
            return False

    # Optional: fetch recharge history for a user

    def get_recharge_history(self, username):
        try:
            mydb = self.connection()
            if mydb is None:
                return []

            cursor = mydb.cursor(dictionary=True)
            sql = """
                SELECT operator, phone_no, amount, recharge_date
                FROM recharge_history
                WHERE username=%s
                ORDER BY recharge_date DESC
            """
            cursor.execute(sql, (username,))
            result = cursor.fetchall()
            cursor.close()
            mydb.close()
            return result
        except Exception as e:
            print("Failed to fetch history:", e)
            return []

    # TO UPDATE USER DEPOSIT BALANCE AFTER RECHARGE

    def add_deposit(self, username, amount):
        mydb = self.connection()
        if mydb is None:
            return False
        cursor = mydb.cursor()
        try:
            # Update deposit by adding the new recharge amount
            sql = "UPDATE user SET deposit = deposit + %s WHERE username = %s"
            val = (amount, username)
            cursor.execute(sql, val)
            mydb.commit()
            print("Deposit updated successfully.")
            return True
        except mysql.connector.Error as err:
            print("Failed to update deposit:", err)
            return False
        finally:
            cursor.close()
            mydb.close()

    def get_employee_details(self, employee_ID):
        mydb = self.connection()
        if mydb is None:
            return None

        cursor = mydb.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM employees WHERE employee_ID=%s", (employee_ID,))
        emp = cursor.fetchone()
        cursor.close()
        mydb.close()
        return emp

#- - - - - -  
    def save_deposit_history(self,username,amount):
        try:
            mydb = self.connection()
            cursor = mydb.cursor()
            query = "INSERT INTO deposit_history (username, amount) VALUES (%s, %s)"
            cursor.execute(query, (username, amount))
            mydb.commit()
            cursor.close()
            mydb.close()
            return True
        except Exception as e:
            print("error saving depost history . . . . . ")
            return False
        
    def get_deposit_history(self,username):
        try:
            mydb = self.connection()
            cursor = mydb.cursor(dictionary=True)
            query = "SELECT * FROM deposit_history WHERE username = %s ORDER BY date DESC"
            cursor.execute(query, (username,))
            result = cursor.fetchall()
            cursor.close()
            mydb.close()
            return result
        except Exception as e:
            print("eroor fetching depo history . . . ")
            return[]