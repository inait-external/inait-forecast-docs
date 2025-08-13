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
import math


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
    predicted_data: pd.DataFrame | dict[str, pd.DataFrame],
    observation_length=None,
    legend_title_predicted="Predicted",
):
    """
    Plots the actual vs predicted values.

    Args:
        historical_data (pd.DataFrame): The actual data.
        predicted_data (pd.DataFrame | dict[str, pd.DataFrame]): The predicted data.
        observation_length (int): How many past observations to include in the plot.
        legend_title_predicted (str): The legend title for the predicted data.

    Returns:
        plotly.graph_objects.Figure: The figure object containing the plot.
    """
    # Convert single DataFrame to dict format for consistent processing
    if isinstance(predicted_data, pd.DataFrame):
        predicted_data = {legend_title_predicted: predicted_data}

    if type(historical_data) is pd.Series:
        historical_data = historical_data.to_frame()

    # Get the first DataFrame to check structure and validate columns
    first_df = next(iter(predicted_data.values()))
    predicted_cols = first_df.columns[first_df.columns.str.endswith("_predicted")]
    
    if historical_data.shape[1] != len(predicted_cols):
        raise ValueError(
            "Historical data and predicted data must have the same number of columns. Consider passing only the target columns of historical_data."
        )

    # Check if any DataFrame has prediction intervals
    has_intervals = any(
        len(df.columns[df.columns.str.endswith("_predicted")]) != len(df.columns)
        for df in predicted_data.values()
    )
    
    level = None
    if has_intervals:
        # Get level from the first DataFrame that has intervals
        for df in predicted_data.values():
            non_predicted_cols = df.columns[~df.columns.str.endswith("_predicted")]
            if len(non_predicted_cols) > 0:
                level = non_predicted_cols[-1].split("-")[-1]
                break

    if not observation_length:
        # Use the first DataFrame to determine observation length
        observation_length = (
            len(first_df) * 4
            if len(first_df) * 4 < historical_data.shape[0]
            else historical_data.shape[0]
        )

    historical_color = "#4682B4"  # Steel Blue
    
    # Generate colors programmatically
    def generate_prediction_color(index, total_count):
        """Generate distinct colors for predictions"""
        import colorsys
        
        # Default to green for single prediction
        if total_count == 1:
            return "#228B22"  # Forest Green
        
        # Use diverse color palette for multiple predictions
        # Generate colors across the full hue spectrum, avoiding red (which might conflict with error indicators)
        hue_ranges = [
            (120, 150),  # Green range
            (180, 210),  # Cyan range  
            (240, 270),  # Blue range
            (270, 300),  # Purple range
            (60, 90),    # Yellow-green range
            (30, 60),    # Orange range
            (300, 330),  # Magenta range
            (150, 180),  # Teal range
        ]
        
        # Select hue range based on index
        hue_start, hue_end = hue_ranges[index % len(hue_ranges)]
        
        # Add variation within the range
        hue_offset = (hue_end - hue_start) * (index // len(hue_ranges)) / max(1, total_count // len(hue_ranges))
        hue = (hue_start + hue_offset) / 360  # Convert to 0-1 range
        
        # Vary saturation and lightness for additional distinction
        saturation = 0.6 + (0.3 * (index % 2))  # 0.6 or 0.9
        lightness = 0.4 + (0.2 * ((index // 2) % 3))  # 0.4, 0.6, or 0.8
        
        # Convert HSL to RGB
        r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)
        
        # Convert to hex
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    
    band_fill = "rgba(60,179,113,0.18)"  # 3CB371 with ~18% opacity

    nplots = len(predicted_cols)
    ncols = 1 if nplots == 1 else 2
    nrows = math.ceil(nplots / ncols)

    fig = make_subplots(rows=nrows, cols=ncols, subplot_titles=historical_data.columns)

    # Flags to add each legend item only once
    hist_legend_added = False
    band_legend_added = False

    # Historical traces (add once)
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

    # Predicted traces - loop through each DataFrame in the dict
    total_predictions = len(predicted_data)
    for pred_idx, (title, df_predicted) in enumerate(predicted_data.items()):
        # Generate color for this predicted dataset
        predicted_color = generate_prediction_color(pred_idx, total_predictions)
        
        pred_cols = df_predicted.columns[df_predicted.columns.str.endswith("_predicted")]
        pred_legend_added = False
        
        # Add prediction intervals if they exist for this DataFrame
        if has_intervals and len(df_predicted.columns) > len(pred_cols):
            interval_cols = df_predicted.columns[~df_predicted.columns.str.endswith("_predicted")]
            
            for i, pred_col in enumerate(pred_cols):
                col_id = pred_col.split("_predicted")[0]
                row = i // ncols + 1
                col_pos = i % ncols + 1
                
                lo_col = f"{col_id}_predicted-lo-{level}"
                hi_col = f"{col_id}_predicted-hi-{level}"
                
                if lo_col in df_predicted.columns and hi_col in df_predicted.columns:
                    # Add LO trace (invisible)
                    fig.add_trace(
                        go.Scatter(
                            x=df_predicted.index,
                            y=df_predicted[lo_col],
                            mode="lines",
                            line=dict(width=0),
                            hoverinfo="skip",
                            showlegend=False,
                            legendgroup=f"pred_{title}",
                        ),
                        row=row,
                        col=col_pos,
                    )
                    
                    # Add HI trace with fill
                    fig.add_trace(
                        go.Scatter(
                            x=df_predicted.index,
                            y=df_predicted[hi_col],
                            mode="lines",
                            line=dict(width=0),
                            fill="tonexty",
                            fillcolor=band_fill,
                            hoverinfo="skip",
                            showlegend=not band_legend_added,
                            legendgroup=f"pred_{title}",
                            name=f"{level}% interval",
                        ),
                        row=row,
                        col=col_pos,
                    )
                    band_legend_added = True

        # Add predicted line traces
        for i, pred_col in enumerate(pred_cols):
            row = i // ncols + 1
            col_pos = i % ncols + 1

            fig.add_trace(
                go.Scatter(
                    x=df_predicted.index,
                    y=df_predicted[pred_col],
                    mode="markers+lines" if len(df_predicted) == 1 else "lines",
                    name=title,
                    showlegend=not pred_legend_added,
                    line=dict(color=predicted_color),
                    legendgroup=f"pred_{title}",
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
