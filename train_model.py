import json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

CSV_PATH = "heart_disease_uci.csv"
MODEL_PATH = "model.joblib"
META_PATH = "model_meta.json"

# Columns
CATEGORICAL_COLS = ['sex', 'cp', 'fbs', 'restecg', 'exang', 'slope', 'thal']
NUMERIC_COLS = ['age', 'trestbps', 'chol', 'thalch', 'ca', 'oldpeak']
TARGET_COL = 'target'

# Mappings for categorical columns
MAPPINGS = {
    "sex": {"male": 1, "female": 0},
    "cp": {
        "typical angina": 0,
        "atypical angina": 1,
        "non-anginal": 2,
        "asymptomatic": 3,
    },
    "fbs": {"true": 1, "false": 0},
    "restecg": {
        "normal": 0,
        "lv hypertrophy": 1,
        "st-t abnormality": 2,
    },
    "exang": {"true": 1, "false": 0},
    "slope": {
        "upsloping": 0,
        "flat": 1,
        "downsloping": 2,
    },
    "thal": {
        "normal": 0,
        "fixed defect": 1,
        "reversable defect": 2,
    },
}

def main():
    print("📦 Loading dataset:", CSV_PATH)
    df = pd.read_csv(CSV_PATH)

    print("Before processing, shape:", df.shape)
    print(df.head())

    # Ensure numeric columns are numeric
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Standardize strings to lowercase and map categorical columns
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
            if col in MAPPINGS:
                df[col] = df[col].map(MAPPINGS[col])

    # Fill missing numeric values with median
    for col in NUMERIC_COLS:
        df[col] = df[col].fillna(df[col].median())

    # Fill missing categorical values with mode
    for col in CATEGORICAL_COLS:
        df[col] = df[col].fillna(df[col].mode()[0])

    # Ensure target is integer
    df[TARGET_COL] = pd.to_numeric(df[TARGET_COL], errors='coerce')
    df = df.dropna(subset=[TARGET_COL])
    df[TARGET_COL] = df[TARGET_COL].astype(int)

    print("After cleaning, shape:", df.shape)
    print("Target distribution:\n", df[TARGET_COL].value_counts())

    # Features and target
    X = df[CATEGORICAL_COLS + NUMERIC_COLS]
    y = df[TARGET_COL]

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Preprocessing: scale all features (since categorical are numeric)
    preprocessor = ColumnTransformer(
        transformers=[("num", StandardScaler(), NUMERIC_COLS )],
         remainder="passthrough"
        )

    clf = RandomForestClassifier(n_estimators=90, random_state=42)

    pipeline = Pipeline([
        ("pre", preprocessor),
        ("clf", clf),
    ])

    print("🧠 Training model...")
    pipeline.fit(X_train, y_train)

    print("🔎 Evaluating...")
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"✅ Accuracy: {acc*100:.2f}%")
    print("Classification Report:\n", classification_report(y_test, y_pred, digits=3))

    # Save model
    joblib.dump(pipeline, MODEL_PATH)
    print(f"💾 Saved pipeline to {MODEL_PATH}")

    # Save metadata
    meta = {
        "categorical_cols": CATEGORICAL_COLS,
        "numeric_cols": NUMERIC_COLS,
        "target_col": TARGET_COL,
        "accuracy": acc,
        "mappings": MAPPINGS,
    }
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"💾 Saved metadata to {META_PATH}")

if __name__ == "__main__":
    main()

