from flask import Flask, render_template, request, redirect, url_for, session
from database import database
from models import User
import employee
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
load_dotenv()
import os

from instamojo_wrapper import Instamojo   #FOR API AND PAYMENT GATEWAY

#========================================================================
api = Instamojo(
    api_key=os.getenv("INSTAMOJO_API_KEY"),
    auth_token=os.getenv("INSTAMOJO_AUTH_TOKEN"),
    endpoint="https://www.instamojo.com/api/1.1/"
)
#=========================================================================

app = Flask(__name__)
app.secret_key = "your_secret_key"  # required for session

# Initialize database
db = database()


# ---------------- HOME ROUTE ----------------
@app.route("/")
def home():
    return render_template("index.html")


# ---------------- LOGIN ROUTE ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            user = db.get_user_details(username)
            if user and check_password_hash(user["password"], password):
                session["username"] = username
                return redirect(url_for("user_dashboard"))
            else:
                return "INVALID USERNAME OR PASSWORD. <a href='/login'>Try Again</a>"
        except Exception as e:
            print("Login DB Error:", e)
            return f"Login failed due to server error: {e}"

    return render_template("user_login.html")


# ---------------- REGISTER ROUTE ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        phonum = request.form.get("phonum")
        email = request.form.get("email")
        password = request.form.get("password")
        deposit = request.form.get("deposit", 0)

        # Hash the password before saving
        hashed_password = generate_password_hash(password)

        success = db.user_savedata(
            username, phonum, email, hashed_password, deposit)
        if success:
            return "Registration successful! <a href='/login'>Go to Login</a>"
        else:
            return "Registration failed. Please check your details and try again."
    return render_template("user_register.html")


# ---------------- DASHBOARD ROUTE ----------------
@app.route("/dashboard")
def user_dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user = db.get_user_details(username)
    history = db.get_recharge_history(username)

    return render_template("user_dashboard.html", user=user, history=history)

# ---------------- PROFILE ROUTE ----------------


@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user = db.get_user_details(username)
    history = db.get_recharge_history(username)
    deposit_history = db.get_deposit_history(username)  #deposit history

    return render_template("user_profile.html", user=user, history=history, deposits=deposit_history)


# ---------------- LOGOUT ROUTE ----------------
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/recharge", methods=["GET", "POST"])
def recharge():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        username = session["username"]
        operator = request.form.get("operator")
        phone_no = request.form.get("phone_no")  # <--- ADD THIS
        amount = int(request.form.get("amount"))

        # Fetch user details from DB
        user = db.get_user_details(username)
        if not user:
            return render_template("error.html", message="User not found.")

        current_balance = user["deposit"]

        if current_balance < amount:
            return render_template("error.html", message="Insufficient balance. Please try again.")

        # <--- ADD THESE LINES TO SAVE RECHARGE AND DEDUCT BALANCE
        success1 = db.save_recharge(username, operator, phone_no, amount)
        success2 = db.add_deposit(username, -amount)

        if success1 and success2:
            return render_template("success.html", username=username, operator=operator, amount=amount)
        else:
            return render_template("error.html", message="Recharge failed. Please try again later.")

    return render_template("recharge.html")


@app.route("/add_money", methods=["GET", "POST"])
def add_money():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    if request.method == "POST":
        amount = request.form.get("amount")
        try:
            amount = float(amount)
        except ValueError:
            return "Enter a valid amount."

        if db.add_deposit(username, amount):
            db.save_deposit_history(username,amount) #deposit hrty
            return redirect(url_for("profile"))
        else:
            return "Failed to add money. Please try again."

    return render_template("add_money.html")


@app.route("/employee", methods=["GET", "POST"])
def employee_login():
    if request.method == "POST":
        employee_ID = request.form.get("employee_ID")
        e_password = request.form.get("e_password")

        try:
            emp = db.get_employee_details(employee_ID)
            if emp and check_password_hash(emp["password"], e_password):
                session['employee_id'] = employee_ID
                session['employee_name'] = emp['name']
                return redirect(url_for("employee_dashboard"))
            else:
                return "Invalid ID or password"
        except Exception as e:
            print("Employee Login DB Error:", e)
            return f"Employee login failed: {e}"

    return render_template("employee_login.html")


@app.route("/employee_dashboard")
def employee_dashboard():
    if "employee_id" not in session:
        return redirect(url_for("employee_login"))

    employee_ID = session["employee_id"]
    emp = db.get_employee_details(employee_ID)
    name = emp["name"] if emp else employee_ID

    return render_template("employee_dashboard.html", employee_ID=employee_ID, name=name)


# View all users


@app.route("/view_users")
def view_users():
    if "employee_id" not in session:
        return redirect(url_for("employee_login"))
    return employee.view_all_users()

# Search user


@app.route("/search_user", methods=["GET", "POST"])
def search_user():
    if "employee_id" not in session:
        return redirect(url_for("employee_login"))
    return employee.search_user()

# Update user


@app.route("/update_user", methods=["POST"])
def update_user():
    if "employee_id" not in session:
        return redirect(url_for("employee_login"))
    return employee.update_user()

# Delete user


@app.route("/delete_user", methods=["POST"])
def delete_user():
    if "employee_id" not in session:
        return redirect(url_for("employee_login"))
    return employee.delete_user()

# employee logout


@app.route("/employee_logout", methods=["GET", "POST"])
def employee_logout():
    session.pop('employee_id', None)
    session.pop('employee_name', None)
    return redirect(url_for('employee_login'))



#INSTAMOJO ADD MONEY

@app.route("/pay", methods=["POST"])
def pay():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username=session["username"]
    amount = request.form.get("amount")

    try:
        response = api.payment_request_create(
            amount=amount,
            purpose="add money in wallet . .",
            buyer_name=username,
            send_email=True,
            redirect_url=url_for("payment_success", _external=True)
        
        )
        return redirect(response['payment_request']['longurl'])
    
    except Exception as e:
        print("payment error:", e)
        return f"payment creatiin faild: {e}"
    

#Instamojo Payment success
@app.route("/payment_success")
def payment_success():
    payment_request_id = request.args.get('payment_request_id')
    payment_id = request.args.get('payment_id')

    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]

    # You can verify payment status (optional)
    response = api.payment_request_status(payment_request_id)

    if response['payment_request']['status'] == 'Completed':
        amount = response['payment_request']['amount']
        db.add_deposit(username, float(amount))
        db.save_deposit_history(username, float(amount))
        return render_template("success.html", username=username, operator="Instamojo", amount=amount)
    else:
        return render_template("error.html", message="Payment not completed or failed.")



# ---------------- RUN APP ----------------


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
