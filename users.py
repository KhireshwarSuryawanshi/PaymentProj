from database import *

db = database()


def get_user_(username):
    return db.get_user_details(username)


def update_user(username, phone_no=None, email=None, deposit=None):
    mydb = db.connection()
    cursor = mydb.cursor()
    updates = []
    values = []

    if phone_no:
        updates.append("phone_no = %s")
        values.append(phone_no)

    if email:
        updates.append("email = %s")
        values.append(email)

    if deposit:
        updates.append("deposit = %s")
        values.append(deposit)

    values.append(username)
    sql = f"UPDATE user SET { ','.join(updates)} WHERE username = %s"
    cursor.execute(sql,values)
    mydb.commit()
    cursor.close()
    mydb.close()
    return True

