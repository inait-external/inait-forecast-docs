import pandas as pd
from typing import Optional, List
from .utils import make_request, make_get_request, with_credentials
import time


def create_payload_from_file(
    data: Optional[pd.DataFrame],
    target_columns: str,
    forecasting_horizon: int,
    observation_length: int,
    explanatory_columns: Optional[str] = None,
    models: str = "inait-basic",
    test_size: int = 0,
    n_splits: Optional[int] = 1,
    test_stride: Optional[int] = 1,
    tune: Optional[bool] = True,
    max_candidates: Optional[int] = -1,
    background: bool = True,
    session_id: Optional[str] = None,
    data_path: Optional[str] = None,
) -> dict:
    """
    Creates a JSON payload for the prediction request using a CSV or Parquet file.

    Args:
        data (pd.DataFrame): DataFrame containing the data.
        target_columns (list): List of target columns to predict.
        forecasting_horizon (int): Forecasting horizon, i.e. number of steps ahead to predict.
        observation_length (int): Observation length, i.e. number of past steps to consider when making a single prediction.
        explanatory_columns (Optional[list]): List of explanatory columns to use for prediction.
        models (Optional[str]): Model to use for prediction. Defaults to ["inait-basic"]. Available options are: ["inait-basic", "inait-advanced", "inait-best"].
        test_size (int): Number of samples to include in the test split.
        n_splits (Optional[int]): Number of splits for cross-validation. Defaults to 1.
        test_stride (Optional[int]): Stride between test splits. Defaults to 1.
        tune (Optional[bool]): Whether to perform hyperparameter tuning. Defaults to True.
        max_candidates (Optional[int]): Maximum number of candidate models to consider during hyperparameter tuning. Defaults to -1 (no limit).
        background (bool): Whether to run the operation in the background/asynchronously.
        session_id (Optional[str]): Session ID for the operation. If not provided, a new session will be created.
        data_path (str): Path to the data file. If not provided, data must be provided as a DataFrame.


    Returns:
        dict: The JSON payload for the prediction request.
    """

    return {
        "data": data.to_dict(orient="split"),
        "config": {
            "operation": "backtest",
            "session_id": session_id,
            "operation_arguments": {
                "forecasting_horizon": forecasting_horizon,
                "dataset": data_path,
                "observation_length": observation_length,
                "targets": target_columns,
                "features": explanatory_columns,
                "forecaster": models,
                "outer_cv": {
                    "n_splits": n_splits,
                    "test_size": test_size,
                },
                "tune": tune,
                "max_candidates": max_candidates,
            },
        },
        "background": background,  # Support for background/asynchronous execution
    }


def get_heuristic_train_freq(full_test_size: int):
    n_splits = 1
    test_size = full_test_size
    if full_test_size >= 100:
        n_splits = 3
        test_size = full_test_size // n_splits
    return {"n_splits": n_splits, "test_size": test_size}


@with_credentials
def backtest(
    target_columns: List[str],
    forecasting_horizon: int,
    observation_length: int,
    full_test_size: int,
    explanatory_columns: Optional[List[str]] = None,
    model: Optional[str] = "inait-basic",
    background: Optional[bool] = True,
    session_id: Optional[str] = None,
    data: Optional[pd.DataFrame] = None,
    data_path: str = None,
    tune: Optional[bool] = True,
    max_candidates: Optional[int] = -1,
    # prediction_interval_levels: Optional[float] = None,
    base_url: Optional[str] = None,
    auth_key: Optional[str] = None,
) -> dict[pd.DataFrame, str]:
    """
    Trains a model using the target columns of given dataframe, and outputs a single prediction of `forecasting_horizon` length.

    Args:
        target_columns (List[str]): List of target columns to predict.
        forecasting_horizon (int): The forecasting horizon, i.e. number of steps ahead to predict.
        observation_length (int): The observation length, i.e. number of past steps to consider when making a single prediction.
        full_test_size (int): The total number of samples to include in the test split across all cross-validation folds.
        explanatory_columns (Optional[List[str]]): List of explanatory columns to use for prediction.
        model (Optional[str]): The model to use for prediction. Defaults to "inait-basic". Available options are: ["inait-basic", "inait-advanced", "inait-best"].
        background (Optional[bool]): Whether to run the operation in the background/asynchronously. Defaults to True.
        session_id (Optional[str]): Session ID for the operation. If not provided, a new session will be created.
        data (Optional[pd.DataFrame]): DataFrame containing the data.
        data_path (str): Path to the data file. If not provided, data must be provided as a DataFrame.
        tune (Optional[bool]): Whether to perform hyperparameter tuning. Defaults to True.
        max_candidates (Optional[int]): Maximum number of candidate models to consider during hyperparameter tuning. Defaults to -1 (no limit).
        base_url (Optional[str]): The base URL of the API. If not provided, it will be read from the environment variable `INAIT_API_URL`.
        auth_key (Optional[str]): The authentication key for the API. If not provided, it will be read from the environment variable `INAIT_API_KEY`.

    Returns:
        dict: A dictionary containing:
            - "predictions": List of DataFrames, each containing predictions for one cross-validation fold
            - "score": Overall backtest score as a string
    """
    heuristics_outer_cv = get_heuristic_train_freq(full_test_size)

    payload = create_payload_from_file(
        target_columns=",".join(target_columns),
        forecasting_horizon=forecasting_horizon,
        observation_length=observation_length,
        explanatory_columns=",".join(explanatory_columns)
        if explanatory_columns
        else None,
        models=model,
        background=background,
        session_id=session_id,
        test_size=heuristics_outer_cv["test_size"],
        n_splits=heuristics_outer_cv["n_splits"],
        data_path=data_path,
        data=data,
        tune=tune,
        max_candidates=max_candidates,
    )

    # Send prediction request to the API
    response = make_request(base_url + "/backtest", payload, auth_key=auth_key)

    session_id = response["response"]["session_id"]
    response = make_get_request(
        base_url + "/status/", session_id=session_id, auth_key=auth_key
    )

    status = response["status"]
    while status != "completed":
        response = make_get_request(
            base_url + "/status/", session_id=session_id, auth_key=auth_key
        )
        status = response["status"]
        print(f"Status: {status}")
        if status == "failed":
            print(response)
            # raise ValueError("Backtest failed")
        time.sleep(10)

    response = make_get_request(
        base_url + "/result/", session_id=session_id, auth_key=auth_key
    )
    df_pred = pd.DataFrame(**response["response"]["data"]["predictions"][0])
    df_pred = df_pred.drop(columns=["outer_cv"], errors="ignore")
    df_pred.columns = [col.strip("__target") + "_predicted" for col in df_pred.columns]

    predictions = [
        df_pred.iloc[i * forecasting_horizon : (i + 1) * forecasting_horizon].copy()
        for i in range(len(df_pred) // forecasting_horizon)
    ]
    score = response["response"]["data"]["scores"]["test_error"][0]

    return {"predictions": predictions, "score": score}
