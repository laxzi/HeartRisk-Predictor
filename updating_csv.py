import pandas as pd

df = pd.read_csv("heart_disease_uci.csv")

# Convert multi-class target to binary
df['target'] = df['target'].apply(lambda x: 0 if x == 0 else 1)

df.to_csv("heart_disease_uci.csv", index=False)
print(df['target'].value_counts())  # Check the distribution
