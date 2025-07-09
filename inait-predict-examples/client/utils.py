import requests
import argparse
import os
from typing import Optional


def make_request(url: str, payload: dict, auth_key: Optional[str] = None):
    """
    Makes a POST request to the specified endpoint with optional authentication.

    Args:
        url (str): The URL of the endpoint.
        payload (dict): The JSON payload for the request.
        auth_key (Optional[str]): Authentication key for the server.

    Returns:
        dict: The response JSON if the request is successful.

    Raises:
        Exception: If the request fails or returns a non-200 status code.
    """
    headers = {"Content-Type": "application/json"}
    if auth_key:
        headers["Authorization"] = f"Bearer {auth_key}"

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code in [200, 202]:
        response = response.json()
        return response
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")


def make_get_request(
    url: str, session_id: Optional[str], auth_key: Optional[str] = None
):
    """
    Check task status and return result if completed.

    Args:
        url (str): Base server URL.
        session_id (str): Task session ID.
        auth_key (Optional[str]): Authentication key.

    Returns:
        dict: Task status or result if completed.
    """
    bearer_str = f"Bearer {auth_key}" if auth_key else ""
    headers = {"Authorization": bearer_str} if auth_key else {}

    # Check status
    if session_id is not None:
        url = f"{url}{session_id}"
        status_response = requests.get(f"{url}", headers=headers)
        if status_response.status_code != 200:
            raise Exception(
                f"Status check failed for url {url}: {status_response.status_code}, {status_response.text}"
            )
        return status_response.json()
    else:
        status_response = requests.get(url, headers=headers)
        if status_response.status_code != 200:
            raise Exception(
                f"Status check failed for url {url}: {status_response.status_code}, {status_response.text}"
            )
        return status_response.json()


def parse_common_arguments():
    """
    Parses common command-line arguments for tools.

    Returns:
        argparse.Namespace: Parsed arguments containing base URL and authentication key.
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--base-url",
        type=str,
        required=True,
        help="Base URL of the FastAPI server.",
    )
    parser.add_argument(
        "--auth-key",
        type=str,
        default=os.getenv("FINCHAT_AUTH_KEY"),
        help="Authentication key for the server (default: FINCHAT_AUTH_KEY environment variable).",
    )
    return parser
