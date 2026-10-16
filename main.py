import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------
# Sugar Cosmetics | Instagram Performance & Growth Analytics
# ------------------------------------------------------------
st.set_page_config(
    page_title="Sugar Cosmetics | Instagram Analytics",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded",
)

TEAL = "#168C88"
DARK = "#263238"
MINT = "#D9F3EF"
CORAL = "#F06464"
GOLD = "#E9B44C"
PALETTE = [TEAL, "#58C4C0", "#263238", "#E9B44C", "#F06464", "#8C79C6", "#82B366"]

st.markdown(
    """
    <style>
      .stApp { background: #F5F7F8; }
      [data-testid="stSidebar"] { background: #FFFFFF; border-right: 1px solid #E5EAED; }
      .block-container { padding-top: 1.3rem; padding-bottom: 2rem; }
      h1, h2, h3 { color: #263238; }
      div[data-testid="stMetric"] {
        background: #FFFFFF; border: 1px solid #E4EAED; padding: 15px 17px;
        border-radius: 15px; box-shadow: 0 3px 12px rgba(30,55,65,.045);
      }
      div[data-testid="stMetricLabel"] { color: #64747B; }
      div[data-testid="stMetricValue"] { color: #168C88; }
      .hero { padding: 22px 25px; border-radius: 18px; color: white;
        background: linear-gradient(110deg, #087E7A 0%, #168C88 52%, #55BDB5 100%);
        margin-bottom: 18px; }
      .hero h1 { color: white; font-size: 2rem; margin: 0 0 6px 0; }
      .hero p { color: #E8FFFC; margin: 0; font-size: .98rem; }
      .section-note { color: #64747B; font-size: .9rem; }
      .insight { background: #FFFFFF; border-left: 4px solid #168C88; padding: 12px 15px;
        border-radius: 8px; margin: 7px 0 12px 0; }
      footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

REQUIRED = [
    "Post Date", "Post Type", "Campaign Type", "Hashtags", "Audience Emotion",
    "Engagement Source", "Impressions", "Reach", "Likes", "Comments", "Shares",
    "Saves", "Profile Visits", "Follows",
]
METRICS = ["Impressions", "Reach", "Likes", "Comments", "Shares", "Saves", "Profile Visits", "Follows"]


@st.cache_data(show_spinner=False)
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        raw = pd.read_csv(uploaded_file)
    else:
        # Try common CSV filenames beside app.py; if none exists, the user can upload.
        candidates = list(Path(".").glob("*.csv"))
        if not candidates:
            return None
        preferred = [p for p in candidates if "sugar_cosmetics_instagram_data" in p.name.lower()]
        raw = pd.read_csv(preferred[0] if preferred else candidates[0])

    missing = [c for c in REQUIRED if c not in raw.columns]
    if missing:
        raise ValueError("The CSV is missing required columns: " + ", ".join(missing))

    df = raw.copy()
    df["Post Date"] = pd.to_datetime(df["Post Date"], errors="coerce")
    for col in METRICS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).clip(lower=0)
    for col in ["Post Type", "Campaign Type", "Hashtags", "Audience Emotion", "Engagement Source"]:
        df[col] = df[col].fillna("Unknown").astype(str).str.strip().replace("", "Unknown")

    df = df.dropna(subset=["Post Date"]).copy()
    # This dataset does not provide a post ID. Use a row-level identifier for exploration only.
    df["Post ID"] = [f"POST-{i:05d}" for i in range(1, len(df) + 1)]
    df["Total Engagements"] = df[["Likes", "Comments", "Shares", "Saves"]].sum(axis=1)
    df["Post Engagement Rate"] = np.where(df["Reach"] > 0, df["Total Engagements"] / df["Reach"], np.nan)
    df["Engagement Rate by Impressions"] = np.where(
        df["Impressions"] > 0, df["Total Engagements"] / df["Impressions"], np.nan
    )
    df["Profile Visit Rate"] = np.where(df["Reach"] > 0, df["Profile Visits"] / df["Reach"], np.nan)
    df["Follow Conversion Rate"] = np.where(df["Profile Visits"] > 0, df["Follows"] / df["Profile Visits"], np.nan)
    df["Share Rate"] = np.where(df["Reach"] > 0, df["Shares"] / df["Reach"], np.nan)
    df["Save Rate"] = np.where(df["Reach"] > 0, df["Saves"] / df["Reach"], np.nan)
    df["Post Month"] = df["Post Date"].dt.to_period("M").dt.to_timestamp()
    df["Month Label"] = df["Post Month"].dt.strftime("%b %Y")
    df["Weekday"] = df["Post Date"].dt.day_name()
    df["Weekday Number"] = df["Post Date"].dt.dayofweek
    df["Caption Preview"] = "Instagram post · " + df["Post Type"].astype(str)
    return df


def fmt_num(n):
    if pd.isna(n):
        return "—"
    n = float(n)
    if abs(n) >= 1_000_000_000:
        return f"{n/1_000_000_000:.2f}B"
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if abs(n) >= 1_000:
        return f"{n/1_000:.1f}K"
    return f"{n:,.0f}"


def fmt_pct(n):
    return "—" if pd.isna(n) else f"{n:.2%}"


def chart_layout(fig, height=340):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=45, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", color=DARK, size=12),
        title=dict(font=dict(size=15, color=DARK), x=0.02, xanchor="left"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(showgrid=False, linecolor="#E6ECEF")
    fig.update_yaxes(gridcolor="#E8EEF0", zeroline=False)
    return fig


def pct_axis(fig, axis="y"):
    if axis == "y":
        fig.update_yaxes(tickformat=".0%")
    else:
        fig.update_xaxes(tickformat=".0%")
    return fig


def filter_options(frame, column):
    return sorted(frame[column].dropna().astype(str).unique().tolist())


st.sidebar.markdown("## 💄 Sugar Cosmetics")
st.sidebar.caption("Instagram Performance & Growth Analytics")
uploaded = st.sidebar.file_uploader("Upload project CSV", type=["csv"])

try:
    all_data = load_data(uploaded)
except Exception as exc:
    st.error(f"Could not load the dataset: {exc}")
    st.stop()

if all_data is None:
    st.markdown(
        '<div class="hero"><h1>Sugar Cosmetics | Instagram Performance & Growth Analytics</h1>'
        '<p>Upload the project CSV in the sidebar to begin exploring content, engagement, campaigns and conversion.</p></div>',
        unsafe_allow_html=True,
    )
    st.info("Required CSV columns: Post Date, Post Type, Campaign Type, Hashtags, Audience Emotion, Engagement Source, Impressions, Reach, Likes, Comments, Shares, Saves, Profile Visits and Follows.")
    st.stop()

min_date = all_data["Post Date"].min().date()
max_date = all_data["Post Date"].max().date()
st.sidebar.markdown("---")
st.sidebar.markdown("### Dashboard filters")
date_range = st.sidebar.date_input("Post date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

def multiselect_filter(label, column):
    options = filter_options(all_data, column)
    return st.sidebar.multiselect(label, options, default=options)

selected_types = multiselect_filter("Post type", "Post Type")
selected_campaigns = multiselect_filter("Campaign type", "Campaign Type")
selected_sources = multiselect_filter("Engagement source", "Engagement Source")
selected_emotions = multiselect_filter("Audience emotion", "Audience Emotion")

filtered = all_data[
    all_data["Post Date"].dt.date.between(start_date, end_date)
    & all_data["Post Type"].isin(selected_types)
    & all_data["Campaign Type"].isin(selected_campaigns)
    & all_data["Engagement Source"].isin(selected_sources)
    & all_data["Audience Emotion"].isin(selected_emotions)
].copy()

if filtered.empty:
    st.warning("No records match the selected filters. Widen the date range or select additional categories.")
    st.stop()

total_posts = len(filtered)
total_reach = filtered["Reach"].sum()
total_impressions = filtered["Impressions"].sum()
total_engagements = filtered["Total Engagements"].sum()
weighted_engagement_rate = total_engagements / total_reach if total_reach else np.nan
weighted_impression_rate = total_engagements / total_impressions if total_impressions else np.nan
total_follows = filtered["Follows"].sum()
total_visits = filtered["Profile Visits"].sum()
visit_rate = total_visits / total_reach if total_reach else np.nan
follow_conversion = total_follows / total_visits if total_visits else np.nan

st.markdown(
    f'<div class="hero"><h1>Sugar Cosmetics | Instagram Performance & Growth Analytics</h1>'
    f'<p>Executive overview · content strategy · hashtag intelligence · conversion analysis</p></div>',
    unsafe_allow_html=True,
)
st.caption(f"Showing {total_posts:,} records from {start_date:%d %b %Y} to {end_date:%d %b %Y}. All charts respond to sidebar filters.")

# KPI cards
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Posts / Records", fmt_num(total_posts))
k2.metric("Total Reach", fmt_num(total_reach))
k3.metric("Impressions", fmt_num(total_impressions))
k4.metric("Engagement Rate", fmt_pct(weighted_engagement_rate))
k5.metric("Total Engagements", fmt_num(total_engagements))
k6.metric("Follows", fmt_num(total_follows))

tab_overview, tab_content, tab_hashtags, tab_explorer = st.tabs([
    "📊 Executive Overview", "🎯 Content & Campaigns", "#️⃣ Hashtag Intelligence", "🔎 Post Explorer"
])

with tab_overview:
    st.subheader("Performance at a glance")
    left, right = st.columns([1.55, 1])
    monthly = filtered.groupby("Post Month", as_index=False).agg(
        Posts=("Post ID", "count"),
        Reach=("Reach", "sum"),
        Engagements=("Total Engagements", "sum"),
        Impressions=("Impressions", "sum"),
        Follows=("Follows", "sum"),
    )
    monthly["Engagement Rate"] = np.where(monthly["Reach"] > 0, monthly["Engagements"] / monthly["Reach"], np.nan)
    monthly["Month"] = monthly["Post Month"].dt.strftime("%b %Y")
    with left:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly["Post Month"], y=monthly["Reach"], name="Reach",
            mode="lines+markers", line=dict(color=TEAL, width=3), fill="tozeroy",
            fillcolor="rgba(22,140,136,0.10)", yaxis="y"
        ))
        fig.add_trace(go.Scatter(
            x=monthly["Post Month"], y=monthly["Posts"], name="Posts",
            mode="lines+markers", line=dict(color=GOLD, width=2, dash="dot"), yaxis="y2"
        ))
        fig.update_layout(title="Monthly reach & posting volume", yaxis=dict(title="Reach", gridcolor="#E8EEF0"),
                          yaxis2=dict(title="Posts", overlaying="y", side="right", showgrid=False),
                          hovermode="x unified")
        st.plotly_chart(chart_layout(fig, 360), use_container_width=True)
    with right:
        by_type = filtered.groupby("Post Type", as_index=False).agg(
            Engagements=("Total Engagements", "sum"), Reach=("Reach", "sum"),
            Posts=("Post ID", "count"), Likes=("Likes", "sum")
        )
        by_type["Engagement Rate"] = np.where(by_type["Reach"] > 0, by_type["Engagements"] / by_type["Reach"], np.nan)
        fig = px.bar(by_type.sort_values("Engagement Rate"), x="Engagement Rate", y="Post Type",
                     orientation="h", color="Post Type", color_discrete_sequence=PALETTE,
                     title="Weighted engagement rate by post type", text=by_type.sort_values("Engagement Rate")["Engagement Rate"].map(fmt_pct))
        fig.update_traces(textposition="outside", cliponaxis=False)
        pct_axis(fig)
        st.plotly_chart(chart_layout(fig, 360), use_container_width=True)

    l2, r2 = st.columns(2)
    with l2:
        engagement_mix = pd.DataFrame({
            "Interaction": ["Likes", "Comments", "Shares", "Saves"],
            "Count": [filtered["Likes"].sum(), filtered["Comments"].sum(), filtered["Shares"].sum(), filtered["Saves"].sum()]
        })
        fig = px.pie(engagement_mix, names="Interaction", values="Count", hole=0.62,
                     color_discrete_sequence=[TEAL, "#58C4C0", GOLD, "#8C79C6"],
                     title="Engagement mix")
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(chart_layout(fig, 330), use_container_width=True)
    with r2:
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday = filtered.groupby(["Weekday", "Weekday Number"], as_index=False).agg(
            Posts=("Post ID", "count"), Engagements=("Total Engagements", "sum"), Reach=("Reach", "sum")
        )
        weekday["Avg Engagements"] = weekday["Engagements"] / weekday["Posts"]
        weekday = weekday.sort_values("Weekday Number")
        fig = px.bar(weekday, x="Weekday", y="Avg Engagements", color="Avg Engagements",
                     color_continuous_scale=["#D9F3EF", TEAL], title="Average engagements by weekday",
                     category_orders={"Weekday": weekday_order})
        st.plotly_chart(chart_layout(fig, 330), use_container_width=True)

    st.subheader("Audience journey (aggregate proxy)")
    funnel = pd.DataFrame({
        "Stage": ["Impressions", "Reach", "Engagements", "Profile Visits", "Follows"],
        "Count": [total_impressions, total_reach, total_engagements, total_visits, total_follows],
    })
    funnel_fig = px.funnel(funnel, x="Count", y="Stage", color="Stage", color_discrete_sequence=PALETTE,
                           title="From exposure to follow")
    funnel_fig.update_traces(texttemplate="%{x:,.0f}")
    st.plotly_chart(chart_layout(funnel_fig, 340), use_container_width=True)
    st.caption("This is a sequence of aggregate metrics, not a user-level conversion funnel. The source data does not link individual users between stages.")

with tab_content:
    st.subheader("Which content and campaigns perform best?")
    a, b = st.columns(2)
    type_stats = filtered.groupby("Post Type", as_index=False).agg(
        Posts=("Post ID", "count"), Avg_Likes=("Likes", "mean"), Avg_Comments=("Comments", "mean"),
        Avg_Shares=("Shares", "mean"), Avg_Saves=("Saves", "mean"), Reach=("Reach", "sum"),
        Engagements=("Total Engagements", "sum")
    )
    type_stats["Engagement Rate"] = np.where(type_stats["Reach"] > 0, type_stats["Engagements"] / type_stats["Reach"], np.nan)
    with a:
        melted = type_stats.melt(id_vars="Post Type", value_vars=["Avg_Likes", "Avg_Comments", "Avg_Shares", "Avg_Saves"],
                                 var_name="Metric", value_name="Average per post")
        melted["Metric"] = melted["Metric"].str.replace("Avg_", "", regex=False)
        fig = px.bar(melted, x="Post Type", y="Average per post", color="Metric", barmode="group",
                     color_discrete_sequence=[TEAL, "#58C4C0", GOLD, "#8C79C6"],
                     title="Average interactions by content format")
        st.plotly_chart(chart_layout(fig, 380), use_container_width=True)
    with b:
        camp = filtered.groupby("Campaign Type", as_index=False).agg(
            Posts=("Post ID", "count"), Reach=("Reach", "sum"), Engagements=("Total Engagements", "sum"),
            Follows=("Follows", "sum"), Profile_Visits=("Profile Visits", "sum")
        )
        camp["Engagement Rate"] = np.where(camp["Reach"] > 0, camp["Engagements"] / camp["Reach"], np.nan)
        fig = px.bar(camp.sort_values("Engagement Rate"), x="Engagement Rate", y="Campaign Type", orientation="h",
                     color="Engagement Rate", color_continuous_scale=["#D9F3EF", TEAL],
                     title="Campaign performance by weighted engagement rate", hover_data=["Posts", "Follows"])
        pct_axis(fig)
        st.plotly_chart(chart_layout(fig, 380), use_container_width=True)

    c, d = st.columns(2)
    with c:
        source = filtered.groupby("Engagement Source", as_index=False).agg(
            Posts=("Post ID", "count"), Reach=("Reach", "sum"), Engagements=("Total Engagements", "sum")
        )
        source["Engagement Rate"] = np.where(source["Reach"] > 0, source["Engagements"] / source["Reach"], np.nan)
        fig = px.bar(source.sort_values("Engagement Rate"), x="Engagement Source", y="Engagement Rate",
                     color="Engagement Rate", color_continuous_scale=["#D9F3EF", TEAL],
                     title="Engagement source comparison", hover_data=["Posts"])
        pct_axis(fig)
        st.plotly_chart(chart_layout(fig, 350), use_container_width=True)
    with d:
        emotion = filtered.groupby("Audience Emotion", as_index=False).agg(
            Posts=("Post ID", "count"), Reach=("Reach", "sum"), Engagements=("Total Engagements", "sum")
        )
        emotion["Engagement Rate"] = np.where(emotion["Reach"] > 0, emotion["Engagements"] / emotion["Reach"], np.nan)
        fig = px.bar(emotion.sort_values("Engagement Rate"), x="Engagement Rate", y="Audience Emotion",
                     orientation="h", color="Engagement Rate", color_continuous_scale=["#D9F3EF", TEAL],
                     title="Engagement by audience emotion", hover_data=["Posts"])
        pct_axis(fig)
        st.plotly_chart(chart_layout(fig, 350), use_container_width=True)

    st.subheader("Reach vs. engagement")
    scatter = filtered.copy()
    fig = px.scatter(scatter, x="Reach", y="Post Engagement Rate", color="Post Type",
                     size="Total Engagements", hover_data=["Post ID", "Post Date", "Campaign Type", "Likes", "Comments", "Shares", "Saves"],
                     color_discrete_sequence=PALETTE, opacity=0.65,
                     title="Post-level reach versus engagement rate")
    pct_axis(fig)
    st.plotly_chart(chart_layout(fig, 430), use_container_width=True)
    st.caption("Each point is a CSV row because the source has no unique post identifier or caption. The generated POST IDs are row identifiers for this dashboard only.")

with tab_hashtags:
    st.subheader("Hashtag intelligence")
    st.caption("Hashtags are split into individual tags for this tab only. Engagement and reach are averaged per source row to avoid inflating the main dashboard totals.")
    hashtag_rows = filtered[["Post ID", "Hashtags", "Reach", "Total Engagements", "Likes", "Comments", "Shares", "Saves"]].copy()
    hashtag_rows["Hashtag"] = hashtag_rows["Hashtags"].str.split(",")
    hashtag_rows = hashtag_rows.explode("Hashtag")
    hashtag_rows["Hashtag"] = hashtag_rows["Hashtag"].astype(str).str.strip().str.lower()
    hashtag_rows = hashtag_rows[hashtag_rows["Hashtag"].str.startswith("#")]
    if hashtag_rows.empty:
        st.info("No valid hashtags found in the current filter selection.")
    else:
        hashtag_stats = hashtag_rows.groupby("Hashtag", as_index=False).agg(
            Posts=("Post ID", "nunique"), Avg_Reach=("Reach", "mean"),
            Avg_Engagements=("Total Engagements", "mean"), Reach=("Reach", "sum"),
            Engagements=("Total Engagements", "sum")
        )
        hashtag_stats["Engagement Rate"] = np.where(
            hashtag_stats["Reach"] > 0, hashtag_stats["Engagements"] / hashtag_stats["Reach"], np.nan
        )
        min_posts = st.slider("Minimum source records per hashtag", min_value=1,
                              max_value=max(1, int(hashtag_stats["Posts"].max())), value=1)
        eligible = hashtag_stats[hashtag_stats["Posts"] >= min_posts]
        h1, h2 = st.columns(2)
        with h1:
            top_used = eligible.sort_values("Posts", ascending=False).head(15).sort_values("Posts")
            fig = px.bar(top_used, x="Posts", y="Hashtag", orientation="h", color="Posts",
                         color_continuous_scale=["#D9F3EF", TEAL], title="Most-used hashtags (top 15)")
            st.plotly_chart(chart_layout(fig, 420), use_container_width=True)
        with h2:
            top_rate = eligible.sort_values("Engagement Rate", ascending=False).head(15).sort_values("Engagement Rate")
            fig = px.bar(top_rate, x="Engagement Rate", y="Hashtag", orientation="h", color="Engagement Rate",
                         color_continuous_scale=["#D9F3EF", TEAL], title="Highest engagement-rate hashtags (top 15)",
                         hover_data=["Posts", "Avg_Reach", "Avg_Engagements"])
            pct_axis(fig)
            st.plotly_chart(chart_layout(fig, 420), use_container_width=True)
        st.dataframe(
            eligible.sort_values("Engagement Rate", ascending=False)
            .rename(columns={"Posts": "Source records", "Avg_Reach": "Avg reach / record",
                             "Avg_Engagements": "Avg engagements / record", "Engagement Rate": "Weighted engagement rate"})
            [["Hashtag", "Source records", "Avg reach / record", "Avg engagements / record", "Weighted engagement rate"]],
            use_container_width=True, hide_index=True,
            column_config={"Weighted engagement rate": st.column_config.NumberColumn(format="%.2%%"),
                           "Avg reach / record": st.column_config.NumberColumn(format="%,.0f"),
                           "Avg engagements / record": st.column_config.NumberColumn(format="%,.1f")}
        )

with tab_explorer:
    st.subheader("Post-level data explorer")
    search = st.text_input("Search generated Post ID or hashtag", placeholder="e.g. POST-00010 or #makeupgoals")
    explore = filtered.copy()
    if search.strip():
        mask = (
            explore["Post ID"].str.contains(search.strip(), case=False, na=False)
            | explore["Hashtags"].str.contains(search.strip(), case=False, na=False)
        )
        explore = explore[mask]
    sort_label = st.selectbox("Sort records by", ["Reach", "Total Engagements", "Likes", "Comments", "Shares", "Saves", "Follows", "Post Engagement Rate"])
    descending = st.checkbox("Highest first", value=True)
    explore = explore.sort_values(sort_label, ascending=not descending)
    display_cols = ["Post ID", "Post Date", "Post Type", "Campaign Type", "Engagement Source",
                    "Audience Emotion", "Hashtags", "Impressions", "Reach", "Likes", "Comments",
                    "Shares", "Saves", "Total Engagements", "Post Engagement Rate", "Profile Visits", "Follows"]
    st.dataframe(
        explore[display_cols],
        use_container_width=True, hide_index=True,
        column_config={
            "Post Date": st.column_config.DateColumn(format="DD MMM YYYY"),
            "Post Engagement Rate": st.column_config.NumberColumn(format="%.2%%"),
            "Reach": st.column_config.NumberColumn(format="%,d"),
            "Impressions": st.column_config.NumberColumn(format="%,d"),
            "Total Engagements": st.column_config.NumberColumn(format="%,d"),
        }
    )
    csv_bytes = explore[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered records (CSV)", data=csv_bytes,
                       file_name="sugar_cosmetics_filtered_instagram_data.csv", mime="text/csv")

st.markdown("---")
with st.expander("📌 Metric definitions & data caveats"):
    st.markdown(
        """
        - **Total engagements** = likes + comments + shares + saves.
        - **Engagement rate by reach** = total engagements ÷ total reach. This is a weighted aggregate rate.
        - **Engagement rate by impressions** = total engagements ÷ total impressions.
        - **Profile visit rate** = profile visits ÷ reach.
        - **Follow conversion rate** = follows ÷ profile visits; this is an aggregate proxy, not verified user-level attribution.
        - **Post ID** is generated from row order because the provided CSV does not include a unique post identifier or caption. It is not an actual Instagram ID.
        - **Data grain must be validated** before interpreting each record as a unique published post. If rows are synthetic or represent repeated observations, the dashboard labels should be updated accordingly.
        - The CSV does not include follower counts over time, spend, revenue, or individual user journeys. Do not claim follower growth, ROI, or causal campaign lift from this dataset alone.
        """
    )
st.caption("Sugar Cosmetics Instagram analytics · Built with Streamlit and Plotly")
