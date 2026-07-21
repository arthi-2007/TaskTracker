import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import datetime

# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///tasktracker.db")  # Make sure to create this DB or rename accordingly

# Secret key for sessions
app.secret_key = os.urandom(24)

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    """Show tasks for logged-in user"""
    user_id = session["user_id"]
    tasks = db.execute("SELECT id, task, done FROM tasks WHERE user_id = ?", user_id)
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
@login_required
def add():
    """Add a new task"""
    task = request.form.get("task")
    if not task:
        flash("Task cannot be empty!")
        return redirect(url_for("index"))
    db.execute("INSERT INTO tasks (user_id, task, done) VALUES (?, ?, 0)", session["user_id"], task)
    flash("Task added!")
    return redirect(url_for("index"))

@app.route("/done/<int:task_id>")
S@login_required
def delete(task_id):
    """Delete task"""
    db.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", task_id, session["user_id"])
    flash("Task deleted!")
    return redirect(url_for("index"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            flash("Please fill all fields")
            return redirect(url_for("register"))

        if password != confirmation:
            flash("Passwords do not match")
            return redirect(url_for("register"))

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) > 0:
            flash("Username already taken")
            return redirect(url_for("register"))

        hash_pw = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash_pw)

        flash("Registered successfully! Please log in.")
        return redirect(url_for("login"))
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Must provide username and password")
            return redirect(url_for("login"))

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username and/or password")
            return redirect(url_for("login"))

        session["user_id"] = rows[0]["id"]
        flash("Logged in successfully!")
        return redirect(url_for("index"))
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/now")
def now():
    now = datetime.datetime.now()
    return render_template("now.html", now=now)

if __name__ == "__main__":
    app.run(debug=True)
