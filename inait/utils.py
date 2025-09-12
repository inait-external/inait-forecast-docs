import requests
import argparse
import os
from typing import Optional
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
from functools import wraps, lru_cache


def load_credentials(path: str) -> tuple[str, str]:
    load_dotenv(path)

    base_url = os.environ.get("API_BASE_URL")
    auth_key = os.environ.get("API_AUTH_KEY")

    if not base_url or not auth_key:
        raise ValueError(
            "❌ Missing environment variables. Please set API_BASE_URL and API_AUTH_KEY in credentials.txt."
        )

    return base_url, auth_key


@lru_cache(maxsize=1)
def auto_load_credentials() -> tuple[str, str]:
    """
    Automatically load credentials from multiple possible locations.
    Tries in order:
    1. Environment variables (API_BASE_URL, API_AUTH_KEY)
    2. ../credentials.txt (relative to current working directory)
    3. ./credentials.txt (in current working directory)

    Returns:
        tuple[str, str]: base_url and auth_key

    Raises:
        ValueError: If credentials cannot be found in any location
    """
    # First try environment variables
    base_url = os.environ.get("API_BASE_URL", "").strip()
    auth_key = os.environ.get("API_AUTH_KEY", "").strip()

    if base_url and auth_key:
        return base_url, auth_key

    # Try loading from standard locations
    credential_paths = [
        "../credentials.txt",  # Parent directory (common for notebooks)
        "./credentials.txt",  # Current directory
        "credentials.txt",  # Current directory without ./
    ]

    for path in credential_paths:
        if os.path.exists(path):
            try:
                load_dotenv(path)
                base_url = os.environ.get("API_BASE_URL", "").strip()
                auth_key = os.environ.get("API_AUTH_KEY", "").strip()

                if base_url and auth_key:
                    return base_url, auth_key
            except Exception:
                continue

    raise ValueError(
        "❌ Could not find credentials. Please set API_BASE_URL and API_AUTH_KEY "
        "either as environment variables or in credentials.txt file."
    )


def with_credentials(func):
    """
    Decorator that automatically injects credentials if not provided.

    If base_url or auth_key are None, attempts to load them automatically
    from standard locations (environment variables or credentials.txt files).
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if base_url and auth_key are in kwargs
        base_url = kwargs.get("base_url")
        auth_key = kwargs.get("auth_key")

        # If either is None or not provided, auto-load credentials
        if base_url is None or auth_key is None:
            try:
                auto_base_url, auto_auth_key = auto_load_credentials()
                if base_url is None:
                    kwargs["base_url"] = auto_base_url
                if auth_key is None:
                    kwargs["auth_key"] = auto_auth_key
            except ValueError as e:
                # Only raise if credentials were truly not provided
                if base_url is None and auth_key is None:
                    raise e
                elif base_url is None or auth_key is None:
                    raise ValueError(
                        "Both base_url and auth_key must be provided, or neither "
                        "(to use auto-loading)."
                    )

        return func(*args, **kwargs)

    return wrapper


def _build_auth_headers(auth_key: Optional[str]) -> dict:
    """
    If an auth_key is provided, include BOTH common auth headers so the server
    can accept whichever it supports (Bearer or Azure APIM subscription key).
    """
    if not auth_key:
        return {}

    return {
        "Authorization": f"Bearer {auth_key}",
        "Ocp-Apim-Subscription-Key": auth_key,
    }


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
    headers.update(_build_auth_headers(auth_key))

    response = requests.post(url, json=payload, headers=headers)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"Request failed: {response.status_code}, {response.text}"
        ) from e

    return response.json()


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
    headers = _build_auth_headers(auth_key)

    # Check status
    full_url = f"{url}{session_id}" if session_id is not None else url
    status_response = requests.get(full_url, headers=headers)

    try:
        status_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise Exception(
            f"Status check failed for url {full_url}: {status_response.status_code}, {status_response.text}"
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
        pd.DataFrame: Loaded dataframe with columns sorted alphabetically.

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
            data = reader(filepath, **kwargs)
            # Sort columns alphabetically
            data = data[sorted(data.columns)]
            return data
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
        data = reader(filepath, **kwargs)
        # Sort columns alphabetically
        data = data[sorted(data.columns)]
        return data
    except Exception as e:
        raise Exception(f"Failed to load {extension} file: {e}") from e
