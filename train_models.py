"""
Regenerate the three disease prediction models from CSV data.
Run this script once to produce:
  - diabetes_model.sav
  - heart_disease_model.sav
  - parkinsons_model.sav
"""
import os, pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

BASE = os.path.dirname(os.path.abspath(__file__))

# --- Diabetes -----------------------------------------------
print("Training diabetes model...")
df = pd.read_csv(os.path.join(BASE, "diabetes.csv"))
X = df.drop(columns="Outcome")
y = df["Outcome"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = SVC(kernel="rbf", probability=True, random_state=42)
model.fit(X_train, y_train)
acc = model.score(X_test, y_test)
print(f"  accuracy: {acc:.4f}")
pickle.dump(model, open(os.path.join(BASE, "diabetes_model.sav"), "wb"))
pickle.dump(scaler, open(os.path.join(BASE, "diabetes_scaler.pkl"), "wb"))

# --- Heart Disease ------------------------------------------
print("Training heart-disease model...")
df = pd.read_csv(os.path.join(BASE, "heart.csv"))
X = df.drop(columns="target")
y = df["target"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)
acc = model.score(X_test, y_test)
print(f"  accuracy: {acc:.4f}")
pickle.dump(model, open(os.path.join(BASE, "heart_disease_model.sav"), "wb"))
pickle.dump(scaler, open(os.path.join(BASE, "heart_disease_scaler.pkl"), "wb"))

# --- Parkinson's -------------------------------------------
print("Training Parkinsons model...")
df = pd.read_csv(os.path.join(BASE, "parkinsons.csv"))
X = df.drop(columns=["name", "status"])
y = df["status"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = SVC(kernel="rbf", probability=True, random_state=42)
model.fit(X_train, y_train)
acc = model.score(X_test, y_test)
print(f"  accuracy: {acc:.4f}")
pickle.dump(model, open(os.path.join(BASE, "parkinsons_model.sav"), "wb"))
pickle.dump(scaler, open(os.path.join(BASE, "parkinsons_scaler.pkl"), "wb"))

print("All three models saved successfully.")

