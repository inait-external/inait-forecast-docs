import argparse
import json
from .utils import parse_common_arguments
from typing import Optional
from .utils import make_request
import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_image(image_bytes: bytes):
    # Create a BytesIO object from the bytes
    image_stream = BytesIO(image_bytes)
    # Read the image from the BytesIO object
    image = plt.imread(image_stream, format="png")
    # Display the image
    plt.imshow(image)


def bytes_from_base64(base64_string: str) -> bytes:
    """
    Converts a base64 encoded string to bytes.

    Args:
        base64_string (str): Base64 encoded string.

    Returns:
        bytes: Decoded bytes from the base64 string.
    """
    import base64

    return base64.b64decode(base64_string)


def create_plot_payload(
    session_id: str,
    plot_type: str,
    cutoff_date: Optional[str],
    prediction_for: Optional[str],
) -> dict:
    """
    Creates a JSON payload for the explanation request.

    Args:
        session_id (str): Identifier for the operation session.
        cutoff_days (str): Comma-separated list of dates for explanation.

    Returns:
        dict: The JSON payload for the explanation request.
    """
    payload = {
        "data": None,  # No data needed for plotting
        "config": {
            "session_id": session_id,
            "operation": "image",
            "operation_arguments": {
                "plot_type": plot_type,
                "cutoff_date": cutoff_date,
                "prediction_for": prediction_for,
            },
        },
    }

    return payload


def parse_arguments():
    """
    Parses command-line arguments for the plot script.

    Returns:
        argparse.Namespace: Parsed arguments containing plot type and other parameters.
    """
    # Add common arguments parsing
    parent_parser = parse_common_arguments()
    parser = argparse.ArgumentParser(
        description="Generate plots based on ImageOperationArguments.",
        parents=[parent_parser],
    )
    parser.add_argument(
        "--session-id",
        type=str,
        required=True,
        help="Session ID from a previous prediction request.",
    )
    parser.add_argument(
        "--plot-type",
        type=str,
        choices=["prediction", "explanation"],
        required=True,
        help="Type of plot to generate (prediction or explanation).",
    )
    parser.add_argument(
        "--cutoff-date",
        type=str,
        default=None,
        help="Cutoff date for the plot (optional).",
    )
    parser.add_argument(
        "--prediction-for",
        type=str,
        default=None,
        help="Prediction target for the plot (optional).",
    )
    return parser.parse_args()


