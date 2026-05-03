import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import os

# ── 1. Load dataset ──────────────────────────────────────────
df = pd.read_csv('train.csv')
print("Dataset loaded. Shape:", df.shape)

# ── 2. Handle missing values ──────────────────────────────────
df.fillna(0, inplace=True)

# ── 3. Create new feature ─────────────────────────────────────
# Avoid division by zero
df['follower_following_ratio'] = df['#followers'] / (df['#follows'] + 1)

# ── 4. Select features (X) and label (y) ─────────────────────
X = df[['profile pic', 'nums/length username', 'fullname words',
        'nums/length fullname', 'name==username', 'description length',
        'external URL', 'private', '#posts', '#followers', '#follows',
        'follower_following_ratio']]

y = df['fake']

# ── 5. Scale the features ─────────────────────────────────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ── 6. Split into train and test sets ─────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

# ── 7. Train the Random Forest model ─────────────────────────
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ── 8. Evaluate the model ─────────────────────────────────────
y_pred = model.predict(X_test)
print("Accuracy :", round(accuracy_score(y_test, y_pred) * 100, 2), "%")
print("Precision:", round(precision_score(y_test, y_pred) * 100, 2), "%")
print("Recall   :", round(recall_score(y_test, y_pred) * 100, 2), "%")

# ── 9. Save the model AND scaler ─────────────────────────────
joblib.dump(model, 'model.pkl')
joblib.dump(scaler, 'scaler.pkl')
print("model.pkl and scaler.pkl saved successfully!")


