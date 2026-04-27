import pandas as pd
import numpy as np
import random
import os

def generate_data(num_samples=2000):
    locations = ['New York', 'London', 'Paris', 'Tokyo', 'Sydney', 'Mumbai', 'Dubai', 'Toronto']
    devices = ['Desktop', 'Mobile', 'Tablet', 'Unknown']
    
    data = []
    for _ in range(num_samples):
        # Normal behavior (mostly)
        amount = np.random.lognormal(mean=3.5, sigma=1.0)
        location = random.choice(locations)
        device = random.choice(devices)
        time_hour = random.randint(0, 23)
        
        # Fraud Logic
        is_fraud = 0
        fraud_prob = 0.05
        
        # Condition 1: High amount
        if amount > 1000:
            fraud_prob += 0.3
            
        # Condition 2: Suspicious time (2 AM - 4 AM)
        if 2 <= time_hour <= 4:
            fraud_prob += 0.2
            
        # Condition 3: Unknown device
        if device == 'Unknown':
            fraud_prob += 0.15
            
        if random.random() < fraud_prob:
            is_fraud = 1
            if amount < 50:
                amount = amount * random.uniform(10, 50) # Make fraud amounts higher on average
                
        # Round amount
        amount = round(amount, 2)
        
        data.append([amount, location, device, time_hour, is_fraud])
        
    df = pd.DataFrame(data, columns=['amount', 'location', 'device', 'time', 'is_fraud'])
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/dataset.csv', index=False)
    print(f"Generated {num_samples} samples and saved to data/dataset.csv")
    print(df['is_fraud'].value_counts())

if __name__ == '__main__':
    generate_data(5000)
