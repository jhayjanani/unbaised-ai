from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import pickle
import io
import time
from .database import init_db, insert_transaction, insert_transactions_batch, get_stats, get_recent_transactions

app = FastAPI(title="FraudShield AI Backend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and preprocessors
try:
    with open('backend/model.pkl', 'rb') as f:
        artifacts = pickle.load(f)
        model = artifacts['model']
        label_encoders = artifacts['label_encoders']
        scaler = artifacts['scaler']
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Initialize Database
init_db()

FEATURE_COLUMNS = ['amount', 'location', 'device', 'time']

class TransactionRequest(BaseModel):
    amount: float
    location: str
    device: str
    time: int

def preprocess_single(req: TransactionRequest):
    data = {
        'amount': [req.amount],
        'location': [req.location],
        'device': [req.device],
        'time': [req.time]
    }
    df = pd.DataFrame(data)
    
    # Handle unseen labels by assigning to a default or the first seen class
    for col in ['location', 'device']:
        le = label_encoders[col]
        # If unseen, fallback to 0 index (or 'Unknown' if it was present)
        df[col] = df[col].apply(lambda x: x if x in le.classes_ else le.classes_[0])
        df[col] = le.transform(df[col])
        
    df[['amount', 'time']] = scaler.transform(df[['amount', 'time']])
    return df[FEATURE_COLUMNS]

@app.post("/predict")
async def predict_transaction(req: TransactionRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")
        
    # Simulate processing time for animation
    time.sleep(1.5)
    
    df = preprocess_single(req)
    
    prediction_num = model.predict(df)[0]
    probabilities = model.predict_proba(df)[0]
    
    risk_score = round(float(probabilities[1]) * 100, 2)
    prediction = "Fraud" if prediction_num == 1 else "Normal"
    
    if risk_score > 70:
        risk_level = "HIGH"
    elif risk_score > 30:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
        
    insert_transaction(req.amount, req.location, req.device, req.time, prediction, risk_score)
    
    return {
        "prediction": prediction,
        "risk_score": risk_score,
        "risk_level": risk_level
    }

@app.post("/analyze-dataset")
async def analyze_dataset(file: UploadFile = File(...)):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")
        
    content = await file.read()
    df = pd.read_csv(io.BytesIO(content))
    
    # Normalize columns to lowercase for robustness
    df.columns = [c.lower().strip() for c in df.columns]
    
    print(f"Received CSV with columns: {list(df.columns)}")
    
    required_cols = {'amount', 'location', 'device', 'time'}
    if not required_cols.issubset(set(df.columns)):
        error_msg = f"CSV missing columns. Required: {required_cols}. Found: {list(df.columns)}"
        print(f"Error: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Clean amount column: handle strings like "$1,000"
    def parse_amount(val):
        try:
            if isinstance(val, str):
                # Remove currency symbols and commas
                clean_val = val.replace('$', '').replace(',', '').strip()
                return float(clean_val)
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    df['amount'] = df['amount'].apply(parse_amount)
    
    # Robust Time Parsing: Ensure 'time' is an integer hour (0-23)
    def parse_hour(val):
        try:
            if isinstance(val, str):
                val = val.strip()
                # Handle HH:MM or HH:MM:SS
                if ':' in val:
                    return int(val.split(':')[0])
                # Handle plain numeric strings
                return int(float(val))
            return int(val)
        except (ValueError, TypeError, IndexError):
            return 0 # Fallback to 0 if parsing fails

    df['time'] = df['time'].apply(parse_hour)
    
    # Handle missing values if any after cleaning
    df = df.dropna(subset=list(required_cols))
    
    if len(df) == 0:
        raise HTTPException(status_code=400, detail="No valid data rows found in CSV after cleaning.")

    processed_df = df.copy()
    
    for col in ['location', 'device']:
        le = label_encoders[col]
        # Ensure values are strings and handle unseen labels
        processed_df[col] = processed_df[col].astype(str).apply(lambda x: x if x in le.classes_ else le.classes_[0])
        processed_df[col] = le.transform(processed_df[col])
        
    # Scale numeric features
    try:
        processed_df[['amount', 'time']] = scaler.transform(processed_df[['amount', 'time']])
    except Exception as e:
        print(f"Scaling error: {e}")
        print(f"Sample data - Amount: {processed_df['amount'].head().tolist()}, Time: {processed_df['time'].head().tolist()}")
        raise HTTPException(status_code=500, detail=f"Scaling error: {str(e)}")
    
    # Ensure columns are in correct order for model
    try:
        X = processed_df[FEATURE_COLUMNS]
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)[:, 1]
    except Exception as e:
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
    
    df['prediction'] = ["Fraud" if p == 1 else "Normal" for p in predictions]
    df['risk_score'] = [round(float(prob) * 100, 2) for prob in probabilities]
    
    try:
        # Batch Insert into DB
        db_records = []
        for _, row in df.iterrows():
            db_records.append((
                float(row['amount']), 
                str(row['location']), 
                str(row['device']), 
                int(row['time']), 
                str(row['prediction']), 
                float(row['risk_score'])
            ))
        
        print(f"Inserting {len(db_records)} records into database...")
        insert_transactions_batch(db_records)
            
        fraud_count = int(sum(predictions))
        total_records = len(df)
        
        print(f"Analysis complete. Total: {total_records}, Fraud: {fraud_count}")
        
        high_risk_df = df.sort_values(by='risk_score', ascending=False).head(5)
        high_risk_transactions = high_risk_df.to_dict(orient='records')
        
        return {
            "total_records": total_records,
            "fraud_count": fraud_count,
            "normal_count": total_records - fraud_count,
            "fraud_percentage": round((fraud_count / total_records) * 100, 2) if total_records > 0 else 0,
            "avg_risk_score": round(df['risk_score'].mean(), 2),
            "high_risk_transactions": high_risk_transactions
        }
    except Exception as e:
        import traceback
        print(f"Error during batch analysis: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error during analysis: {str(e)}")

@app.get("/stats")
async def stats():
    return get_stats()

@app.get("/transactions")
async def transactions():
    return get_recent_transactions(20)

from fastapi.staticfiles import StaticFiles

# Serve the frontend directory at the root
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
