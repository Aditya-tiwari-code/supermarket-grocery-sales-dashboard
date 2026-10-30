import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import random

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GroceryLens | Sales Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

PALETTE  = ["#0F766E", "#F59E0B", "#6366F1", "#EF4444", "#14B8A6",
            "#EC4899", "#84CC16", "#0EA5E9", "#F97316", "#8B5CF6"]
SEQ      = "Tealgrn"
TEMPLATE = "simple_white"

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── layout ── */
.block-container {padding-top: 1rem; padding-bottom: 2rem;}

/* ── hero ── */
.hero {
  background: linear-gradient(135deg, #0F766E 0%, #0D9488 40%, #6366F1 100%);
  padding: 1.6rem 2rem; border-radius: 20px; color: #fff;
  margin-bottom: 1.2rem; box-shadow: 0 4px 24px rgba(15,118,110,.25);
}
.hero h1 {margin: 0; font-size: 2.1rem; color: #fff; letter-spacing: -.5px;}
.hero p  {margin: .4rem 0 0; opacity: .88; font-size: 1.05rem;}

/* ── KPI cards ── */
div[data-testid="stMetric"] {
  background: linear-gradient(135deg, #F0FDFA 0%, #fff 100%);
  border-left: 5px solid #0F766E; padding: .9rem 1.1rem;
  border-radius: 14px; box-shadow: 0 2px 10px rgba(0,0,0,.06);
  transition: transform .15s;
}
div[data-testid="stMetric"]:hover {transform: translateY(-2px);}
div[data-testid="stMetric"] label,
div[data-testid="stMetricValue"] {color: #134E4A !important;}
div[data-testid="stMetricDelta"] {font-size: .78rem;}

/* ── insight card ── */
.insight-card {
  background: #FFFBEB; border-left: 5px solid #F59E0B;
  padding: .85rem 1.1rem; border-radius: 10px;
  margin: .45rem 0; color: #78350F; line-height: 1.6;
}
.insight-card .icon {font-size: 1.25rem; margin-right: .4rem;}

/* ── story card ── */
.story-card {
  background: linear-gradient(135deg, #EFF6FF 0%, #F5F3FF 100%);
  border-radius: 14px; padding: 1.1rem 1.4rem; margin: .6rem 0;
  border: 1px solid #C7D2FE; color: #1E1B4B;
}
.story-card h4 {margin: 0 0 .3rem; color: #4338CA; font-size: 1rem;}

/* ── compare card ── */
.compare-box {
  background: #F0FDF4; border: 1.5px solid #6EE7B7;
  border-radius: 14px; padding: 1rem 1.3rem; margin-bottom: .5rem;
}

/* ── fun fact ── */
.fun-fact {
  background: linear-gradient(135deg, #FFF7ED 0%, #FFF 100%);
  border: 1.5px dashed #FDBA74; border-radius: 12px;
  padding: .8rem 1.1rem; color: #9A3412; margin: .5rem 0;
}

/* ── section header ── */
.sec-header {
  font-size: 1.1rem; font-weight: 700; color: #0F766E;
  border-bottom: 2px solid #99F6E4; padding-bottom: .3rem;
  margin: 1.2rem 0 .6rem;
}

/* ── sidebar ── */
[data-testid="stSidebar"] {background: #F0FDFA;}
[data-testid="stSidebar"] h2 {color: #0F766E;}

/* ── tab bar ── */
button[data-baseweb="tab"] {font-size: .95rem; font-weight: 600;}
button[data-baseweb="tab"][aria-selected="true"] {
  border-bottom: 3px solid #0F766E !important; color: #0F766E !important;
}

/* ── expander ── */
details summary {font-weight: 600; color: #0F766E;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  DATA LOADING
# ─────────────────────────────────────────────
@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        data = (pd.read_csv(uploaded_file)
                if uploaded_file.name.lower().endswith(".csv")
                else pd.read_excel(uploaded_file))
    else:
        csv_path  = Path(__file__).parent / "BlinkIT_Grocery_Data.csv"
        xlsx_path = Path(__file__).parent / "BlinkIT Grocery Data.xlsx"
        data = pd.read_csv(csv_path) if csv_path.exists() else pd.read_excel(xlsx_path)

    data.columns = data.columns.str.strip()
    data["Item Fat Content"] = data["Item Fat Content"].replace(
        {"LF": "Low Fat", "low fat": "Low Fat", "reg": "Regular"}
    )
    data["Outlet Age"] = data["Outlet Establishment Year"].max() - data["Outlet Establishment Year"]
    data["Visibility Band"] = pd.qcut(
        data["Item Visibility"].rank(method="first"), 4,
        labels=["Lowest 25%", "Low-mid", "High-mid", "Highest 25%"]
    )
    return data


def fmt(n):
    for unit, div in (("M", 1e6), ("K", 1e3)):
        if abs(n) >= div:
            return f"{n / div:,.2f}{unit}"
    return f"{n:,.2f}"


def human_pct(p):
    if p >= 50:  return f"a dominant {p:.1f}%"
    if p >= 30:  return f"a solid {p:.1f}%"
    if p >= 15:  return f"a decent {p:.1f}%"
    return f"a modest {p:.1f}%"


def rating_label(r):
    if r >= 4.5: return "⭐ Outstanding"
    if r >= 4.0: return "😊 Very Good"
    if r >= 3.5: return "👍 Good"
    return "😐 Average"


FUN_FACTS = [
    "💡 Did you know? Supermarkets stock ~30,000 SKUs on average — yet 80% of sales come from under 20% of them.",
    "🛒 Fact: Products placed at eye level sell up to 35% more than those on lower shelves.",
    "📦 Insight: Low-fat labels boost perceived healthiness, which can increase purchase intent by ~20%.",
    "🏪 Fact: Tier-1 city outlets report higher basket sizes but lower visit frequency than Tier-3 stores.",
    "📊 Insight: A 1-star rating improvement correlates with ~5–9% revenue uplift in grocery retail.",
]


# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 GroceryLens")
    st.caption("Your personal grocery sales explorer")
    st.divider()

    uploaded = st.file_uploader(
        "📂 Drop your own dataset (CSV / Excel)",
        type=["csv", "xlsx"],
        help="Leave blank to use the default BlinkIT dataset."
    )
    data = load_data(uploaded)

    st.markdown("### 🎛️ Filter the data")

    def multi(label, col, icon=""):
        opts = sorted(data[col].dropna().unique())
        return st.multiselect(f"{icon} {label}", opts, default=opts)

    with st.expander("🧺 Products", expanded=True):
        selected_categories = multi("Item categories", "Item Type")
        selected_fat        = multi("Fat content",     "Item Fat Content")

    with st.expander("🏬 Outlets", expanded=True):
        selected_outlets   = multi("Outlet types",    "Outlet Type")
        selected_locations = multi("Location tiers",  "Outlet Location Type")
        selected_sizes     = multi("Outlet sizes",    "Outlet Size")

    with st.expander("⭐ Quality", expanded=False):
        r_min, r_max   = float(data["Rating"].min()), float(data["Rating"].max())
        rating_range   = st.slider("Rating range", r_min, r_max, (r_min, r_max), step=0.1)

    top_n = st.slider("🔢 Top-N categories to highlight", 3, 16, 8)

    st.divider()
    if st.button("🔄 Reset all filters", use_container_width=True):
        st.rerun()

    st.caption("💬 Tip: Use filters to drill into a specific segment, then check the **💡 Story** tab for plain-English insights.")


# ─────────────────────────────────────────────
#  APPLY FILTERS
# ─────────────────────────────────────────────
filtered = data[
    data["Item Type"].isin(selected_categories)
    & data["Outlet Type"].isin(selected_outlets)
    & data["Item Fat Content"].isin(selected_fat)
    & data["Outlet Location Type"].isin(selected_locations)
    & data["Outlet Size"].isin(selected_sizes)
    & data["Rating"].between(*rating_range)
].copy()

if filtered.empty:
    st.error("😕 No records match your current filters. Try broadening your selection in the sidebar.")
    st.stop()


# ─────────────────────────────────────────────
#  HERO BANNER
# ─────────────────────────────────────────────
pct_shown = len(filtered) / len(data) * 100
st.markdown(f"""
<div class="hero">
  <h1>🛒 GroceryLens — Sales Intelligence</h1>
  <p>Exploring <strong>{len(filtered):,}</strong> of <strong>{len(data):,}</strong> records &nbsp;·&nbsp;
     <strong>{pct_shown:.1f}%</strong> of the full BlinkIT dataset visible with your current filters.</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  KPIs
# ─────────────────────────────────────────────
total_sales   = filtered["Sales"].sum()
all_sales     = data["Sales"].sum()
share_of_all  = total_sales / all_sales * 100
cat_totals    = filtered.groupby("Item Type")["Sales"].sum().sort_values(ascending=False)
out_totals    = filtered.groupby("Outlet Identifier")["Sales"].sum().sort_values(ascending=False)
avg_sales     = filtered["Sales"].mean()
avg_rating    = filtered["Rating"].mean()
total_records = len(filtered)

# compare against full dataset averages
all_avg_sales  = data["Sales"].mean()
all_avg_rating = data["Rating"].mean()
delta_sales    = avg_sales - all_avg_sales
delta_rating   = avg_rating - all_avg_rating

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("💰 Total Sales",         fmt(total_sales),
          f"{share_of_all:.1f}% of full dataset",
          help="Sum of all 'Sales' values in the filtered view.")
k2.metric("📦 Avg Sale / Record",   f"₹ {avg_sales:,.2f}",
          f"{delta_sales:+.2f} vs full data",
          help="How the average sale in this filter compares to the whole dataset.")
k3.metric("⭐ Avg Customer Rating", f"{avg_rating:.2f}",
          f"{delta_rating:+.2f} vs full data",
          help="Higher is better. Full dataset average is shown as delta.")
k4.metric("🏆 Best Category",       cat_totals.index[0],
          f"{cat_totals.iloc[0] / total_sales * 100:.1f}% of sales",
          help="Category contributing the most revenue in this filter.")
k5.metric("🏬 Top Outlet",          out_totals.index[0],
          f"₹ {fmt(out_totals.iloc[0])}",
          help="Single outlet with highest total sales.")


# ─────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────
(tab_over, tab_cat, tab_out, tab_rate,
 tab_stat, tab_compare, tab_story) = st.tabs([
    "🏠 Overview", "🧺 Categories", "🏬 Outlets",
    "⭐ Ratings & Visibility", "📐 Statistics",
    "🔀 Compare Outlets", "💡 Story & Insights",
])


# ══════════════════════════════════════════════
#  TAB 1 — OVERVIEW
# ══════════════════════════════════════════════
with tab_over:
    st.markdown('<div class="sec-header">📊 Sales at a glance</div>', unsafe_allow_html=True)

    left, right = st.columns(2)
    top = cat_totals.head(top_n).reset_index()
    fig_bar = px.bar(
        top, x="Sales", y="Item Type", orientation="h",
        color="Sales", color_continuous_scale=SEQ,
        title=f"🏆 Top {top_n} categories by revenue",
        template=TEMPLATE,
        labels={"Sales": "Revenue (₹)", "Item Type": "Category"},
    ).update_yaxes(autorange="reversed").update_traces(
        hovertemplate="<b>%{y}</b><br>Revenue: ₹%{x:,.0f}<extra></extra>"
    )
    left.plotly_chart(fig_bar, use_container_width=True)
    left.caption(f"👆 **{top['Item Type'].iloc[0]}** alone accounts for "
                 f"{top['Sales'].iloc[0] / total_sales * 100:.1f}% of your filtered revenue. "
                 "Click the legend items to isolate bars.")

    by_type = filtered.groupby("Outlet Type", as_index=False)["Sales"].sum()
    fig_pie = px.pie(
        by_type, names="Outlet Type", values="Sales", hole=0.58,
        color_discrete_sequence=PALETTE,
        title="🏪 Revenue share by outlet type",
        template=TEMPLATE,
    ).update_traces(hovertemplate="<b>%{label}</b><br>₹%{value:,.0f}<br>%{percent}<extra></extra>")
    right.plotly_chart(fig_pie, use_container_width=True)
    top_out_type = by_type.sort_values("Sales", ascending=False).iloc[0]
    right.caption(f"👆 **{top_out_type['Outlet Type']}** leads with "
                  f"{top_out_type['Sales'] / total_sales * 100:.1f}% of revenue. "
                  "Hover slices for exact values.")

    st.markdown('<div class="sec-header">📅 How outlet age affects revenue</div>', unsafe_allow_html=True)
    yearly = filtered.groupby("Outlet Establishment Year", as_index=False)["Sales"].sum()
    fig_area = px.area(
        yearly, x="Outlet Establishment Year", y="Sales", markers=True,
        color_discrete_sequence=[PALETTE[0]],
        title="Revenue by outlet establishment year",
        template=TEMPLATE,
        labels={"Sales": "Total Revenue (₹)", "Outlet Establishment Year": "Year Established"},
    ).update_traces(
        hovertemplate="<b>Est. %{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
        fill="tozeroy", fillcolor="rgba(15,118,110,0.12)"
    )
    peak_yr = yearly.loc[yearly["Sales"].idxmax()]
    st.plotly_chart(fig_area, use_container_width=True)
    st.caption(f"📌 Outlets established in **{int(peak_yr['Outlet Establishment Year'])}** "
               f"generated the most revenue (₹ {fmt(peak_yr['Sales'])}). "
               "This could reflect a larger network of stores opened that year.")

    st.markdown('<div class="sec-header">🥗 Low Fat vs Regular across outlets</div>', unsafe_allow_html=True)
    fat = filtered.groupby(["Outlet Identifier", "Item Fat Content"], as_index=False)["Sales"].sum()
    fat_pct = fat.copy()
    tot = fat_pct.groupby("Outlet Identifier")["Sales"].transform("sum")
    fat_pct["Share"] = fat_pct["Sales"] / tot * 100
    fig_fat = px.bar(
        fat, x="Outlet Identifier", y="Sales", color="Item Fat Content",
        barmode="stack", color_discrete_sequence=[PALETTE[0], PALETTE[1]],
        title="Low Fat vs Regular product revenue by outlet",
        template=TEMPLATE,
        labels={"Sales": "Revenue (₹)", "Outlet Identifier": "Outlet"},
    ).update_traces(hovertemplate="<b>%{x}</b><br>%{fullData.name}: ₹%{y:,.0f}<extra></extra>")
    st.plotly_chart(fig_fat, use_container_width=True)
    lf = filtered[filtered["Item Fat Content"] == "Low Fat"]["Sales"].sum()
    st.caption(f"🥗 Low-fat products account for **{lf / total_sales * 100:.1f}%** of total revenue. "
               "This reflects growing consumer preference for healthier options.")

    # Fun fact
    st.markdown(f'<div class="fun-fact">🎲 <b>Random Fact</b> &nbsp;—&nbsp; {random.choice(FUN_FACTS)}</div>',
                unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  TAB 2 — CATEGORIES
# ══════════════════════════════════════════════
with tab_cat:
    cat = filtered.groupby("Item Type", as_index=False).agg(
        Total_Sales=("Sales", "sum"), Average_Sales=("Sales", "mean"),
        Average_Rating=("Rating", "mean"), Records=("Sales", "size"),
    ).sort_values("Total_Sales", ascending=False)
    cat["Cumulative_%"] = cat["Total_Sales"].cumsum() / cat["Total_Sales"].sum() * 100

    n80 = int((cat["Cumulative_%"] < 80).sum() + 1)
    top_share = cat.head(top_n)["Total_Sales"].sum() / total_sales * 100

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Top {min(top_n, len(cat))} categories' share",
              f"{top_share:.1f}%", help="Revenue concentration in the top N.")
    c2.metric("Categories for 80% of revenue", n80, f"of {len(cat)} total",
              help="Pareto: how many categories drive 80% of sales?")
    c3.metric("Avg revenue per category",
              f"₹ {fmt(total_sales / len(cat))}",
              help="Even distribution benchmark.")

    # Pareto
    st.markdown('<div class="sec-header">📈 Pareto — which categories matter most?</div>', unsafe_allow_html=True)
    pareto = go.Figure()
    pareto.add_bar(
        x=cat["Item Type"], y=cat["Total_Sales"], name="Revenue (₹)",
        marker_color=PALETTE[0],
        hovertemplate="<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<extra></extra>",
    )
    pareto.add_scatter(
        x=cat["Item Type"], y=cat["Cumulative_%"], name="Cumulative %",
        yaxis="y2", mode="lines+markers",
        line=dict(color=PALETTE[1], width=3),
        hovertemplate="<b>%{x}</b><br>Cumulative: %{y:.1f}%<extra></extra>",
    )
    pareto.add_hline(y=80, line_dash="dot", line_color="#EF4444", annotation_text="80% mark",
                     annotation_position="right")
    pareto.update_layout(
        template=TEMPLATE,
        title=f"Pareto chart — just {n80} categories drive 80% of revenue",
        yaxis2=dict(overlaying="y", side="right", range=[0, 108], title="Cumulative %"),
        legend=dict(orientation="h", y=-0.35), xaxis_tickangle=-40,
        hoverlabel=dict(bgcolor="white"),
    )
    st.plotly_chart(pareto, use_container_width=True)
    st.caption(f"📌 The classic Pareto principle holds here: just **{n80} of {len(cat)} categories** "
               f"generate **80%** of total revenue. Focus on these for maximum impact.")

    a, b = st.columns(2)
    # Sunburst
    fig_sun = px.sunburst(
        filtered, path=["Outlet Type", "Item Type"], values="Sales",
        color_discrete_sequence=PALETTE,
        title="🌞 Revenue drill-down: Outlet → Category",
        hover_data={"Sales": ":,.0f"},
    )
    a.plotly_chart(fig_sun, use_container_width=True)
    a.caption("👆 Click any segment to zoom in. Click the centre circle to zoom back out.")

    # Bubble: avg sales vs avg rating
    fig_bub = px.scatter(
        cat, x="Average_Sales", y="Average_Rating",
        size="Total_Sales", color="Item Type", size_max=55,
        title="💬 Revenue vs Rating bubble chart",
        template=TEMPLATE,
        labels={"Average_Sales": "Avg Revenue / Record (₹)", "Average_Rating": "Avg Rating",
                "Total_Sales": "Total Revenue"},
        hover_data={"Total_Sales": ":,.0f", "Records": True},
    )
    b.plotly_chart(fig_bub, use_container_width=True)
    b.caption("👆 Big bubbles = high total revenue. Top-right corner = high revenue **and** high rating — the sweet spot.")

    # Heatmap
    st.markdown('<div class="sec-header">🗺️ Which outlet type sells which category best?</div>',
                unsafe_allow_html=True)
    pivot = filtered.pivot_table(
        index="Item Type", columns="Outlet Type", values="Sales", aggfunc="sum", fill_value=0
    )
    fig_heat = px.imshow(
        pivot, aspect="auto", color_continuous_scale=SEQ,
        title="Category × Outlet type revenue heatmap",
        labels=dict(x="Outlet Type", y="Category", color="Revenue (₹)"),
        text_auto=False,
    ).update_traces(hovertemplate="<b>%{y}</b> @ <b>%{x}</b><br>Revenue: ₹%{z:,.0f}<extra></extra>")
    st.plotly_chart(fig_heat, use_container_width=True)
    st.caption("🔥 Darker cells = higher revenue. Hover for exact values.")

    with st.expander("📋 Full category summary table", expanded=False):
        st.dataframe(
            cat.rename(columns={
                "Total_Sales": "Total Revenue (₹)", "Average_Sales": "Avg Revenue",
                "Average_Rating": "Avg Rating", "Records": "# Products",
                "Cumulative_%": "Cumulative %",
            }).round(2),
            use_container_width=True, hide_index=True,
        )


# ══════════════════════════════════════════════
#  TAB 3 — OUTLETS
# ══════════════════════════════════════════════
with tab_out:
    outlet = filtered.groupby(
        ["Outlet Identifier", "Outlet Type", "Outlet Location Type",
         "Outlet Size", "Outlet Establishment Year"], as_index=False,
    ).agg(Total_Sales=("Sales", "sum"), Average_Sales=("Sales", "mean"),
          Average_Rating=("Rating", "mean"), Records=("Sales", "size"))

    o1, o2, o3 = st.columns(3)
    best_out  = outlet.loc[outlet["Total_Sales"].idxmax()]
    worst_out = outlet.loc[outlet["Total_Sales"].idxmin()]
    gap       = best_out["Total_Sales"] / worst_out["Total_Sales"]
    o1.metric("🏆 Best outlet",   best_out["Outlet Identifier"], f"₹ {fmt(best_out['Total_Sales'])}")
    o2.metric("📉 Weakest outlet", worst_out["Outlet Identifier"], f"₹ {fmt(worst_out['Total_Sales'])}")
    o3.metric("📏 Revenue gap", f"{gap:.1f}×", "best vs worst outlet",
              help="How many times larger is the best outlet's revenue vs the weakest?")

    # Bar
    st.markdown('<div class="sec-header">🏬 Revenue by outlet</div>', unsafe_allow_html=True)
    fig_out_bar = px.bar(
        outlet.sort_values("Total_Sales", ascending=False),
        x="Outlet Identifier", y="Total_Sales", color="Outlet Type",
        color_discrete_sequence=PALETTE,
        title="Total revenue per outlet (click bars to highlight)",
        template=TEMPLATE,
        labels={"Total_Sales": "Revenue (₹)", "Outlet Identifier": "Outlet"},
        hover_data={"Outlet Location Type": True, "Outlet Size": True,
                    "Average_Rating": ":.2f", "Records": True},
    ).update_traces(hovertemplate=(
        "<b>%{x}</b><br>Revenue: ₹%{y:,.0f}<br>"
        "Type: %{customdata[0]}<br>Size: %{customdata[1]}<extra></extra>"
    ))
    st.plotly_chart(fig_out_bar, use_container_width=True)

    a, b = st.columns(2)
    # Violin
    fig_violin = px.violin(
        filtered, x="Outlet Type", y="Sales", color="Outlet Type",
        box=True, points="outliers",
        color_discrete_sequence=PALETTE,
        title="📦 Revenue spread by outlet type",
        template=TEMPLATE,
        labels={"Sales": "Revenue per record (₹)", "Outlet Type": ""},
    )
    a.plotly_chart(fig_violin, use_container_width=True)
    a.caption("👆 The wider the violin, the more records cluster at that revenue level. "
              "Box shows median and IQR; dots are outliers.")

    # Location + Size grouped bar
    size_loc = filtered.groupby(["Outlet Location Type", "Outlet Size"], as_index=False)["Sales"].sum()
    fig_sz = px.bar(
        size_loc, x="Outlet Location Type", y="Sales", color="Outlet Size",
        barmode="group", color_discrete_sequence=PALETTE,
        title="📍 Revenue by location tier & outlet size",
        template=TEMPLATE,
        labels={"Sales": "Revenue (₹)", "Outlet Location Type": "Location Tier"},
    )
    b.plotly_chart(fig_sz, use_container_width=True)
    b.caption("👆 Compare how outlet size performance varies across Tier 1/2/3 cities.")

    # Scatter: age vs revenue
    st.markdown('<div class="sec-header">⏳ Does outlet age affect revenue?</div>', unsafe_allow_html=True)
    fig_age = px.scatter(
        outlet, x="Outlet Establishment Year", y="Total_Sales",
        size="Records", color="Outlet Size", hover_name="Outlet Identifier",
        color_discrete_sequence=PALETTE, trendline="ols",
        title="Outlet establishment year vs total revenue (bubble = # products sold)",
        template=TEMPLATE,
        labels={"Total_Sales": "Total Revenue (₹)",
                "Outlet Establishment Year": "Year Established",
                "Records": "Products"},
    )
    st.plotly_chart(fig_age, use_container_width=True)
    corr_age = outlet["Outlet Establishment Year"].corr(outlet["Total_Sales"])
    direction = "newer outlets tend to generate more revenue" if corr_age > 0.1 \
                else "older outlets tend to generate more revenue" if corr_age < -0.1 \
                else "outlet age has little direct influence on revenue"
    st.caption(f"📌 Correlation between year & revenue: **{corr_age:.2f}** — suggesting {direction}.")

    with st.expander("📋 Full outlet summary table", expanded=False):
        st.dataframe(
            outlet.sort_values("Total_Sales", ascending=False).round(2),
            use_container_width=True, hide_index=True,
        )


# ══════════════════════════════════════════════
#  TAB 4 — RATINGS & VISIBILITY
# ══════════════════════════════════════════════
with tab_rate:
    st.markdown('<div class="sec-header">⭐ How customers are rating products</div>',
                unsafe_allow_html=True)
    a, b = st.columns(2)

    fig_hist = px.histogram(
        filtered, x="Rating", nbins=25, color_discrete_sequence=[PALETTE[2]],
        title="Customer rating distribution",
        template=TEMPLATE, marginal="box",
        labels={"Rating": "Customer Rating", "count": "# Products"},
    ).update_traces(hovertemplate="Rating ~%{x:.1f} ★<br>Count: %{y}<extra></extra>")
    a.plotly_chart(fig_hist, use_container_width=True)
    mode_rat = filtered["Rating"].round(1).mode().iloc[0]
    a.caption(f"👆 Most products are rated around **{mode_rat} ★**. "
              "The box in the margin shows median and spread.")

    rating_cat = filtered.groupby("Item Type", as_index=False)["Rating"].mean().sort_values("Rating")
    fig_rcat = px.bar(
        rating_cat, x="Rating", y="Item Type", orientation="h",
        color="Rating", color_continuous_scale="Sunsetdark",
        title="Average rating by product category",
        template=TEMPLATE,
        labels={"Rating": "Avg Rating ★", "Item Type": ""},
    ).update_traces(hovertemplate="<b>%{y}</b><br>Avg rating: %{x:.2f} ★<extra></extra>")
    b.plotly_chart(fig_rcat, use_container_width=True)
    top_rated = rating_cat.iloc[-1]
    low_rated = rating_cat.iloc[0]
    b.caption(f"👆 **{top_rated['Item Type']}** is the top-rated category ({top_rated['Rating']:.2f} ★), "
              f"while **{low_rated['Item Type']}** scores lowest ({low_rated['Rating']:.2f} ★).")

    # Visibility
    st.markdown('<div class="sec-header">👁️ Does visibility drive sales?</div>', unsafe_allow_html=True)
    band = filtered.groupby("Visibility Band", observed=True, as_index=False).agg(
        Average_Sales=("Sales", "mean"), Records=("Sales", "size")
    )
    c, d = st.columns(2)
    fig_band = px.bar(
        band, x="Visibility Band", y="Average_Sales",
        text_auto=".1f", color_discrete_sequence=[PALETTE[1]],
        title="Average revenue by shelf visibility quartile",
        template=TEMPLATE,
        labels={"Average_Sales": "Avg Revenue (₹)", "Visibility Band": "Visibility Tier"},
    ).update_traces(hovertemplate="<b>%{x}</b><br>Avg revenue: ₹%{y:,.2f}<extra></extra>")
    c.plotly_chart(fig_band, use_container_width=True)
    c.caption("👆 Surprisingly, **higher shelf visibility doesn't always mean higher sales** — "
              "many staple items sell well regardless of placement.")

    fig_vis = px.scatter(
        filtered, x="Item Visibility", y="Sales", color="Rating",
        opacity=0.45, color_continuous_scale="Viridis",
        title="Visibility vs revenue, coloured by rating",
        trendline="ols", trendline_color_override="red",
        template=TEMPLATE,
        labels={"Sales": "Revenue (₹)", "Item Visibility": "Item Visibility Score"},
    ).update_traces(hovertemplate="Visibility: %{x:.3f}<br>Revenue: ₹%{y:,.0f}<extra></extra>")
    d.plotly_chart(fig_vis, use_container_width=True)
    corr_vis = filtered["Item Visibility"].corr(filtered["Sales"])
    d.caption(f"📌 Trend line: correlation = **{corr_vis:.3f}** — "
              f"{'virtually no' if abs(corr_vis) < 0.05 else 'a weak'} linear relationship.")

    # Correlation matrix
    st.markdown('<div class="sec-header">🔗 How do variables relate to each other?</div>',
                unsafe_allow_html=True)
    corr_cols = ["Sales", "Rating", "Item Visibility", "Item Weight", "Outlet Age"]
    corr = filtered[corr_cols].corr().round(3)
    fig_corr = px.imshow(
        corr, text_auto=True, zmin=-1, zmax=1,
        color_continuous_scale="RdBu_r",
        title="Correlation matrix (blue = positive, red = negative)",
    ).update_traces(hovertemplate="<b>%{x}</b> × <b>%{y}</b><br>r = %{z}<extra></extra>")
    st.plotly_chart(fig_corr, use_container_width=True)
    st.caption("🔬 Values close to **+1** mean strong positive correlation; close to **−1** means inverse. "
               "Near **0** means little to no linear relationship. "
               "Correlation ≠ causation — always investigate further.")


# ══════════════════════════════════════════════
#  TAB 5 — STATISTICS
# ══════════════════════════════════════════════
with tab_stat:
    s = filtered["Sales"]
    q1, q3 = s.quantile([.25, .75])
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    outliers = filtered[(s < low) | (s > high)]

    st.markdown('<div class="sec-header">📐 Descriptive statistics for Sales</div>', unsafe_allow_html=True)

    stats = pd.DataFrame({
        "Statistic":   ["Count", "Mean", "Median", "Std Deviation", "Variance",
                        "Skewness", "Kurtosis", "Minimum",
                        "25th percentile (Q1)", "75th percentile (Q3)",
                        "95th percentile", "Maximum"],
        "Value":       [s.count(), s.mean(), s.median(), s.std(), s.var(),
                        s.skew(), s.kurt(), s.min(),
                        s.quantile(.25), s.quantile(.75), s.quantile(.95), s.max()],
        "Plain English": [
            f"{s.count():,} products in the filtered view",
            f"On average each record brings in ₹ {s.mean():,.2f}",
            f"Half of records earn less than ₹ {s.median():,.2f}",
            f"Revenue varies by ±₹ {s.std():,.2f} around the mean",
            "Spread of values (std² — useful for calculations)",
            f"{'Right-skewed (a few big earners pull the mean up)' if s.skew() > 0.5 else 'Roughly symmetric distribution'}",
            "Measures how heavy-tailed the distribution is",
            f"The single lowest revenue record: ₹ {s.min():,.2f}",
            f"75% of records earn less than ₹ {q1:,.2f}",
            f"75% of records earn less than ₹ {q3:,.2f}",
            f"Only 5% of records exceed ₹ {s.quantile(.95):,.2f}",
            f"The single highest revenue record: ₹ {s.max():,.2f}",
        ],
    })
    st.dataframe(stats.round(3), use_container_width=True, hide_index=True)

    st.info(
        f"🔍 **Outlier detection (IQR method):** Records below **₹ {low:,.2f}** or above "
        f"**₹ {high:,.2f}** are considered outliers → **{len(outliers):,} records** "
        f"({len(outliers) / len(filtered) * 100:.2f}% of filtered data)."
    )

    a, b = st.columns(2)
    fig_dist = px.histogram(
        filtered, x="Sales", nbins=45, marginal="box",
        color_discrete_sequence=[PALETTE[0]],
        title="Revenue distribution",
        template=TEMPLATE,
        labels={"Sales": "Revenue per record (₹)", "count": "# Records"},
    ).update_traces(hovertemplate="₹%{x:,.0f}<br>Count: %{y}<extra></extra>")
    a.plotly_chart(fig_dist, use_container_width=True)
    a.caption(f"👆 The distribution is **{'right-skewed' if s.skew() > 0.5 else 'roughly symmetric'}** "
              f"(skewness = {s.skew():.2f}). Most records cluster near ₹ {s.median():,.0f}.")

    ecdf = px.ecdf(
        filtered, x="Sales", color_discrete_sequence=[PALETTE[3]],
        title="Cumulative revenue distribution (ECDF)",
        template=TEMPLATE,
        labels={"Sales": "Revenue (₹)"},
    ).update_traces(hovertemplate="Revenue ≤ ₹%{x:,.0f}<br>Proportion: %{y:.1%}<extra></extra>")
    b.plotly_chart(ecdf, use_container_width=True)
    b.caption("👆 Read as: 'X% of records earn *at most* ₹Y.' "
              f"50% of records earn ≤ ₹ {s.median():,.0f}.")

    with st.expander(f"⚠️ Show {len(outliers):,} flagged outlier records", expanded=False):
        if outliers.empty:
            st.success("No outliers detected with the current IQR thresholds.")
        else:
            st.dataframe(outliers.sort_values("Sales", ascending=False),
                         use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════
#  TAB 6 — COMPARE OUTLETS
# ══════════════════════════════════════════════
with tab_compare:
    st.markdown('<div class="sec-header">🔀 Head-to-head outlet comparison</div>',
                unsafe_allow_html=True)
    st.caption("Pick any two outlets to see a side-by-side breakdown of revenue, rating, and top categories.")

    all_outlets = sorted(filtered["Outlet Identifier"].unique())
    default_a   = all_outlets[0] if len(all_outlets) > 0 else None
    default_b   = all_outlets[1] if len(all_outlets) > 1 else None

    col_a, col_b = st.columns(2)
    outlet_a = col_a.selectbox("🅰️ Outlet A", all_outlets, index=0)
    outlet_b = col_b.selectbox("🅱️ Outlet B", all_outlets,
                                index=min(1, len(all_outlets) - 1))

    if outlet_a == outlet_b:
        st.warning("Please select two *different* outlets to compare.")
    else:
        df_a = filtered[filtered["Outlet Identifier"] == outlet_a]
        df_b = filtered[filtered["Outlet Identifier"] == outlet_b]

        # Summary metrics
        def outlet_kpis(df, name):
            return {
                "Outlet": name,
                "Total Revenue": df["Sales"].sum(),
                "Avg Revenue":   df["Sales"].mean(),
                "Avg Rating":    df["Rating"].mean(),
                "Products":      len(df),
                "Type":          df["Outlet Type"].iloc[0],
                "Location":      df["Outlet Location Type"].iloc[0],
                "Size":          df["Outlet Size"].iloc[0],
            }

        kpi_a = outlet_kpis(df_a, outlet_a)
        kpi_b = outlet_kpis(df_b, outlet_b)

        def cmp_delta(val_a, val_b, fmt_fn=lambda x: f"{x:,.2f}"):
            diff = val_a - val_b
            arrow = "🟢" if diff > 0 else "🔴" if diff < 0 else "⚪"
            return f"{arrow} {fmt_fn(abs(diff))}"

        ca, cb, cc = st.columns(3)
        ca.markdown(f"""<div class="compare-box">
            <b>💰 Total Revenue</b><br>
            🅰️ {kpi_a['Outlet']}: <b>₹ {fmt(kpi_a['Total Revenue'])}</b><br>
            🅱️ {kpi_b['Outlet']}: <b>₹ {fmt(kpi_b['Total Revenue'])}</b><br>
            Gap: {cmp_delta(kpi_a['Total Revenue'], kpi_b['Total Revenue'], fmt)}
        </div>""", unsafe_allow_html=True)

        cb.markdown(f"""<div class="compare-box">
            <b>⭐ Avg Rating</b><br>
            🅰️ {kpi_a['Outlet']}: <b>{kpi_a['Avg Rating']:.2f} ★</b><br>
            🅱️ {kpi_b['Outlet']}: <b>{kpi_b['Avg Rating']:.2f} ★</b><br>
            Gap: {cmp_delta(kpi_a['Avg Rating'], kpi_b['Avg Rating'], lambda x: f'{x:.2f}')}
        </div>""", unsafe_allow_html=True)

        cc.markdown(f"""<div class="compare-box">
            <b>📦 Avg Revenue / Record</b><br>
            🅰️ {kpi_a['Outlet']}: <b>₹ {kpi_a['Avg Revenue']:,.2f}</b><br>
            🅱️ {kpi_b['Outlet']}: <b>₹ {kpi_b['Avg Revenue']:,.2f}</b><br>
            Gap: {cmp_delta(kpi_a['Avg Revenue'], kpi_b['Avg Revenue'])}
        </div>""", unsafe_allow_html=True)

        # Category breakdown comparison
        st.markdown("#### 🧺 Revenue by category — side by side")
        cat_a = df_a.groupby("Item Type")["Sales"].sum().reset_index().rename(columns={"Sales": outlet_a})
        cat_b = df_b.groupby("Item Type")["Sales"].sum().reset_index().rename(columns={"Sales": outlet_b})
        cat_cmp = pd.merge(cat_a, cat_b, on="Item Type", how="outer").fillna(0)
        cat_cmp_melt = cat_cmp.melt("Item Type", var_name="Outlet", value_name="Revenue")

        fig_cmp = px.bar(
            cat_cmp_melt, x="Item Type", y="Revenue", color="Outlet",
            barmode="group", color_discrete_sequence=[PALETTE[0], PALETTE[1]],
            title=f"Category revenue: {outlet_a} vs {outlet_b}",
            template=TEMPLATE,
            labels={"Revenue": "Revenue (₹)", "Item Type": ""},
        ).update_layout(xaxis_tickangle=-35)
        st.plotly_chart(fig_cmp, use_container_width=True)

        # Radar chart
        st.markdown("#### 🕸️ Multi-metric radar comparison")
        metrics = ["Total Revenue", "Avg Revenue", "Avg Rating", "Products"]
        scale_a = [kpi_a[m] for m in metrics]
        scale_b = [kpi_b[m] for m in metrics]
        # Normalise 0-1 per metric
        maxvals = [max(scale_a[i], scale_b[i]) or 1 for i in range(len(metrics))]
        norm_a  = [scale_a[i] / maxvals[i] for i in range(len(metrics))]
        norm_b  = [scale_b[i] / maxvals[i] for i in range(len(metrics))]
        labels  = ["Total Revenue", "Avg Revenue", "Avg Rating", "# Products"]

        radar = go.Figure()
        radar.add_trace(go.Scatterpolar(
            r=norm_a + [norm_a[0]], theta=labels + [labels[0]],
            fill="toself", name=outlet_a, line_color=PALETTE[0], fillcolor="rgba(15,118,110,.2)",
        ))
        radar.add_trace(go.Scatterpolar(
            r=norm_b + [norm_b[0]], theta=labels + [labels[0]],
            fill="toself", name=outlet_b, line_color=PALETTE[1], fillcolor="rgba(245,158,11,.2)",
        ))
        radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            template=TEMPLATE, showlegend=True,
            title=f"Normalised multi-metric radar: {outlet_a} vs {outlet_b}",
        )
        st.plotly_chart(radar, use_container_width=True)
        st.caption("👆 All metrics are normalised to [0, 1] so they're comparable on the same scale. "
                   "The outlet covering more area performs better overall.")

        # Fat content comparison
        st.markdown("#### 🥗 Fat content revenue mix")
        fat_a = df_a.groupby("Item Fat Content")["Sales"].sum().reset_index().rename(columns={"Sales": outlet_a})
        fat_b = df_b.groupby("Item Fat Content")["Sales"].sum().reset_index().rename(columns={"Sales": outlet_b})
        fat_cmp = pd.merge(fat_a, fat_b, on="Item Fat Content", how="outer").fillna(0)
        fat_melt = fat_cmp.melt("Item Fat Content", var_name="Outlet", value_name="Revenue")
        fig_fat_cmp = px.bar(
            fat_melt, x="Item Fat Content", y="Revenue", color="Outlet",
            barmode="group", color_discrete_sequence=[PALETTE[0], PALETTE[1]],
            template=TEMPLATE, title="Low Fat vs Regular revenue by outlet",
            labels={"Revenue": "Revenue (₹)", "Item Fat Content": ""},
        )
        st.plotly_chart(fig_fat_cmp, use_container_width=True)


# ══════════════════════════════════════════════
#  TAB 7 — STORY & INSIGHTS
# ══════════════════════════════════════════════
with tab_story:
    st.markdown('<div class="sec-header">📖 The story your data is telling</div>',
                unsafe_allow_html=True)
    st.caption("Auto-generated plain-English insights based on your current filter selection.")

    # Compute everything
    out_type_sales  = filtered.groupby("Outlet Type")["Sales"].sum().sort_values(ascending=False)
    fat_sales       = filtered.groupby("Item Fat Content")["Sales"].sum().sort_values(ascending=False)
    rating_by_cat   = filtered.groupby("Item Type")["Rating"].mean().sort_values(ascending=False)
    avg_by_size     = filtered.groupby("Outlet Size")["Sales"].mean().sort_values(ascending=False)
    corr_vis        = filtered["Item Visibility"].corr(filtered["Sales"])
    cat_n           = len(cat_totals)
    top1_share      = cat_totals.iloc[0] / total_sales * 100
    top_out_type_sh = out_type_sales.iloc[0] / total_sales * 100
    lf_share        = fat_sales.get("Low Fat", 0) / total_sales * 100

    story_cards = [
        ("🏆 Revenue leader",
         f"**{cat_totals.index[0]}** is the single biggest revenue driver, capturing "
         f"{human_pct(top1_share)} of your filtered sales (₹ {fmt(cat_totals.iloc[0])}). "
         f"If supply or margins here shift, it will be felt across the entire portfolio."),

        ("🏪 Outlet type dominance",
         f"**{out_type_sales.index[0]}** outlet type generates {human_pct(top_out_type_sh)} of revenue. "
         f"{'This concentration could be a risk — consider diversifying sales channels.' if top_out_type_sh > 60 else 'The revenue is reasonably spread across outlet types, which is healthy.'}"),

        ("🏅 Individual outlet standout",
         f"**{out_totals.index[0]}** is your highest-performing outlet (₹ {fmt(out_totals.iloc[0])}), "
         f"while **{out_totals.index[-1]}** (₹ {fmt(out_totals.iloc[-1])}) is the weakest. "
         f"The gap is **{out_totals.iloc[0] / out_totals.iloc[-1]:.1f}×** — "
         f"{'a significant disparity worth investigating.' if out_totals.iloc[0] / out_totals.iloc[-1] > 5 else 'a relatively balanced network.'}"),

        ("🥗 Health-conscious shoppers?",
         f"**{fat_sales.index[0]}** products capture {human_pct(lf_share)} of revenue. "
         f"{'Consumers are clearly leaning toward healthier options — a trend worth amplifying in marketing.' if fat_sales.index[0] == 'Low Fat' else 'Regular products still dominate — consider promotional nudges toward healthier alternatives.'}"),

        ("⭐ Quality perception",
         f"**{rating_by_cat.index[0]}** has the highest customer satisfaction ({rating_by_cat.iloc[0]:.2f} ★ — "
         f"{rating_label(rating_by_cat.iloc[0])}), while **{rating_by_cat.index[-1]}** "
         f"scores lowest ({rating_by_cat.iloc[-1]:.2f} ★ — {rating_label(rating_by_cat.iloc[-1])}). "
         f"Bridging this gap could unlock meaningful revenue."),

        ("🏗️ Size matters?",
         f"**{avg_by_size.index[0]}** outlets have the highest average revenue per record "
         f"(₹ {avg_by_size.iloc[0]:,.2f}). "
         f"{'Consider expanding this outlet format.' if avg_by_size.index[0] != avg_by_size.index[-1] else 'Outlet sizes perform similarly on a per-record basis.'}"),

        ("👁️ Visibility vs Sales",
         f"The correlation between item visibility and sales is **{corr_vis:.3f}** — "
         f"{'a near-zero relationship, meaning shelf placement has little bearing on revenue in this dataset. Other factors (brand, price, demand) drive purchases.' if abs(corr_vis) < 0.1 else 'a noticeable relationship — more visible products do tend to generate different revenue levels.'}"),

        ("📊 Concentration risk",
         f"Just **{n80} of {cat_n} categories** drive **80%** of revenue (Pareto principle). "
         f"This means the business is {'highly concentrated — a single category disruption could have outsized impact.' if n80 <= 3 else 'moderately diversified across product types.'}"),
    ]

    for icon_title, text in story_cards:
        st.markdown(
            f'<div class="insight-card"><span class="icon"></span>'
            f'<b>{icon_title}</b><br>{text}</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown("### 🎯 Recommended next steps")
    recs = [
        f"Double down on **{cat_totals.index[0]}** — it's your star category. Ensure consistent stock and competitive pricing.",
        f"Investigate **{out_totals.index[-1]}** — understand why it underperforms and whether a turnaround is feasible.",
        f"If not already done, run a promotion on **{rating_by_cat.index[-1]}** to lift its rating and unlock revenue potential.",
        f"Review shelf-space allocation strategy — visibility alone doesn't drive sales (r = {corr_vis:.2f}). Focus on demand signals instead.",
        f"Consider outlet size expansion in **{avg_by_size.index[0]}** format, which has the best per-record revenue.",
    ]
    for i, rec in enumerate(recs, 1):
        st.markdown(f"**{i}.** {rec}")

    st.divider()
    # Download
    report_lines = ["# 📊 GroceryLens — Sales Insight Report\n"]
    report_lines.append(f"*Filters applied: {len(filtered):,} of {len(data):,} records shown.*\n")
    report_lines.append("## Key Insights\n")
    for title, text in story_cards:
        import re
        clean = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        report_lines.append(f"### {title}\n{clean}\n")
    report_lines.append("## Recommended Next Steps\n")
    for i, rec in enumerate(recs, 1):
        import re
        clean = re.sub(r"\*\*(.+?)\*\*", r"\1", rec)
        report_lines.append(f"{i}. {clean}")

    report_md = "\n".join(report_lines)

    dl1, dl2 = st.columns(2)
    dl1.download_button(
        "📥 Download insight report (Markdown)",
        report_md, "grocerylens_report.md", "text/markdown",
        use_container_width=True,
    )
    dl2.download_button(
        "📥 Download filtered data (CSV)",
        filtered.to_csv(index=False).encode("utf-8"),
        "filtered_grocery_data.csv", "text/csv",
        use_container_width=True,
    )


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.divider()
f1, f2, f3 = st.columns([3, 1, 1])
f1.caption(f"🛒 **GroceryLens** — Showing **{len(filtered):,}** of **{len(data):,}** records "
           f"({pct_shown:.1f}% of dataset) · BlinkIT Grocery Dataset")
f2.download_button(
    "⬇️ Download filtered CSV",
    filtered.to_csv(index=False).encode("utf-8"),
    "filtered_grocery_data.csv", "text/csv",
    use_container_width=True,
)
f3.caption("Built with ❤️ using Streamlit & Plotly")
