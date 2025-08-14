import argparse
from typing import Optional
from .utils import make_request, parse_common_arguments
import pandas as pd
import plotly.express as px


def create_explanation_payload(session_id: str, cutoff_days: str) -> dict:
    """
    Creates a JSON payload for the explanation request.

    Args:
        session_id (str): Identifier for the operation session.
        cutoff_days (str): Comma-separated list of dates for explanation.

    Returns:
        dict: The JSON payload for the explanation request.
    """
    payload = {
        "data": None,  # No data needed for explanation
        "config": {
            "session_id": session_id,
            "operation": "explain",
            "operation_arguments": {"cutoff_days": cutoff_days},
        },
    }
    return payload


def parse_arguments():
    """
    Parses command-line arguments for the script.

    Returns:
        argparse.Namespace: Parsed arguments containing session ID and cutoff days.
    """
    parent_parser = parse_common_arguments()
    parser = argparse.ArgumentParser(
        description="Make an explanation request to the FastAPI server.",
        parents=[parent_parser],
    )
    parser.add_argument(
        "--session-id",
        type=str,
        required=True,
        help="Session ID from a previous prediction request.",
    )
    parser.add_argument(
        "--cutoff-days",
        type=str,
        default=None,
        help="Comma-separated list of dates for explanation (default: None).",
    )
    return parser.parse_args()


def explain(
    session_id: str,
    base_url: str,
    auth_key: str,
    historical_data: pd.DataFrame,
    cutoff_date: Optional[str] = None,
    forecasted_step: Optional[int] = 0,
    max_drivers_displayed: int = 10,
):
    """
    Generate and display a feature importance explanation for the model predictions.

    Args:
        session_id (str): The session ID for the explanation request.
        base_url (str): The base URL for the API.
        auth_key (str): The authentication key for the API.
        historical_data (pd.DataFrame): The historical data used for the explanation.
        cutoff_date (Optional[str]): The cutoff date for the explanation, i.e, the date up to which the historical data is considered.
        forecasted_step (Optional[int]): The forecasted step for the explanation, i.e., what step of the prediction to explain (starting from 0).
        max_features_displayed (int): The maximum number of features to display in the explanation plot.
    """

    cutoff_date = (
        cutoff_date or historical_data.index[-1]
    )  # Default to the last date in the historical data

    payload = create_explanation_payload(session_id=session_id, cutoff_days=cutoff_date)
    explanation_response = make_request(
        base_url + "/explanation", payload, auth_key=auth_key
    )

    explanation = explanation_response["response"]["data"][
        cutoff_date
    ]  # Select the explanation for the specified cutoff date
    explanation = explanation[
        sorted(explanation.keys())[forecasted_step]
    ]  # Extract the explanation for the specified forecasted step
    explanation = (
        pd.DataFrame.from_dict(explanation, orient="index")
        .abs()
        .reset_index()
        .iloc[:-1, :]
    )  # Convert into DF, take abs and exclude the last row which is the target variable
    explanation = explanation.rename(columns={"index": "feature", 0: "shap_value"})
    explanation = explanation.sort_values(by="shap_value", ascending=False).reset_index(
        drop=True
    )
    excluded_features_sum = explanation["shap_value"].iloc[max_drivers_displayed:].sum()
    number_of_excluded_features = max(explanation.shape[0] - max_drivers_displayed, 0)
    explanation = explanation.head(max_drivers_displayed)  # Limit to the top N features
    if number_of_excluded_features > 0:
        explanation = pd.concat(
            [
                explanation,
                pd.DataFrame(
                    [
                        [
                            f"Sum of the {number_of_excluded_features} remaining features",
                            excluded_features_sum,
                        ]
                    ],
                    columns=explanation.columns,
                ),
            ]
        )
    explanation = explanation.iloc[::-1]

    fig = px.bar(
        x=explanation["shap_value"],
        y=explanation["feature"],
        orientation="h",
        color=explanation["shap_value"],
        color_continuous_scale=["red", "lightgray", "blue"],
        color_continuous_midpoint=0,
        title="Main drivers of predictions",
    )

    fig.update_layout(
        xaxis_title="Impact of each feature on the prediction",
        yaxis_title="Features",
        coloraxis_showscale=False,
        height=max(
            400, len(explanation) * 25
        ),  # Adjust height based on number of features
    )

    fig.show()


if __name__ == "__main__":
    # python examples/client/explanation_script.py --base-url http://127.0.0.1:8004/explanation/ --auth-key "your_auth_key_here" --session-id "session_from_prediction"
    args = parse_arguments()

    try:
        payload = create_explanation_payload(args.session_id, args.cutoff_days)
        explanation_response = make_request(
            args.base_url, payload, auth_key=args.auth_key
        )
        print("Explanation Response:")
        print(explanation_response)
    except Exception as e:
        print(str(e))
