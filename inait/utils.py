import requests
import argparse
import os
from typing import Optional
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path


def load_credentials(path: str) -> tuple[str, str]:
    load_dotenv(path)

    base_url = os.environ.get("API_BASE_URL")
    auth_key = os.environ.get("API_AUTH_KEY")

    if not base_url or not auth_key:
        raise ValueError(
            "❌ Missing environment variables. Please set API_BASE_URL and API_AUTH_KEY in credentials.txt."
        )

    return base_url, auth_key


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

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"Request failed: {response.status_code}, {response.text}"
        ) from e

    response = response.json()
    return response


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
    else:
        status_response = requests.get(url, headers=headers)

    try:
        status_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"Status check failed for url {url}: {status_response.status_code}, {status_response.text}"
        ) from e
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


def read_file(filepath: str, file_type: Optional[str] = None, **kwargs) -> pd.DataFrame:
    """
    Load a file as a pandas DataFrame based on its extension or specified type.

    Supports loading from local files and HTTPS URLs.

    Args:
        filepath (str): Path to the file (local or HTTPS URL).
        file_type (Optional[str]): Force a specific file type reader.
                                  Options: 'csv', 'excel', 'json', 'parquet',
                                  'hdf'/'h5', 'pickle'/'pkl'
        **kwargs: Additional arguments passed to the pandas reader function.

    Returns:
        pd.DataFrame: Loaded dataframe.

    Raises:
        ValueError: If file type or extension is not supported.
        Exception: If file loading fails.

    Examples:
        # Load CSV file
        df = read_file("data.csv")

        # Load CSV with index column (common pandas parameter)
        df = read_file("data.csv", index_col=0)

        # Load Excel file with specific sheet
        df = read_file("data.xlsx", sheet_name="Sheet2")

        # Load from HTTPS URL
        df = read_file("https://example.com/data.csv")

        # Force .dat file to be read as CSV
        df = read_file("custom.dat", file_type="csv")

        # Force specific reader with additional parameters
        df = read_file("data.txt", file_type="csv", delimiter="\t")
    """
    # Map file types to pandas reader functions
    type_readers = {
        "csv": pd.read_csv,
        "excel": pd.read_excel,
        "json": pd.read_json,
        "parquet": pd.read_parquet,
        "hdf": pd.read_hdf,
        "h5": pd.read_hdf,
        "pickle": pd.read_pickle,
        "pkl": pd.read_pickle,
    }

    # If file_type is specified, use it
    if file_type:
        file_type_lower = file_type.lower()
        if file_type_lower not in type_readers:
            raise ValueError(
                f"Unsupported file type: '{file_type}'. "
                f"Supported types: {', '.join(sorted(set(type_readers.keys())))}"
            )
        reader = type_readers[file_type_lower]
        try:
            return reader(filepath, **kwargs)
        except Exception as e:
            raise Exception(f"Failed to load file as {file_type}: {e}") from e

    # Determine file extension
    if filepath.startswith(("http://", "https://")):
        # For URLs, extract extension from the path
        path = Path(filepath.split("?")[0])  # Remove query parameters if any
    else:
        path = Path(filepath)

    extension = path.suffix.lower()

    # Map extensions to pandas reader functions
    readers = {
        ".csv": pd.read_csv,
        ".xlsx": pd.read_excel,
        ".xls": pd.read_excel,
        ".json": pd.read_json,
        ".parquet": pd.read_parquet,
        ".h5": pd.read_hdf,
        ".hdf5": pd.read_hdf,
        ".pkl": pd.read_pickle,
        ".pickle": pd.read_pickle,
    }

    if extension not in readers:
        raise ValueError(
            f"Unsupported file extension: {extension}. "
            f"Supported extensions: {', '.join(readers.keys())}. "
            f"Use file_type parameter to force a specific reader."
        )

    reader = readers[extension]

    try:
        return reader(filepath, **kwargs)
    except Exception as e:
        raise Exception(f"Failed to load {extension} file: {e}") from e
