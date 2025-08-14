"""
Inait Forecasting Client Package

This package contains client utilities and scripts for interacting with the Inait Forecasting API.
"""

from .utils import make_request, make_get_request, load_credentials
from .prediction_script import (
    create_payload_from_file,
    get_dataframe_from_response,
    predict,
    predict_test,
    score_test,
    check_coverage,
)
from .plot_script import create_plot_payload, plot_image, bytes_from_base64, plot
from .explanation_script import explain, create_explanation_payload

__version__ = "0.1.0"
__author__ = "Inait Team"

__all__ = [
    "bytes_from_base64",
    "create_explanation_payload",
    "create_payload_from_file",
    "create_plot_payload",
    "explain",
    "get_dataframe_from_response",
    "make_get_request",
    "make_request",
    "plot_image",
    "plot",
    "predict",
    "load_credentials",
    "predict_test",
    "score_test",
    "check_coverage",
]
