# User Manual — Preparing Data for FutureComplete

The purpose of this document is to guide any user through the process of preparing time series data to use with the forecasting tool `FutureComplete`. It covers the required data format, quality requirements, supported file types, and how to configure the tool to read your data correctly.



## 1. Overview

The forecasting tool accepts **time series data in ['wide' tabular format][wide_wiki]**. Before you can run a prediction, you must deliver a single table in which:

- every **row** represents one observation at a single point in time,
- every **column** represents one time series (either a variable you want to predict, i.e. a 'target', or a variable you want to use as input, i.e. 'feature'),
- one column that identifies the **timestamp** of each row (usually, the first column of the table).

[wide_wiki]: https://en.wikipedia.org/wiki/Wide_and_narrow_data

This document explains exactly how to build that table and how to declare it in the configuration.

---

## 2. The Wide Table Format

### 2.1 Structure

```
Date        | target_A | target_B | feature_1 | feature_2 | ...
------------|----------|----------|-----------|-----------|----
2020-01-01  |   1.23   |   4.56   |   0.10    |   7.80    |
2020-01-02  |   1.25   |   4.61   |   0.12    |   7.75    |
2020-01-03  |   1.19   |   4.59   |   0.09    |   7.82    |
...
```

**One row = one time step.** If your data is daily, each row is one calendar or business day. If it is monthly, each row is one month. Mixed frequencies are not supported within a single table.

**One column = one series.** Both target series (what you want to forecast) and explanatory series (features you provide as context, which should act as drivers or provide more information for the targets) live as separate columns in the same table. There is no nesting, no multi-level column header, and no separate files for targets vs. features.

### 2.2 The Date column

- There must be exactly **one** column containing the timestamp of each row. If there are more (or none is found), an error will be returned.
- It is important to have a clear and consistent format. Examples are:
    - YYYY-MM-DD, e.g. 2024-03-15 
    - YYYY-MM-DD HH:MM:SS, e.g. 2024-03-15 09:30:00 
    - DD/MM/YYYY, e.g. 15/03/2024 
    - MM/DD/YYYY, e.g. 03/15/2024 
    - DD.MM.YYYY, e.g. 15.03.2024 
    - DD Mon YYYY, e.g. 15 Mar 2024
- For Python users: all Pandas timestamp format are accepted. When multiple patterns match (e.g. 03/04/2024 could be day-first or month-first), the system picks the one that produces the most regularly-spaced intervals.
- If there are duplicates or gaps, the tool should be able to handle them by filling the gaps with NaN values and removing duplicated rows. However, it is best to clean your data beforehand to avoid unexpected behaviour. 
- A frequency for the data is inferred. If there are missing data within the inferred frequency, the tool imputes missing values (NaN) by forward-filling them, i.e. by repeating the last valid value.

### 2.3 Target column(s)

These are the series the tool will learn to forecast. Rules:

- Values must be **numeric and finite** (no `Inf`). Missing values are allowed.
- Values are used **as-is**: the tool does not expect you to pre-shift them by the forecast horizon. That alignment is handled internally (see `forecasting_horizon` in §5).
- Any real-valued series is accepted.
- For **multi-target** problems, simply include several columns in the same table and list all of them under `target_columns` in the configuration. Different column names are spaced by commas (",") and inside square brackets ("[...]"), e.g. ["target_1","target_2"]. See below for further examples. When multiple targets are present, the model can leverage Cross Learning — training across all series simultaneously — which improves forecast quality, especially when individual series are short.
- IMPORTANT: please, avoid double underscores ("__") in the names of your target columns, as this is a reserved pattern for Local Features (see §2.4).

### 2.4 Features or Explanatory column(s)

These are optional input features that the model may use to improve its forecasts. Rules:

