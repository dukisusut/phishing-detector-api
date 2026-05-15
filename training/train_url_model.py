import pandas as pd
import joblib
from xgboost import XGBClassifier
from feature import extract_features
from sklearn.utils import resample
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ===== LOAD DATA =====
df = pd.read_csv("data/url_dataset.csv")

# ===== BALANCE =====
df_phish = df[df.label == 1]
df_legit = df[df.label == 0]

print("Before balance:")
print(df.label.value_counts())

df_legit_upsampled = resample(
    df_legit,
    replace=True,
    n_samples=len(df_phish),
    random_state=42
)

df_balanced = pd.concat([df_phish, df_legit_upsampled])

# 🔥 SHUFFLE (QUAN TRỌNG)
df_balanced = df_balanced.sample(frac=1, random_state=42).reset_index(drop=True)

print("After balance:")
print(df_balanced.label.value_counts())

# ===== FEATURE =====
X = df_balanced["url"].apply(extract_features).tolist()
y = df_balanced["label"]

print("Feature sample:", X[0])
print("Total samples:", len(X))

# ===== TRAIN / TEST SPLIT =====
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ===== MODEL =====
model = XGBClassifier(
    max_depth=6,
    n_estimators=300,
    learning_rate=0.05,
    eval_metric="logloss"
)

model.fit(X_train, y_train)

# ===== EVALUATE =====
y_pred = model.predict(X_test)

print("\n=== Evaluation ===")
print(classification_report(y_test, y_pred))

# ===== SAVE =====
joblib.dump(model, "model/url_model.pkl")

print("Training done!")
