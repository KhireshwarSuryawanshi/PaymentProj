from flask import Flask, render_template, request, redirect, url_for, session
from database import database
from models import User
import employee
from werkzeug.security import generate_password_hash

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

        if db.validate_user(username, password):
            session["username"] = username  # store logged-in user
            return redirect(url_for("user_dashboard"))
        else:
            return "INVALID USERNAME OR PASSWORD. <a href='/login'>Try Again</a>"
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
    history = db.get_recharge_history(username)  # fetch from DB

    return render_template("user_dashboard.html", user=user, history=history)


# ---------------- PROFILE ROUTE ----------------
@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user = db.get_user_details(username)
    history = db.get_recharge_history(username)

    return render_template("user_profile.html", user=user, history=history)


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
            return redirect(url_for("profile"))
        else:
            return "Failed to add money. Please try again."

    return render_template("add_money.html")


@app.route("/employee", methods=["GET", "POST"])
def employee_login():
    if request.method == "POST":
        employee_ID = request.form.get("employee_ID")
        e_password = request.form.get("e_password")

        # Validate employee login
        if db.validate_employee(employee_ID, e_password):
            # Fetch employee details
            emp = db.get_employee_details(employee_ID)

            # Store the name in session
            session['employee_name'] = emp['name']
            session['employee_ID'] = employee_ID

            # Redirect to employee dashboard
            return redirect(url_for("employee_dashboard"))
        else:
            return "Invalid ID or password"
    
    return render_template("employee_login.html")

@app.route("/employee_dashboard")
def employee_dashboard():
    if "employee_id" not in session:
        return redirect(url_for("employee_login"))
    employee_ID = session["employee_id"]
    emp = db.get_employee_details(employee_ID)
    name = emp["name"] if emp else employee_ID
    return render_template("employee_dashboard.html", employee_ID=employee_ID)

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
    session.pop('employee_id', None)  # also fix key name
    return redirect(url_for('employee_login'))


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
