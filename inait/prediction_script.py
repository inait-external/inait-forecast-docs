import pandas as pd
import argparse
from typing import Optional
from .utils import make_request, parse_common_arguments, with_credentials
from tqdm.auto import tqdm
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
)  # to be removed in future version


def get_dataframe_from_response(
    response: dict,
) -> tuple[pd.DataFrame | None, str | None]:
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
    data: pd.DataFrame,
    target_columns: str,
    forecasting_horizon: int,
    observation_length: int,
    explanatory_columns: Optional[str] = None,
    models: Optional[str] = "inait-basic",
    prediction_interval_levels: Optional[str] = None,
    background: Optional[bool] = False,
) -> dict:
    """
    Creates a JSON payload for the prediction request using a CSV or Parquet file.

    Args:
        data (pd.DataFrame): DataFrame containing the input data.
        target_columns (str): Comma-separated string of column names to predict.
        explanatory_columns (Optional[str]): Comma-separated string of explanatory column names.
        models (str): Comma-separated list of models to use.
        prediction_interval_levels (Optional[str]): Comma-separated list of prediction interval levels.
        forecasting_horizon (int): Forecasting horizon.
        observation_length (int): Observation length.
        background (bool): Whether to execute the request in background mode (default: False).

    Returns:
        dict: The JSON payload for the prediction request.
    """

    return {
        "data": data.to_dict(orient="split"),
        "config": {
            "operation": "forecast",
            "operation_arguments": {
                "forecasting_horizon": forecasting_horizon,
                "observation_length": observation_length,
                "targets": target_columns,
                "dataset": None,
                "features": explanatory_columns,
                "prediction_interval_levels": prediction_interval_levels,
                "forecaster": models,
            },
        },
        "background": background,  # Support for background/asynchronous execution
    }


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
        default="inait-basic",
        help="Comma-separated list of models to use (default: inait-basic). Supported models: inait-basic, inait-advanced, inait-best.",
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


# def process_models(models: Optional[str] = None):
#     if models is None:
#         models = ["inait-basic"]
#     elif isinstance(models, str):
#         models = [models]
#     elif not isinstance(models, list):
#         raise TypeError("models must be a string or None")

#     if models == ["inait-basic"]:
#         models = ["basic"]
#     elif models == ["inait-advanced"]:
#         models = ["basic", "gradient_boost"]
#     elif models == ["inait-best"]:
#         models = ["robust", "fast_boost", "gradient_boost"]

#     return models


@with_credentials
def predict(
    data: pd.DataFrame,
    forecasting_horizon: int,
    observation_length: int,
    target_columns: list[str] | str,
    positive_predictions_only: bool = False,
    explanatory_columns: Optional[list] = None,
    prediction_interval_levels: Optional[float] = None,
    model: Optional[str] = "inait-basic",
    verbose: Optional[bool] = True,
    base_url: Optional[str] = None,
    auth_key: Optional[str] = None,
) -> dict[pd.DataFrame, str]:
    """
    Trains a model using the target columns of given dataframe, and outputs a single prediction of `forecasting_horizon` length.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
        target_columns (list): List of target columns to predict.
        explanatory_columns (Optional[list]): List of explanatory columns to use for prediction.
        forecasting_horizon (int): Forecasting horizon, i.e. number of steps ahead to predict.
        observation_length (int): Observation length, i.e. number of past steps to consider when making a single prediction.
        model (Optional[str]): Model to use for prediction. Defaults to ["inait-basic"]. Available options are: ["inait-basic", "inait-advanced", "inait-best"].
        verbose (bool): Whether to print logs during prediction.
        base_url (Optional[str]): The base URL of the inait Forecasting API. If not provided, will be auto-loaded from credentials.
        auth_key (Optional[str]): The authentication key for the API. If not provided, will be auto-loaded from credentials.

    Returns:
        dict: The response from the API containing the prediction results and the session id.
    """
    if observation_length <= 0:
        raise ValueError("observation_length must be greater than 0")
    if forecasting_horizon <= 0:
        raise ValueError("forecasting_horizon must be greater than 0")
    if observation_length > len(data):
        raise ValueError(
            "observation_length must be less than or equal to the length of the data"
        )

    # models = process_models(model)

    payload = create_payload_from_file(
        data=data,
        target_columns=",".join(target_columns),
        forecasting_horizon=forecasting_horizon,
        observation_length=observation_length,
        explanatory_columns=",".join(explanatory_columns)
        if explanatory_columns
        else None,
        models=model,
        prediction_interval_levels=str(prediction_interval_levels)
        if prediction_interval_levels
        else None,
    )

    # Send prediction request to the API
    if verbose:
        print("Sending prediction request...")
    response = make_request(base_url + "/prediction", payload, auth_key=auth_key)

    # Process the response and extract results
    df, session_id = get_dataframe_from_response(response)

    columns_inait = [c for c in df.columns if c.startswith("Inait")]
    df_wide = df.drop("cutoff", axis=1).pivot(
        index="ds", columns="unique_id", values=columns_inait
    )

    df_wide.index.name = None

    # Merge levels into a single column name
    df_wide.columns = [f"{b}_{a}" if b else str(a) for a, b in df_wide.columns]
    df_wide.columns = df_wide.columns.str.replace(r"_Inait", "_predicted", regex=True)
    if positive_predictions_only:
        # Ensure all predictions are non-negative
        df_wide = df_wide.clip(lower=0)
    return dict(prediction=df_wide, session_id=session_id)


