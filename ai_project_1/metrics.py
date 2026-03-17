
import pandas as pd
import plotly.express as px
from sklearn.metrics import accuracy_score, precision_score, confusion_matrix

def evaluate_model():
   data = generate_mock_data()
   X = data.drop(['customer_id', 'churn'], axis=1)
   y = data['churn']
   X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
   models = train_model()
   
   metrics = {}
   for model_name, model in models.items():
       y_pred = model.predict(X_test)
       accuracy = accuracy_score(y_test, y_pred)
       precision = precision_score(y_test, y_pred)
       conf_mat = confusion_matrix(y_test, y_pred)
       
       metrics[model_name] = {
           'Accuracy': accuracy,
           'Precision': precision,
           'Confusion Matrix': conf_mat
       }
       
       fig = px.imshow(conf_mat, text_auto=True, color_continuous_scale='Blues')
       fig.update_layout(title=f'{model_name} Confusion Matrix')
       
       return metrics, fig
   