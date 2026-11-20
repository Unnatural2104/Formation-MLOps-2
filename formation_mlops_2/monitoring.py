import pandas as pd


def monitor(latest_predictions: pd.DataFrame) -> pd.DataFrame:
    # Start filling function
    monitoring_df = pd.DataFrame({
        "predictions_time": [latest_predictions["predictions_time"][0]],
        "predictions": [latest_predictions["predictions"].max()]
    })
    # End filling function
    return monitoring_df
