from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import pandas as pd
import joblib
import json
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # for session and flash messages
DATABASE = "database.db"

# ----------------- Database Initialization -----------------
def init_db():
    """Ensure the necessary database tables exist upon startup."""
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        
        # Create predictions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                inputs TEXT NOT NULL,
                prediction TEXT NOT NULL,
                probability REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create contacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

# Initialize DB when the app starts
init_db()

# ----------------- ML Model Setup -----------------
pipe = joblib.load("model.joblib")

with open("model_meta.json", "r") as f:
    META = json.load(f)

CATEGORICAL_COLS = META["categorical_cols"]
NUMERIC_COLS = META["numeric_cols"]
MAPPINGS = META["mappings"]

# ----------------- Database Helper -----------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.context_processor
def inject_user():
    return dict(session=session)

# ----------------- Sign Up -----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("signup"))

        conn = get_db_connection()
        
        # 1. Check if user already exists
        existing_user = conn.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone()

        if existing_user:
            conn.close()
            flash("That username is already taken. Please choose another.", "danger")
            return redirect(url_for("signup"))

        # 2. Hash the password for security
        hashed_password = generate_password_hash(password)

        # 3. Insert the new user into the database
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)", 
                (username, hashed_password)
            )
            conn.commit()
            
            # 4. Log the user in automatically after successful registration
            session["user"] = username
            flash("Account created successfully! You are now logged in.", "success")
            return redirect(url_for("home"))
        except Exception as e:
            conn.rollback()
            print(f"Database insertion error: {e}")
            flash("An error occurred during registration.", "danger")
            return redirect(url_for("signup"))
        finally:
            conn.close()

    return render_template("signup.html")
# ----------------- Login -----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "danger")
    return render_template("login.html")
# ----------------- Logout -----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully", "success")
    return redirect(url_for("home"))

# ----------------- Home / Prediction -----------------
@app.route("/", methods=["GET", "POST"])
def home():
   
    prediction, proba, error = None, None, None
    should_scroll = False
    user_logged_in = session.get("user") is not None 

    if request.method == "POST":
        if not user_logged_in:
            # If a logged-out user attempts to submit the form (e.g., bypassing HTML)
            flash("Please log in to submit a prediction.", "warning")
            # Redirect to the login page immediately. Stop processing the form.
            return redirect(url_for("login"))
        try:
            form = request.form
            row = {}

            for col in CATEGORICAL_COLS + NUMERIC_COLS:
                v = form.get(col, "").strip()
                if v == "":
                    row[col] = None
                    continue

                if col in MAPPINGS:
                    mapping = MAPPINGS[col]
                    if v.isdigit():
                        row[col] = int(v)
                    else:
                        v_norm = v.lower()
                        matched = None
                        for k, val in mapping.items():
                            if str(k).lower().startswith(v_norm):
                                matched = val
                                break
                        if matched is None:
                            raise ValueError(f"Invalid value for {col}: {v}")
                        row[col] = matched
                else:
                    row[col] = float(v)

            if any(v is None for v in row.values()):
                missing = [k for k, v in row.items() if v is None]
                error = f"Missing inputs: {missing}"
                should_scroll = True
            else:
                df = pd.DataFrame([row])
                pred = pipe.predict(df)[0]
                if hasattr(pipe, "predict_proba"):
                    proba = round(float(pipe.predict_proba(df)[0][1]) * 100, 2)
                if pred == 1:
                     prediction = "High Risk of Heart Disease. Your results indicate an elevated likelihood of heart disease."
                else:
                    prediction = "Low Risk of Heart Disease. Your profile suggests a lower chance of heart disease at this time."
                should_scroll = True
                 # ---- Store prediction in DB ----
                conn = get_db_connection()
                conn.execute(
                      "INSERT INTO predictions (username, inputs, prediction, probability) VALUES (?, ?, ?, ?)",
                      (session.get("user"), json.dumps(row), prediction, proba)
                )
                conn.commit()
                conn.close()

        except Exception as e:
            print("Error during prediction:", e)
            error = "Something went wrong. Please check your inputs."
            should_scroll = True

    return render_template("index.html", prediction=prediction, proba=proba, error=error,scroll_to_result=should_scroll,user_logged_in=user_logged_in)
  

# ----------------- Contact -----------------
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        conn = get_db_connection()
        conn.execute("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)",
                     (name, email, message))
        conn.commit()
        conn.close()

        flash("Your message has been sent!", "success")
        return redirect(url_for("contact"))

    return render_template("contact.html")
# ----------------- Run App -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)







