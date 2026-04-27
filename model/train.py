import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
import pickle
import os

def train_model():
    print("Loading dataset...")
    df = pd.read_csv('data/dataset.csv')
    
    # Preprocessing
    print("Preprocessing data...")
    label_encoders = {}
    for col in ['location', 'device']:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
        
    scaler = StandardScaler()
    df[['amount', 'time']] = scaler.fit_transform(df[['amount', 'time']])
    
    X = df.drop('is_fraud', axis=1)
    y = df['is_fraud']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training RandomForestClassifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"Model trained. Accuracy: {accuracy:.4f}")
    
    # Save the model and preprocessors
    os.makedirs('backend', exist_ok=True)
    
    artifacts = {
        'model': model,
        'label_encoders': label_encoders,
        'scaler': scaler
    }
    
    with open('backend/model.pkl', 'wb') as f:
        pickle.dump(artifacts, f)
        
    print("Model and preprocessors saved to backend/model.pkl")

if __name__ == '__main__':
    train_model()
