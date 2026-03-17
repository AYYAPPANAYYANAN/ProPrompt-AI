
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

def train_model():
   data = generate_mock_data()
   X = data.drop(['customer_id', 'churn'], axis=1)
   y = data['churn']
   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
   
   rf_model = RandomForestClassifier(n_estimators=100)
   rf_model.fit(X_train, y_train)
   
   lr_model = LogisticRegression()
   lr_model.fit(X_train, y_train)
   
   return {'Random Forest': rf_model, 'Logistic Regression': lr_model}
   