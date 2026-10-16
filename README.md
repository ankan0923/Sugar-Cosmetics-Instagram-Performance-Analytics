# 💄 Sugar Cosmetics | Instagram Performance & Growth Analytics

An end-to-end analytics project on Sugar Cosmetics Instagram data, delivered as two complementary dashboards:

- **Tableau dashboard** – executive-facing visual storytelling
- **Streamlit app** – interactive exploration with filters, hashtag analysis and CSV export

The analysis covers reach, impressions, engagement, content formats, campaigns, audience emotion, engagement source, hashtags and the profile-visit → follow path.

---

## 📌 Highlights

| KPI | Value |
|---|---|
| Source records | 50,000 |
| Date range | 19 Apr 2024 – 19 Apr 2025 |
| Total reach | 987.42M |
| Total impressions | 1.28B |
| Total engagements (likes + comments + shares + saves) | 183.16M |
| Engagement rate by reach | 18.55% |
| Engagement rate by impressions | 14.35% |
| Profile visit rate (visits ÷ reach) | 3.00% |
| Follow conversion proxy (follows ÷ profile visits) | 29.92% |
| Total follows | 8.87M |

**Key findings** (descriptive, not causal):

- Engagement rates are very close across segments. By format, Story is highest (18.63%) and Image lowest (18.42%).
- Influencer Collab is the top campaign type by weighted engagement rate (18.63%).
- Wednesday has the highest average engagements per record (3,687) and Saturday the lowest (3,626).
- Differences between segments are small, so they are best treated as hypotheses for controlled experiments rather than proof of what works.

---

## 🗂️ Repository Contents

```
.
├── main.py                                                   # Streamlit app
├── Social_media_Sugar_cosmetic_Dashboard_Analysis.twb        # Tableau workbook
├── sugar_cosmetics_instagram_data.csv                        # Dataset (50,000 rows × 14 columns)
├── Sugar_Cosmetics_Instagram_Analytics_Project_Report_and_Presentation_Script.docx
└── README.md
```

> Rename the files above to match what you commit. The app automatically picks up any CSV in the working directory (preferring names containing `sugar_cosmetics_instagram_data`), or you can upload one in the sidebar.

---

## 📊 Dataset

14 columns, 50,000 rows, no null values in the numeric metrics and no fully duplicated rows.

| Group | Fields |
|---|---|
| Time | `Post Date` |
| Content | `Post Type` (Image, Reel, Story, Video), `Hashtags` |
| Campaign context | `Campaign Type` (Tutorial, Giveaway, Festive Offer, Product Launch, Influencer Collab), `Engagement Source` (Organic, Paid, Influencer, Collab) |
| Audience | `Audience Emotion` (Happy, Excited, Curious, Confident, Inspired) |
| Visibility | `Impressions`, `Reach` |
| Interactions | `Likes`, `Comments`, `Shares`, `Saves` |
| Actions | `Profile Visits`, `Follows` |

**Data caveats**

- There is no post ID or caption, so rows are called *records*, not confirmed unique posts. The app generates `POST-00001…` row IDs for exploration only.
- Hashtags are comma-separated in one cell and are split into individual tags only in the hashtag tab.
- The data has no follower-count history, spend, revenue or user-level journeys, so it cannot support claims about net follower growth, ROI or causal campaign lift.

---

## 🧮 Metric Definitions

| Metric | Formula |
|---|---|
| Total Engagements | Likes + Comments + Shares + Saves |
| Engagement Rate (Reach) | Σ Total Engagements ÷ Σ Reach |
| Engagement Rate (Impressions) | Σ Total Engagements ÷ Σ Impressions |
| Profile Visit Rate | Σ Profile Visits ÷ Σ Reach |
| Follow Conversion Rate | Σ Follows ÷ Σ Profile Visits |
| Share Rate / Save Rate | Σ Shares (or Saves) ÷ Σ Reach |

Rates are **weighted aggregates** (ratio of sums), not averages of per-row rates.

---

## 🖥️ Streamlit App

**Tabs**

1. **Executive Overview** – KPI cards, monthly reach vs. posting volume, engagement rate by post type, engagement mix, weekday averages, exposure-to-follow funnel (aggregate proxy)
2. **Content & Campaigns** – interactions by format, campaign / source / emotion engagement rates, reach vs. engagement scatter
3. **Hashtag Intelligence** – most-used and highest-engagement hashtags with a minimum-records slider
4. **Post Explorer** – search, sort, filter and download filtered records as CSV

**Sidebar filters:** date range, post type, campaign type, engagement source, audience emotion.

### Run locally

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install streamlit pandas numpy plotly
streamlit run main.py
```

Place the CSV in the same folder as `main.py`, or upload it from the sidebar.

---

## 📈 Tableau Dashboard

Open `Social_media_Sugar_cosmetic_Dashboard_Analysis.twb` in Tableau Desktop (the CSV must be reachable; re-point the data source if Tableau prompts you).

Worksheets include: Campaign Performance, Content Performance, Emotion vs Engagement, Engagement Rate by Reach, Hashtag Analysis, Source Efficiency, Trend Chart, Weekday Analysis, Weekly Engagement Heatmap, and KPI tiles (Total Posts, Total Reach, Total Engagements, Total Follows, Engagement %).

<details>
<summary>Key calculated fields</summary>

```
Total Engagements:        ZN([Likes]) + ZN([Comments]) + ZN([Shares]) + ZN([Saves])
Engagement Rate by Reach: IF SUM([Reach]) = 0 THEN 0
                          ELSE SUM([Total Engagements]) / SUM([Reach]) END
Profile Visit Rate:       IF SUM([Reach]) = 0 THEN 0
                          ELSE SUM([Profile Visits]) / SUM([Reach]) END
Follow Conversion Rate:   IF SUM([Profile Visits]) = 0 THEN 0
                          ELSE SUM([Follows]) / SUM([Profile Visits]) END
Month-Year:               DATETRUNC('month', [Post Date])
Weekday:                  DATENAME('weekday', [Post Date])
```
</details>

---

## 🔄 Workflow

```
CSV → validation & type conversion → calculated metrics
    → exploratory analysis (time, content, campaign, audience, hashtags)
    → Tableau (executive view) + Streamlit (interactive view)
    → findings, recommendations, next experiments
```

---

## 💡 Recommendations

1. Run controlled format experiments (Reel / Story / Video / Image) instead of assuming a winner.
2. Build a posting calendar and test weekday and time effects.
3. Turn strong campaigns, such as Influencer Collab, into testable playbooks.
4. Evaluate hashtags individually, not as combinations.
5. Improve the reach → profile visit → follow path with clearer CTAs and profile messaging.
6. Use a balanced KPI scorecard rather than optimizing for likes alone.
7. Capture post IDs, captions, publish time, follower snapshots and spend for future ROI analysis.

---

## ⚠️ Limitations & Next Steps

- Confirm whether each row is a unique post or a synthetic / aggregated record.
- The Tableau "Engagement %" KPI tile (32.90%) does not match the documented 18.55%. Check its calculated field, aggregation and filters.
- Add follower history, spend and attribution data to support growth and ROI analysis.

---

## 🛠️ Tech Stack

Python · Streamlit · Pandas · NumPy · Plotly · Tableau

## 👤 Author

**Ankan Chowdhury** · [LinkedIn](www.linkedin.com/in/ankan-chowdhury-440b9532b) · [GitHub](https://github.com/your-username)