def plot(
    historical_data: pd.DataFrame,
    predicted_data: pd.DataFrame,
    observation_length=None,
):
    """
    Plots the actual vs predicted values.

    Args:
        historical_data (pd.DataFrame): The actual data.
        predicted_data (pd.DataFrame): The predicted data.
        observation_length (int): How many past observations to include in the plot.

    Returns:
        plotly.graph_objects.Figure: The figure object containing the plot.
    """
    if type(historical_data) is pd.Series:
        historical_data = historical_data.to_frame()
    # Ensure historical_data and predicted_data have the same number of columns
    predicted_cols = predicted_data.columns[
        predicted_data.columns.str.endswith("_predicted")
    ]
    df_predicted = predicted_data[predicted_cols]

    if historical_data.shape[1] != df_predicted.shape[1]:
        raise ValueError(
            "Historical data and predicted data must have the same number of columns. Consider passing only the target columns of historical_data."
        )

    predicted_intervals_cols = None
    if (
        df_predicted.shape[1] != predicted_data.shape[1]
    ):  # if the predicted data also contains prediction intervals
        predicted_intervals_cols = predicted_data.columns[
            ~predicted_data.columns.str.endswith("_predicted")
        ]
        df_predicted_intervals = predicted_data[predicted_intervals_cols]
        level = df_predicted_intervals.columns[-1].split("-")[
            -1
        ]  # Ensure the last column is named correctly

    if not observation_length:
        observation_length = (
            df_predicted.shape[0] * 4
            if df_predicted.shape[0] * 4 < historical_data.shape[0]
            else historical_data.shape[0]
        )

    historical_color = "#4682B4"  # Steel Blue
    predicted_color = "#3CB371"  # Medium Sea Green
    band_fill = "rgba(60,179,113,0.18)"  # 3CB371 with ~18% opacity

    band_legend_added = False

    nplots = len(df_predicted.columns)
    ncols = 1 if nplots == 1 else 2
    nrows = nplots // ncols  # Ceiling division

    fig = make_subplots(rows=nrows, cols=ncols, subplot_titles=historical_data.columns)

    # Flags to add each legend item only once
    hist_legend_added = False
    pred_legend_added = False

    # Historical traces
    for i, col in enumerate(historical_data.columns):
        row = i // ncols + 1
        col_pos = i % ncols + 1

        fig.add_trace(
            go.Scatter(
                x=historical_data.iloc[-observation_length:].index,
                y=historical_data.iloc[-observation_length:][col],
                mode="lines",
                name="Historical",
                showlegend=not hist_legend_added,
                line=dict(color=historical_color),
            ),
            row=row,
            col=col_pos,
        )
        hist_legend_added = True

    # Predicted traces
    for i, col in enumerate(df_predicted.columns):
        col_id = col.split("_predicted")[0]  # Get the original column name
        row = i // ncols + 1
        col_pos = i % ncols + 1

        if predicted_intervals_cols is not None:
            # --- shaded band: add LO first (no legend, no line) ---
            fig.add_trace(
                go.Scatter(
                    x=df_predicted_intervals.index,
                    y=df_predicted_intervals[f"{col_id}_predicted-lo-{level}"],
                    mode="lines",
                    line=dict(width=0),
                    hoverinfo="skip",
                    showlegend=False,
                    legendgroup="pred",
                ),
                row=row,
                col=col_pos,
            )
            # --- then HI with fill to previous (creates the band) ---
            fig.add_trace(
                go.Scatter(
                    x=predicted_data.index,
                    y=predicted_data[f"{col_id}_predicted-hi-{level}"],
                    mode="lines",
                    line=dict(width=0),
                    fill="tonexty",
                    fillcolor=band_fill,
                    hoverinfo="skip",
                    showlegend=not band_legend_added,
                    legendgroup="pred",
                    name=f"{level}% interval",
                ),
                row=row,
                col=col_pos,
            )
            band_legend_added = True

        # --- predicted line on top ---
        fig.add_trace(
            go.Scatter(
                x=df_predicted.index,
                y=df_predicted[col],
                mode="markers+lines" if len(df_predicted) == 1 else "lines",
                name="Predicted",
                showlegend=not pred_legend_added,
                line=dict(color=predicted_color),
                legendgroup="pred",
            ),
            row=row,
            col=col_pos,
        )

        pred_legend_added = True

    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="")
    fig.update_layout(
        height=300 * nrows,
        width=900,
        title_text="Historical vs Predicted",
        showlegend=True,
        plot_bgcolor="white",  # Plot area background
        paper_bgcolor="white",  # Outer background
    )
    fig.update_layout(legend=dict(groupclick="togglegroup"))

    # Apply grid settings to all subplot axes
    for axis in fig.layout:
        if axis.startswith("xaxis") or axis.startswith("yaxis"):
            fig.layout[axis].showgrid = True
            fig.layout[axis].gridcolor = "lightgray"
            fig.layout[axis].gridwidth = 1

            # Borders
            fig.layout[axis].showline = True
            fig.layout[axis].linecolor = "black"
            fig.layout[axis].linewidth = 1
            fig.layout[axis].mirror = True
    fig.show()


if __name__ == "__main__":
    # python examples/client/plot_script.py --base-url http://127.0.0.1:8004/plot/ --auth-key "your_auth_key_here" --session-id "session_from_prediction" --plot-type prediction
    args = parse_arguments()
    try:
        payload = create_plot_payload(
            session_id=args.session_id,
            plot_type=args.plot_type,
            cutoff_date=args.cutoff_date,
            prediction_for=args.prediction_for,
        )
        # Assuming make_request is a function that sends the request to the server
        response = make_request(args.base_url, payload, auth_key=args.auth_key)
        print("Plot Response:")
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"Error: {str(e)}")
