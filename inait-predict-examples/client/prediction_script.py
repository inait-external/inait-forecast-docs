import pandas as pd
import argparse
from typing import Optional
from .utils import make_request, parse_common_arguments


def get_dataframe_from_response(response: dict) -> tuple[pd.DataFrame, str]:
    """
    Extract DataFrame and session_id from the prediction response.

    Returns:
        tuple[pd.DataFrame, str]: DataFrame with prediction data and session_id
    """
    prediction_response = response["response"]
    df = None
    session_id = None

    if "data" in prediction_response:
        df = pd.DataFrame(**prediction_response["data"])
    else:
        print("No data found in the response to create a DataFrame.")

    if "session_id" in prediction_response:
        session_id = prediction_response["session_id"]
    else:
        print("No session_id found in the response.")

    return df, session_id


def create_payload_from_file(
    file_path: str,
    target_columns: str,
    forecasting_horizon: int,
    observation_length: int,
    feature_columns: Optional[str] = None,
    models: str = "basic",
    prediction_interval_levels: Optional[str] = None,
    background: bool = False,
) -> dict:
    """
    Creates a JSON payload for the prediction request using a CSV or Parquet file.

    Args:
        file_path (str): Path to the file (CSV or Parquet).
        target_columns (str): Comma-separated string of column names to predict.
        feature_columns (Optional[str]): Comma-separated string of feature column names.
        models (str): Comma-separated list of models to use.
        prediction_interval_levels (Optional[str]): Comma-separated list of prediction interval levels.
        forecasting_horizon (int): Forecasting horizon.
        observation_length (int): Observation length.
        background (bool): Whether to execute the request in background mode (default: False).

    Returns:
        dict: The JSON payload for the prediction request.
    """
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif file_path.endswith(".parquet"):
        df = pd.read_parquet(file_path)
    else:
        raise ValueError(
            "Unsupported file format. Please provide a CSV or Parquet file."
        )

    payload = {
        "data": df.to_dict(orient="split"),
        "config": {
            "operation": "forecast",
            "operation_arguments": {
                "forecasting_horizon": forecasting_horizon,
                "observation_length": observation_length,
                "targets": target_columns,
                "dataset": None,
                "features": feature_columns,
                "prediction_interval_levels": prediction_interval_levels,
                "forecaster": models,
            },
        },
        "background": background,  # Support for background/asynchronous execution
    }
    return payload


def parse_arguments():
    parent_parser = parse_common_arguments()
    parser = argparse.ArgumentParser(
        description="Make a prediction request to the FastAPI server.",
        parents=[parent_parser],
    )
    parser.add_argument(
        "--data-path",
        type=str,
        required=True,
        help="Path to the CSV or Parquet file containing data.",
    )
    parser.add_argument(
        "--target-columns",
        type=str,
        required=True,
        help="Comma-separated string of column names to predict.",
    )
    parser.add_argument(
        "--feature-columns",
        type=str,
        default=None,
        help="Comma-separated string of feature column names (default: None).",
    )
    parser.add_argument(
        "--models",
        type=str,
        default="basic",
        help="Comma-separated list of models to use (default: basic). Supported models: basic, robust, neural, gradient_boost, fast_boost.",
    )
    parser.add_argument(
        "--prediction-interval-levels",
        type=str,
        default=None,
        help="Comma-separated list of prediction interval levels (default: None). Example: 10,90",
    )
    parser.add_argument(
        "--forecasting-horizon",
        type=int,
        required=True,
        help="Forecasting horizon (mandatory).",
    )
    parser.add_argument(
        "--observation-length",
        type=int,
        required=True,
        help="Observation length (mandatory).",
    )
    parser.add_argument(
        "--background",
        action="store_true",
        help="Execute request in background/asynchronous mode (default: False).",
    )
    return parser.parse_args()


# Example usage
if __name__ == "__main__":
    # python examples/client/prediction_script.py --base-url http://127.0.0.1:8004/prediction/ --auth-key "your_auth_key_here" --data-path data/airline.csv --target-columns data --forecasting-horizon 10 --observation-length 5 --models basic,robust --prediction-interval-levels 10,90
    args = parse_arguments()

    try:
        payload = create_payload_from_file(
            args.data_path,
            args.target_columns,
            args.forecasting_horizon,
            args.observation_length,
            args.feature_columns,
            args.models,
            args.prediction_interval_levels,
            args.background,
        )
        prediction_response = make_request(
            args.base_url, payload, auth_key=args.auth_key
        )
        print("Prediction Response:")
        print(prediction_response)

        # Extract session_id from response
        if (
            "response" in prediction_response
            and "session_id" in prediction_response["response"]
        ):
            session_id = prediction_response["response"]["session_id"]
            print(f"Generated session_id: {session_id}")
    except Exception as e:
        print(str(e))
