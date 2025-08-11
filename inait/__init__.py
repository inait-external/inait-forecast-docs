"""
Inait Forecasting Client Package

This package contains client utilities and scripts for interacting with the Inait Forecasting API.
"""

from .utils import make_request, make_get_request
from .prediction_script import create_payload_from_file, get_dataframe_from_response
from .plot_script import create_plot_payload, plot_image, bytes_from_base64
from .explanation_script import create_explanation_payload

__version__ = "0.1.0"
__author__ = "Inait Team"

__all__ = [
    "make_request",
    "make_get_request",
    "create_payload_from_file",
    "get_dataframe_from_response",
    "create_plot_payload",
    "plot_image",
    "bytes_from_base64",
    "create_explanation_payload",
    "predict",
    "plot",
]
