import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import mlflow

mlflow.sklearn.autolog()


def train_model(features: pd.DataFrame, model_registry_folder: str) -> None:
    target = 'Ba_avg'
    df_x = features.drop(columns=[target])
    y = features[target]
    with mlflow.start_run() as run:
        model = RandomForestRegressor(n_estimators=1, max_depth=10, n_jobs=1)
        model.fit(df_x, y)

    mlflow.sklearn.log_model(
       sk_model=model,
       name="A nice name for your model",
       input_example=df_x.iloc[:1, :],
       registered_model_name="A nice name for your registered model",
    )

    joblib.dump(model, os.path.join(model_registry_folder, 'model.joblib'))


def predict(features: pd.DataFrame, model_path: str) -> pd.DataFrame:
    model = joblib.load(model_path)
    features['predictions'] = model.predict(features)
    return features
