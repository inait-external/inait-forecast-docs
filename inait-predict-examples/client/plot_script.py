import argparse
import json
from .utils import parse_common_arguments
from typing import Optional
from .utils import make_request
import matplotlib.pyplot as plt
from io import BytesIO


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
