# 🚀 Inait Forecasting: Enterprise Time Series Forecasting Made Simple

## 🛠️ Quick Setup

### Prerequisites
- [UV](https://docs.astral.sh/uv/) - Modern Python package manager
- Python 3.8+ (automatically handled by UV)
- Your URL and API key for inait Forecasting

### Getting Started
1. **Clone and navigate to the directory:**
   ```bash
   cd inait-predict-examples
   ```

2. **Run the setup script:**
   ```bash
   ./setup.sh
   ```

3. **Start Jupyter Lab:**
   ```bash
   uv run jupyter lab
   ```

4. **Open the example notebooks:**
   Navigate to the `notebook-examples/` folder and choose from:
   - `basic_functionality.ipynb` - Complete API overview and synchronous predictions
   - `background_ensemble_prediction.ipynb` or `prediction_intervals_visualization.ipynb` - Asynchronous processing for large datasets

### Alternative Setup (Manual)
```bash
# Install dependencies
uv sync

# Run Jupyter
uv run jupyter lab

# Or run a specific notebook
uv run jupyter notebook notebook-examples/basic_functionality.ipynb
```

---

## 📊 Dataset Format Requirements

To ensure optimal performance with Inait Forecasting, your dataset must follow these formatting conventions:

### **📁 File Format**
- **Supported Format**: CSV (Comma-Separated Values)
- **Encoding**: UTF-8 recommended
- **Headers**: First row must contain column names

### **⏰ Time Series Structure**
- **Row Organization**: Each row represents a single timestamp observation
- **Temporal Ordering**: Rows must be sorted in **chronological order** (ascending timestamps)
- **Time Index**: Include a datetime column with consistent frequency
- **No Gaps**: Ensure regular time intervals (hourly, daily, etc.) without missing timestamps

### **📋 Required Columns**

#### **🎯 Target Column**
- **Purpose**: The variable you want to forecast
- **Name**: Can be any descriptive name (e.g., `"sales"`, `"price"`, `"demand"`)
- **Format**: Numeric values (integers or floats)
- **Example**: `"DE_Spot_EPEX_1H_A"` (electricity spot prices)

#### **📅 Time Index Column**
- **Purpose**: Timestamp for each observation
- **Format**: ISO datetime format recommended (`YYYY-MM-DD HH:MM:SS`)
- **Frequency**: Must be consistent (e.g., hourly, daily, weekly)
- **Example**: `"2024-01-01 00:00:00"`, `"2024-01-01 01:00:00"`, etc.

#### **📊 Exogenous Feature Columns (Optional)**
- **Purpose**: External variables that influence the target
- **Format**: Numeric values corresponding to each timestamp
- **Examples**: 
  - `"DE_Residual_Load_15M_A_AVG"` (grid load data)
  - `"DE_Consumption_15M_A_AVG"` (consumption patterns)
  - `"temperature"`, `"promotion_active"`, `"day_of_week"`

### **📈 Example Dataset Structure**

```csv
timestamp,DE_Spot_EPEX_1H_A,DE_Residual_Load_15M_A_AVG,DE_Consumption_15M_A_AVG
2024-01-01 00:00:00,45.23,32145.5,28932.1
2024-01-01 01:00:00,42.18,31245.2,27845.6
2024-01-01 02:00:00,38.95,30123.8,26789.3
2024-01-01 03:00:00,35.76,29456.1,25956.8
...
```

---

## Transform Your Data Into Actionable Predictions

Inait Forecasting is a powerful, user-friendly time series forecasting platform that democratizes advanced machine learning for businesses of all sizes. Whether you're predicting sales, demand, prices, or any time-dependent metrics, inait Forecasting delivers accurate forecasts without requiring deep ML expertise.

## 🎯 Why Choose inait Forecasting?

### **Effortless Accuracy**
- **5 Intelligent Models**: Choose from `basic`, `robust`, `neural`, `gradient_boost`, or `fast_boost` - each optimized for different data characteristics
- **Automatic Model Selection**: Let inait Forecasting pick the best approach for your data
- **Ensemble Power**: Combine multiple intelligent models above for maximum accuracy and reliability
- **Prediction Intervals**: Get confidence bounds, not just point estimates

### **Business-Ready Features**
- **REST API Integration**: Deploy predictions in minutes with simple HTTP calls
- **Background Processing**: For large datasets or complex models, the application works in background mode, allowing you to focus on other tasks while it processes your data. Query the operation status and download results when ready
- **Visual Insights**: Automatic chart generation for stakeholder presentations

### **Explainable AI**
- **Model Transparency**: Understand exactly what drives your predictions with clear explanations
- **Feature Importance**: See which variables matter most for your forecasts
- **Interactive Insights**: Drill down into any prediction to build trust and understanding

## 🏢 Perfect For Your Industry

### **Retail & E-commerce**
- **Demand Forecasting**: Optimize inventory with accurate sales predictions
- **Price Optimization**: Predict market responses to pricing changes
- **Seasonal Planning**: Handle complex seasonal patterns automatically

### **Finance & Trading**
- **Market Prediction**: Forecast prices, volatility, and trading volumes
- **Risk Management**: Predict default rates and financial metrics
- **Economic Analysis**: Model economic indicators and market trends

### **Manufacturing & Supply Chain**
- **Production Planning**: Forecast demand to optimize manufacturing schedules
- **Maintenance Prediction**: Predict equipment failures before they happen
- **Supply Chain Optimization**: Forecast lead times and inventory needs

### **Energy & Utilities**
- **Load Forecasting**: Predict energy demand across different time horizons
- **Renewable Integration**: Forecast solar and wind energy production
- **Grid Management**: Optimize energy distribution and storage

---

## A decision tree to pick the best solution for your case & data

```mermaid
flowchart TD
    A([START HERE])
    A --> B{Q1: How large is your typical dataset for a single job?}
    B -->|Massive: > 1 GB| C[SaaS SOLUTION<br>Why: Architected for multi-GB data;<br>avoids upload timeouts.]
    B -->|Standard: < 1 GB| D{Q2: How do you want to handle billing and procurement?}
    D -->|Single Bill on Azure Invoice| E[SaaS SOLUTION<br>Why: Simplifies procurement and billing through Azure.]
    D -->|Direct Invoice from INAIT| F{Q3: What is your preference for infrastructure management?}
    F -->|Zero Maintenance| G[SaaS SOLUTION<br>Why: A fully managed service with no operational overhead.]
    F -->|Full Control in own Tenant| H[MANAGED APPLICATION<br>Why: For compliance, access control,<br>or specific policy reasons.]
    
---

*inait Forecasting: Where advanced machine learning meets practical business solutions.*