- Values must be **numeric and finite** (no `Inf`). Missing values are allowed.
- They must be **contemporaneous**: the value in row `t` must be information that is genuinely available at time `t`. Do not include series that would only be known in the future at the time the forecast is issued, unless you have already shifted them appropriately.
- IMPORTANT: Features at row `t` will be used to predict targets at row `t+1`.
- If you do not provide any explanatory columns, the tool will forecast using only the history of the target series itself.
- NOTE: all explanatory columns are shared across all target columns. This means that, looking at the table above, the columns `feature_1a` and `feature_1b`<sup>[1](#myfootnote1)</sup> will be used as features when trying to predict both `target_A` and `target_B`. If you need to specialize some features for some targets, we can use "local features".
- Local features give the possibility of specifying which explanatory columns should be used for specific targets. To do so, it is necessary to give such columns names that include the target as a prefix, separated by `__` (double underscore). For example, we could have `target_A__feature_1a` and `target_B__feature_1b` as columns in the table, and the tool would use `feature_1a` only for forecasting `target_A` and `feature_1b` only for forecasting `target_B`. 
- Note that
  - if we have local features, we can still have global features that are shared across all targets. For example, we could have `feature_2` as a global feature used for both `target_A` and `target_B`, while `feature_1a` and `feature_1b` are local features used only for `target_A` and `target_B`, respectively.
  - if we have a `feature_1` that is used as a local feature for a target, then we should have another local feature with the same name for all the other targets.


<a name="myfootnote1">1</a>: The suffixes "a" and "b" are just examples to imply that the columns are actually different, but the name of the feature should be the same. In practice, we would have, for example, `target_A__temperature` and `target_B__temperature`, or `target_A__price_index` and `target_B__price_index`, etc. The important point is that the part after the double underscore is the same for all targets, while the part before the double underscore identifies the target for which the feature is used.


---

## 3. Data Quality Requirements/Suggestions

| Requirement                      | Details                                                                                                                                                                                                                                                  |
|----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **No duplicate dates**           | Each row must have a unique timestamp.                                                                                                                                                                                                                   |
| **Gaps in the date index**       | Missing dates never cause a failure — they are always filled with last valid numbers.                                                                                                                                                                    |
| **Consistent frequency**         | All rows must be spaced by the same time interval. E.g. do not mix daily and weekly rows.                                                                                                                                                                |
| **Numeric targets and features** | String columns are not accepted (encode them numerically beforehand). Boolean will be converted to 0 (False) / 1 (True).                                                                                                                                 |
| **Sufficient history**           | The tool needs enough historical rows to train. Very short series will degrade forecast quality. This can be offset by including more targets, which automatically triggers Cross Learning — see §2.3 and §2.4 for more details. |

---

## 4. Supported Input File Formats

You may deliver your wide table as any of the following:

| Format | Notes                                                                             |
|---|-----------------------------------------------------------------------------------|
| **CSV** (`.csv`) | Standard comma-separated. The timestamp column should appear as a regular column. |
| **Excel** (`.xlsx`) | Supported only if single-sheet document.                                          |
| **Parquet** (`.pq` / `.parquet`) | Recommended for large datasets (faster I/O, preserves dtypes).                    |

Note 1: Excel files (`.xlsx`) are supported, but it is preferable to convert data to CSV, i.e. save as CSV ("Comma Separated Value") file. This forces the document to have a single sheet and avoids issues with merged cells, formatting, and other Excel-specific features that can interfere with data parsing. If you choose to use Excel files, make sure they are well-structured and do not contain any of these complexities.

Note 2: Input data provided to FutureComplete should occupy less than 200 MB.


---

## 5. Configuration Reference

Once your table is ready, you need to declare target, explanatory variables. The parameters below control how the tool reads and uses your data.

### 5.1 target_columns *(required)*

The name(s) of the column(s) you want to forecast.

```yaml
# Single target
targets: "sales_volume"

# Multiple targets
targets: ["product_A", "product_B", "product_C"]
```

### 5.2 forecasting_horizon *(required)*

How many time steps ahead to forecast. This is an integer matching the unit of your date frequency.

If the user is interested in multiple forecasting horizons at the same time, it will be enough to provide only the largest one, and the tool will automatically produce forecasts for all intermediate horizons. For example, if you set `forecasting_horizon: 7`, the tool will produce forecasts for horizons 1, 2, 3, ..., 7.

```yaml
forecasting_horizon: 7    # 7 days ahead (for a daily table)
# or
forecasting_horizon: 3    # 3 months ahead (for a monthly table)
# or
forecasting_horizon: 63   # 63 calendar days ahead (for a daily table)
```

The tool automatically aligns features at time `t` with the target at time `t + forecasting_horizon`. **Do not pre-shift your data.** The timestamp column always refers to the date of the *observation*, not the date the forecast was issued.

### 5.3 explanatory_columns *(optional)*

The names of the feature columns to pass to the model. If omitted, the tool uses all columns that are not listed in `target_columns`.

```yaml
# Single target
features: "temperature"

# Multiple targets
features: ["temperature", "is_holiday", "price_index"]
```

### 5.4 backtest_size (only relevant for *backtest*)

Number of time steps reserved for out-of-sample evaluation at the end of the series.
Either `backtest_size` or `start_date` + `end_date` must be provided to run a backtest.
If both are provided, only `backtest_size` will be used, and `start_date` + `end_date` will be ignored.

```yaml
backtest_size: 365   # Last 365 days held out for testing (for a dataset with daily frequency)
```


### 5.5 start_date and end_date *(optional)*

Start and end timestamp for the backtest (inclusive). This allows you to restrict the backtest to a specific time window, without modifying the input file.
`start_date` is only available for backtests, while `end_date` is also available for predictions (all timestamps after `end_date` will be ignored). 
If both are provided, `backtest_size` should not be filled (`end_date` can still be used to decide where to stop predictions or backtests)

Below an example to have a 2-months backtest starting from January 1st, 2019:
```yaml
start_date: "2019-01-01"
end_date: "2019-03-01"
```


### 5.6 prediction_stride *(optional, only relevant for backtest)*
The stride length for prediction windows or, in other words, the step size between consecutive forecast origins. This controls how frequently the model is asked to produce forecasts. By default, the tool produces forecasts at every possible time step (i.e. stride of 1). 
If the `prediction_stride` is larger than `forecasting_horizon`, then it will be capped to be equal to `forecasting_horizon`. Setting a stride equal to `forecasting_horizon` will produce non-overlapping forecasts, which can speed up backtesting and reduce the number of predictions.

```yaml
prediction_stride: 7   # Issue a new forecast every 7 days
```
NOTE: If the `prediction_stride` is not a divisor of `forecasting_horizon`, the `prediction_stride` will be automatically set to 1.



### 5.7 prediction_interval_levels *(optional)*
List of confidence levels for which to produce prediction intervals. For example, if you want 90% and 95% prediction intervals, set this to `[0.9, 0.95]`. By default, no prediction intervals are produced.

```yaml
prediction_interval_levels: [0.9, 0.95]
```


### 5.8 run_explain and include_genai_summary *(optional)*
These two parameters are boolean flags to control whether to run the explainability module and include a GenAI summary in the report that explains in plain words the explainability analysis. By default, both are set to `False` to speed up execution. Set them to `True` if you want to generate explanations and a natural language summary of the forecasts.

NOTE: `include_genai_summary` can only be set to `True` if `run_explain` is also `True`, since the GenAI summary relies on the outputs of the explainability module.

```yaml
run_explain: True
include_genai_summary: True
```



## 6. Pre-delivery Checklist

Use this checklist as a final review before running a forecast:

- [ ] The table is in **wide format**: one row per time step, one column per series.
- [ ] There is a **timestamp** column with regular (possibly gap-free and non-duplicate) timestamps.
- [ ] All target and feature columns contain **numeric, finite values**. Target columns' names do not contain double underscores ("__").
- [ ] Feature columns contain only **past or contemporaneous information** — no future leakage.
