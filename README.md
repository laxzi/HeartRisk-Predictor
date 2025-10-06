# Heart Disease Prediction — Flask + HTML/CSS/JS

A beginner-friendly, production-style starter that trains a model from `heart.csv` and serves
predictions via a Flask website.

## Project Structure
```text
heart_disease_site/
├─ app.py                 # Flask backend
├─ train_model.py         # Trains + saves model pipeline
├─ requirements.txt
├─ README.md
├─ templates/
│   └─ index.html         # Frontend form
└─ static/
    ├─ style.css
    └─ script.js
```

## 1) Prerequisites
- Python 3.10 or newer (3.11 recommended)
- A terminal (Command Prompt/PowerShell on Windows, Terminal on macOS/Linux)
- A browser (Chrome, Edge, Firefox)

## 2) Create the project folder
```bash
# Choose a location you like, then:
cd "<your preferred folder>"
# If you downloaded the zip, unzip it and:
cd heart_disease_site
```

## 3) Create and activate a virtual environment

### Windows (PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

> When you're done working, you can deactivate with: `deactivate`

## 4) Install dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Put the dataset in place
- Download a **Heart Disease** dataset that has the classic columns used in many tutorials.
- Save it as: `heart.csv` **in the project root** (same folder as `train_model.py`).
- Expected base columns:
  - Numeric: `age`, `trestbps`, `chol`, `thalach`, `oldpeak`
  - Categorical (encoded by the training script): `sex`, `cp`, `fbs`, `restecg`, `exang`, `slope`, `ca`, `thal`
  - Target: `target` (0 = low risk / no disease, 1 = high risk / disease)

You can verify columns by opening the CSV and checking headers in the first row.

## 6) Train the model (one time, or whenever you change data)
```bash
# Windows
python train_model.py
# macOS/Linux (sometimes `python3`)
python3 train_model.py
```

This will print your accuracy and create `model.joblib` in the project root.

## 7) Run the website
```bash
# Windows
python app.py
# macOS/Linux
python3 app.py
```

Then open your browser to: http://127.0.0.1:5000/

## 8) Common tips / fixes
- If you see a `KeyError` or shape error: your CSV columns may not match the expected ones.
  Ensure the headers are spelled exactly as above and the `target` column exists.
- For categorical fields, the training uses one-hot encoding that safely ignores unseen categories.
- If `trestbps`, `chol`, etc. have missing values, fill or drop them in your CSV (or add handling in the script).

## 9) Deploying (optional)
- For a simple internal demo, running `python app.py` is fine.
- For Linux servers, you can run with `gunicorn` and a reverse proxy (Nginx). Not required for local usage.
