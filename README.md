# FutureComplete – Examples & Notebooks

This README is **only** about running the examples (notebooks + helper utilities). For Azure purchasing/deployment see **[package-README](./package-README.md)**.

---

<details>
<summary><strong>Table of Contents</strong></summary>

- [Run the Notebooks](#run-the-notebooks)
  - [Binder (no local install)](#binder-no-local-install)
  - [GitHub Codespaces](#github-codespaces)
  - [Local (uv)](#local-uv)
- [Configure API access](#configure-api-access)
- [Notebook Example](#notebook-example)
- [Sample data](#sample-data)
- [FutureComplete UI](#futurecomplete-ui)
- [Troubleshooting](#troubleshooting)

</details>

---

## Run the Notebooks

Choose one of the three options below. Once your environment is running, follow the [Configure API access](#configure-api-access) section before running any notebook.

> **First time with Jupyter notebooks?** Click **"Run"** in the top menu and select **"Run All Cells"**. If you get a `timeout error`, restart the Kernel and try again (**"Kernel"** → **"Restart & Clear Output"**).

### Binder (no local install)

Click the badge below to run directly in your browser. The first launch of an updated version may take a few minutes while the image builds.

**Stable version (recommended)**

[![run Stable Version on Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/inait-external/inait-forecast-docs/prod)

**Latest version (unstable)**

[![run HEAD on Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/inait-external/inait-forecast-docs/HEAD)

---

### GitHub Codespaces

Click the badge below. On first start, the dev container installs `uv`, runs `make init` to create `.venv`, and registers the **Python (inait‑uv)** kernel. Open `futurecomplete-examples/` and start any notebook.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/inait-external/inait-forecast-docs?quickstart=1)

---

### Local (uv)

```bash
# 1) Install uv (Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2) From the repo root, set up deps (creates .venv from pyproject.toml)
make init   # or: uv sync

# 3) Launch JupyterLab
uv run jupyter lab
```

---

## Configure API access

Regardless of how you launched the notebooks, API access is configured the same way. Edit (or create) a `credentials.txt` file at the root of the repo:

```bash
API_BASE_URL='https://api.forecasting.inait.ai'
API_AUTH_KEY='your-api-key'
```

> Don't have credentials yet? See **[package-README](./package-README.md)** to obtain them.

---

## Notebook Example

Python notebooks help you understand how to integrate API calls in your code and explore results. They are intended as a reference for your own implementation, not for direct production use.

The current example (`futurecomplete-examples/volatility_prediction_use_case.ipynb`) walks through a full forecasting workflow — predictions, backtesting, and explainability — using volatility data for AAPL (Apple Inc.) and MSFT (Microsoft Corp.) stocks.

More examples covering additional use cases and asset classes are coming soon.

---

## Sample data

Sample CSVs are available in `data/`. The current dataset (`data/dataset_GKYZ_2016_AAPL_MSFT_trimmed.csv`) contains Apple and Microsoft stock data for volatility modeling.

All sample files follow the same expected format: a timestamp column with consistent frequency (hourly, daily, …), followed by one or more numeric target columns and optional exogenous variables, all aligned to the same timestamps. For full details on data formatting, see the **[Input Data Guide](./data_input_guide.md)**.

---

## FutureComplete UI

For a simplified no-code experience, you can submit forecasts and backtests through the FutureComplete UI. Upload your data, configure your job, and visualize results directly in the browser.

Access the UI at [https://futurecomplete.inait.ai](https://futurecomplete.inait.ai/) — you will be prompted for your `Access Token`, which is the same authentication key used in `credentials.txt`.

---

## Troubleshooting

- **Kernel mismatch (Codespaces)**: ensure the notebook kernel is **Python (inait‑uv)**.
- **Import errors in terminal**: run `uv sync && source .venv/bin/activate`.
- **Auth errors (401/403)**: check `API_AUTH_KEY` and the tenant for your endpoint.
- **Background jobs**: some examples poll until completion — keep the cell running.
- **Issues**: [github.com/inait-external/inait-forecast-docs/issues](https://github.com/inait-external/inait-forecast-docs/issues)
- **Email**: contact@inait.ai

---

**Ready for the Next step?** Get Enterprise-grade FutureComplete in Azure: purchase & deployment → **[package-README](./package-README.md)**
