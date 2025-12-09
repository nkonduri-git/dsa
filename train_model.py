import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

# Load data
df = pd.read_csv("dataset.csv")

# Features & target
X = df.drop("Outcome", axis=1)
y = df["Outcome"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# Evaluate
pred = model.predict(X_test)
print("\nMODEL PERFORMANCE:\n")
print(classification_report(y_test, pred))

# Save model
joblib.dump(model, "model.pkl")

print("\nModel saved as model.pkl")
