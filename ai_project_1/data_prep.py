
import pandas as pd
import numpy as np

def generate_mock_data():
   np.random.seed(0)
   data = {
       'customer_id': np.arange(1, 1001),
       'age': np.random.randint(18, 80, 1000),
       'gender': np.random.choice(['Male', 'Female'], 1000),
       'account_length': np.random.randint(1, 20, 1000),
       'usage': np.random.randint(100, 1000, 1000),
       'churn': np.random.choice([0, 1], 1000)
   }
   df = pd.DataFrame(data)
   return df
   