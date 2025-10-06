import pandas as pd

df = pd.read_csv("heart_disease_uci.csv")
print(df.head())
print("\nColumns:", df.columns.tolist())
