
# Inait Forecasting – Examples & Notebooks

This README is **only** about running the examples (notebooks + helper utilities).  
For Azure purchasing/deployment of the Managed App, see **[package-README.md](./package-README.md)**.

> New to inait Forecasting? See **[Why Choose inait Forecasting](./package-README.md#why-choose-inait-forecasting)** for a quick overview of models, ensembles, explainability, and industry use cases.

---

# One‑click: run the notebooks

## MyBinder (no local install)
Click the first **MyBinder badge** below to **run directly on your browser**.
First launch per commit may take a few minutes while the image builds.

### Stable Version (Prod)

[![run Stable Version on Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/inait-external/inait-forecast-docs/prod_branch) 

#### Latest Version (Unstable)

[![run HEAD on Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/inait-external/inait-forecast-docs/HEAD)

### Configure API access

**A) `credentials.txt` (default used by notebooks)**  
Create/edit a `credentials.txt` at the repo root:
```bash
API_BASE_URL='https://<your-forecast-endpoint>'
API_AUTH_KEY='<your-api-key>'
```

----

### GitHub Codespaces
Click the Codespaces badge. On first start, the dev container installs `uv`, runs `make init` to create `.venv`, and registers the **Python (inait‑uv)** kernel. Open `notebook-examples/` and start any notebook.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/inait-external/inait-forecast-docs?quickstart=1)

----

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

**A) `credentials.txt` (default used by notebooks)**  
Create/edit a `credentials.txt` at the repo root:
```bash
API_BASE_URL='https://<your-forecast-endpoint>'
API_AUTH_KEY='<your-api-key>'
```

**B) `.env` (supported via python‑dotenv)**  
Create `.env` at the repo root:
```ini
API_BASE_URL="https://<your-forecast-endpoint>"
API_AUTH_KEY="<your-api-key>"
```

> Don’t have an endpoint yet? See **[package-README.md](./package-README.md)** to deploy the Managed App and obtain credentials.

---

## Notebook catalog

Run top‑to‑bottom:

| Notebook | What it shows |
|---|---|
| `notebook-examples/0_quickstart.ipynb` | **Start here.** Configure credentials, submit your first forecast, and visualize results. |
| `notebook-examples/1_advanced_model_evaluation.ipynb` | Advanced models and evaluation on ETTh1‑style data; compare approaches. |
| `notebook-examples/2_energy_forecast_interpretability.ipynb` | **Explainability** for energy datasets: feature attributions and insights. |
| `notebook-examples/3_sales_forecast_with_uncertainty.ipynb` | Sales forecasting with **prediction intervals** (uncertainty bands). |

---

## Sample data

Small CSVs live in `data/`:

- `data/airline.csv` – classic monthly airline passengers  
- `data/etth1.csv` / `data/etth1_small.csv` – ETTh1‑like energy data (full & small)  
- `data/M5_store_CA_1.csv` – single‑store sample in the M5 style  
- `data/power_day_ahead.csv` – dayahead power demand/prices style

**Expected format** (simplified):
- A timestamp column with consistent frequency (hourly, daily, …)  
- A numeric target column to forecast  
- Optional exogenous feature columns aligned to the same timestamps

---

## Optional: Python helpers & CLI

Lightweight utilities live under `inait/`:

```bash
# Show command help
uv run python -m inait.prediction_script --help
uv run python -m inait.plot_script --help
uv run python -m inait.explanation_script --help
```

---

## Troubleshooting

- **Kernel mismatch (Codespaces)**: ensure the notebook kernel is **Python (inait‑uv)**.  
- **Import errors in terminal**: `uv sync && source .venv/bin/activate`.  
- **Auth errors (401/403)**: check `API_AUTH_KEY` and tenant for your endpoint.  
- **Background jobs**: some examples poll until completion—keep the cell running.

**Next:** Azure purchase & deployment → **[package-README.md](./package-README.md)**