@with_credentials
def predict_test(
    data: pd.DataFrame,
    target_columns: list,
    forecasting_horizon: int,
    observation_length: int,
    train_size: Optional[float] = None,
    test_size: Optional[int] = None,
    model: Optional[str] = "inait-basic",
    base_url: Optional[str] = None,
    auth_key: Optional[str] = None,
) -> dict[list[pd.DataFrame], list[str]]:
    """
    Trains a model using the target columns of given dataframe, and outputs a list of N predictions, with N being the number of test samples.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
        target_columns (list): List of target columns to predict.
        forecasting_horizon (int): Forecasting horizon, i.e. number of steps ahead to predict.
        observation_length (int): Observation length, i.e. number of past steps to consider when making a single prediction.
        train_size (float): Proportion of the dataset to include in the train split. If both train_size and test_size are not specified, train_size will be set to 0.8.
        test_size (int): Number of samples to include in the test split. If both train_size and test_size are not specified, test_size will be set to 0.2.
        model (str): Model to use for prediction. Defaults to "inait-basic". Available options are: ["inait-basic", "inait-advanced", "inait-best"].
        base_url (Optional[str]): The base URL of the inait Forecasting API. If not provided, will be auto-loaded from credentials.
        auth_key (Optional[str]): The authentication key for the API. If not provided, will be auto-loaded from credentials.

    Returns:
        dict[list[pd.DataFrame], list[str]]: A dictionary containing a list of DataFrames with predictions and a list of session IDs.
    """
    if train_size is not None and test_size is not None:
        raise ValueError(
            "Both train_size and test_size cannot be specified at the same time. Please specify only one of them."
        )
    if train_size is not None:
        start_test_index = int(len(data) * train_size)
    elif test_size is not None:
        start_test_index = len(data) - test_size - forecasting_horizon
    else:
        train_size = 0.8
        start_test_index = int(len(data) * train_size)

    predictions = []
    session_ids = []

    # TODO: allow for different strides; currently, we use stride = 1 and therefore predictions overlap when forecasting_horizon > 1.
    for t in tqdm(
        range(start_test_index + 1, len(data) - forecasting_horizon + 1),
        postfix=f"Forecasting with {model}",
    ):
        results = predict(
            data=data.iloc[:t],
            target_columns=target_columns,
            forecasting_horizon=forecasting_horizon,
            observation_length=observation_length,
            model=model,
            verbose=False,
            base_url=base_url,
            auth_key=auth_key,
        )
        predictions.append(results["prediction"])
        session_ids.append(results["session_id"])
    return dict(predictions=predictions, session_ids=session_ids)


def score_test(
    predictions: list[pd.DataFrame], ground_truth: pd.DataFrame, metric: str = "mae"
):
    """
    Computes the score between predictions and ground truth using the specified metric.

    Args:
        predictions (list[pd.DataFrame]): List of DataFrames with predictions.
        ground_truth (pd.DataFrame): DataFrame with ground truth values.
        metric (str): The metric to use for scoring. Defaults to "mae". Options are: ["mae", "mse"].

    Returns:
        float: The computed score.
    """
    if metric not in ["mae", "mse"]:
        raise ValueError(
            f"Invalid metric: {metric}. Supported metrics are: ['mae', 'mse']"
        )

    score = 0
    # if stride < forecasting_horizon then predictions overlap, all horizons are weighted equally
    for prediction in predictions:
        common_idxs = list(set(prediction.index).intersection(set(ground_truth.index)))
        prediction = prediction.loc[common_idxs]
        _ground_truth = ground_truth.loc[common_idxs]
        if metric == "mae":
            score += mean_absolute_error(_ground_truth, prediction)
        elif metric == "mse":
            score += mean_squared_error(_ground_truth, prediction)
    return score / len(predictions)


def check_coverage(
    historical_data: pd.DataFrame,
    prediction_data: pd.DataFrame,
    prediction_interval_level: int,
):
    """
    Checks the coverage of the prediction intervals against the historical data.

    Args:
        historical_data (pd.DataFrame): The historical data.
        prediction_data (pd.DataFrame): The prediction data with intervals.
        prediction_interval_level (int): The prediction interval level (e.g., 80 for 80% interval).
    """

    # Ensure indices are aligned and datetime
    historical_data = historical_data.copy()
    prediction_data = prediction_data.copy()
    historical_data.index = pd.to_datetime(historical_data.index)
    prediction_data.index = pd.to_datetime(prediction_data.index)
    idxs = historical_data.index.intersection(prediction_data.index)
    columns = historical_data.columns.intersection(
        [
            col.replace(f"_predicted-lo-{prediction_interval_level}", "")
            .replace(f"_predicted-hi-{prediction_interval_level}", "")
            .replace("_predicted", "")
            for col in prediction_data.columns
            if "_predicted" in col
        ]
    )

    total_within = 0
    total_count = 0
    for col in columns:
        actual = historical_data.loc[idxs, col]
        lo_col = f"{col}_predicted-lo-{prediction_interval_level}"
        hi_col = f"{col}_predicted-hi-{prediction_interval_level}"
        if lo_col in prediction_data.columns and hi_col in prediction_data.columns:
            lo = prediction_data.loc[idxs, lo_col]
            hi = prediction_data.loc[idxs, hi_col]
            within = (actual >= lo) & (actual <= hi)
            total_within += within.sum()
            total_count += within.count()
    avg_percent = 100 * total_within / total_count if total_count > 0 else 0
    print(
        f"Coverage result: {total_within} out of {total_count} actual values "
        f"({avg_percent:.1f}%) were inside the {prediction_interval_level}% prediction interval."
    )


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
            args.explanatory_columns,
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
        print(e)
