from flask import render_template, request, redirect, url_for, session
from database import database
import mysql.connector


db = database()

# VIEW ALL USERS


def view_all_users():
    mydb = db.connection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user")
    users = cursor.fetchall()
    cursor.close()
    mydb.close()
    return render_template("employee_manage_user.html", users=users)



# SEARCH USER BY USERNAME
def search_user():
    users = []  # initialize empty list
    message = None
    if request.method == "POST":
        username = request.form.get("username")
        mydb = db.connection()
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        mydb.close()

        if user:
            users = [user] 
        else:
            message = "No user found."

    return render_template("employee_manage_user.html", users=users, message=message)


# DELETE USER
def delete_user():
    if request.method == "POST":
        username = request.form.get("username")
        mydb = db.connection()
        cursor = mydb.cursor()
        cursor.execute("DELETE FROM user WHERE username=%s", (username,))
        mydb.commit()
        cursor.close()
        mydb.close()
        return "User deleted successfully."
    return render_template("employee_manage_user.html")


# UPDATE USER DETAILS (like deposit or phone)
def update_user():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        phone_no = request.form.get("phone_no")
        deposit = request.form.get("deposit")

        updates = []
        values = []

        if email:
            updates.append("email = %s")
            values.append(email)
        if phone_no:
            updates.append("phone_no = %s")
            values.append(phone_no)
        if deposit:
            updates.append("deposit = %s")
            values.append(deposit)
        if not updates:
            return "No fields to update!"

        values.append(username)
        mydb = db.connection()
        cursor = mydb.cursor()
        query = f"UPDATE user SET {', '.join(updates)} WHERE username = %s"
        cursor.execute(query, tuple(values))
        mydb.commit()
        cursor.close()
        mydb.close()

        # Render the success page with correct URL
        return render_template(
            "update_success.html",
            back_url=url_for("view_users")
        )
# TO DEDUCT BALANCE DURING RECHARGE


def deduct_balance(username, amount):
    mydb = db.connection()
    if mydb is None:
        return False
    cursor = mydb.cursor()
    try:
        cursor.execute(
            "SELECT deposit FROM user WHERE username=%s", (username,))
        result = cursor.fetchone()
        if result and result[0] >= amount:
            cursor.execute(
                "UPDATE user SET deposit = deposit - %s WHERE username = %s", (amount, username))
            mydb.commit()
            print("Recharge successful, balance deducted.")
            return True
        else:
            print("Insufficient balance.")
            return False
    except mysql.connector.Error as err:
        print("Error deducting balance:", err)
        return False
    finally:
        cursor.close()
        mydb.close()
