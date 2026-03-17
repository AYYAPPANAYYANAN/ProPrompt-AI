
import pandas as pd

def get_trash_hotspots():
    data = {
        'Location': ['Koodal Nagar', 'Simakkal', 'Gandhi Nagar', 'Anna Nagar', 'KK Nagar'],
        'Trash Level': ['High', 'Medium', 'Low', 'High', 'Medium'],
        'Last Cleaned': ['2022-01-01', '2022-01-15', '2022-02-01', '2022-03-01', '2022-04-01']
    }
    return pd.DataFrame(data)
