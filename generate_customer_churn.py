import numpy as np
import pandas as pd


np.random.seed(42)

n_rows = 800

customer_age = np.random.randint(18, 70, size=n_rows)
gender = np.random.choice(['Male', 'Female'], size=n_rows)
contract_type = np.random.choice(['Month-to-Month', 'One Year', 'Two Year'], size=n_rows)
monthly_charges = np.random.uniform(30, 120, size=n_rows).round(2)
tenure = np.random.randint(1, 60, size=n_rows)
support_calls = np.random.randint(0, 10, size=n_rows)
total_usage = np.random.randint(10, 300, size=n_rows)
satisfaction_score = np.random.randint(1, 6, size=n_rows)

base_risk = (
    (customer_age - 40) * 0.015
    + (monthly_charges - 60) * 0.03
    + (support_calls * 0.12)
    + ((tenure < 12) * 0.7)
    + ((contract_type == 'Month-to-Month') * 0.6)
    + ((satisfaction_score <= 2) * 0.9)
)

probability = 1 / (1 + np.exp(-base_risk))
churn = (np.random.rand(n_rows) < probability).astype(int)

df = pd.DataFrame(
    {
        'customer_age': customer_age,
        'gender': gender,
        'contract_type': contract_type,
        'monthly_charges': monthly_charges,
        'tenure': tenure,
        'support_calls': support_calls,
        'total_usage': total_usage,
        'satisfaction_score': satisfaction_score,
        'churn': churn,
    }
)

output_path = 'data/customer_churn.csv'
df.to_csv(output_path, index=False)
print(f"Dataset saved to {output_path}")
print(df.head())
