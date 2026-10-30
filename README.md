# GroceryLens — Sales Intelligence Dashboard

An interactive Streamlit dashboard for exploring the BlinkIT grocery dataset: sales, product categories, outlets, customer ratings and product visibility. A companion Excel workbook is included.

## What's in the dashboard
- **Overview** — KPI cards (total sales, average sales, average rating, best category, best outlet), top-N categories, outlet-type share donut, sales by outlet establishment year, Low Fat vs Regular by outlet.
- **Categories** — Pareto analysis (cumulative % curve), "categories needed for 80% of sales", outlet-type → category sunburst, sales-vs-rating bubble chart, category × outlet heatmap.
- **Outlets** — outlet ranking, violin plots, sales by location tier and outlet size, outlet age vs sales.
- **Ratings & Visibility** — rating distribution, rating by category, sales by visibility quartile, visibility vs sales scatter with trendline, correlation matrix.
- **Statistics** — mean/median/std/variance, skewness, kurtosis, percentiles, IQR outlier flags, histogram with box plot, cumulative distribution.
- **Insights** — auto-generated plain-English findings for the current filters, downloadable as Markdown.

Sidebar filters: category, outlet type, fat content, location tier, outlet size, rating range, and Top-N slider.

## Files
- `app.py` — the dashboard
- `BlinkIT_Grocery_Data.csv` — dataset (8,523 records, 12 columns)
- `BlinkIT Grocery Data.xlsx` — original dataset
- `Supermarket_Sales_Analysis.xlsx` — analysis workbook
- `requirements.txt` — dependencies

## Run locally (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Connect the repository to Streamlit Community Cloud, choose `app.py` as the main file.

## Data notes
- Fat-content labels are standardised (`LF`, `low fat` → `Low Fat`; `reg` → `Regular`).
- `Item Weight` has 1,463 missing values; they are ignored in correlations.
- Derived fields: `Outlet Age` (latest year − establishment year) and visibility quartiles.
- Outliers are flagged with the 1.5×IQR rule — a statistical flag, not proof of error.
- Correlation is descriptive, not causal. No currency is assumed.
