import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import joblib

df = pd.read_pickle('LinkedIn_Dataset.pcl')
print(df.columns)
print(df.head())
df.fillna(0, inplace=True)

# LinkedIn specific features
df['profile_strength'] = (
    df['Number of Skills'] +
    df['Number of Experiences'] +
    df['Number of Educations']
)

df['engagement'] = (
    df['Followers'] +
    df['Number of Recommendations']
)

# ✅ THEN select features
X = df[[
    'Connections',
    'Followers',
    'Number of Experiences',
    'Number of Educations',
    'Number of Skills',
    'Number of Recommendations',
    'Number of Projects',
    'Number of Publications',
    'Number of Courses',
    'Number of Honors',
    'Number of Languages',
    'Number of Organizations',
    'Number of Interests',
    'Number of Activities',
    'profile_strength',
    'engagement'
]]

y = df['Label']
X_scaled = X   # no scaling needed

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

print("Accuracy:", accuracy_score(y_test, model.predict(X_test)))

joblib.dump(model,  'linkedin_model.pkl')
# joblib.dump(scaler, 'linkedin_scaler.pkl')
print("LinkedIn model saved!")