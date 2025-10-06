from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import pandas as pd
import joblib
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"  # for session and flash messages
DATABASE = "database.db"

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
    if not session.get("user"):
        flash("Please log in to access the prediction form.", "warning")
        return redirect(url_for("login"))
    prediction, proba, error = None, None, None

    if request.method == "POST":
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
            else:
                df = pd.DataFrame([row])
                pred = pipe.predict(df)[0]
                if hasattr(pipe, "predict_proba"):
                    proba = round(float(pipe.predict_proba(df)[0][1]) * 100, 2)
                if pred == 1:
                     prediction = "High Risk of Heart Disease. Your results indicate an elevated likelihood of heart disease."
                else:
                    prediction = "Low Risk of Heart Disease. Your profile suggests a lower chance of heart disease at this time."
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

    return render_template("index.html", prediction=prediction, proba=proba, error=error)
  

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







