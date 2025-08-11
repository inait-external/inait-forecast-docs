import argparse
from .utils import make_request, parse_common_arguments


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
