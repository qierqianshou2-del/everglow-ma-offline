import streamlit as st
import requests
import json
import time
from datetime import datetime

GIST_ID = "9e38e0bce5a40760ead9257f885cae7e"   # <- same Gist ID as monitor script

st.set_page_config(page_title="everglow offline MA Fansign", page_icon="🎫", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.metric-card { background:white; border-radius:14px; padding:20px 24px; box-shadow:0 2px 12px rgba(0,0,0,0.06); margin-bottom:8px; }
.metric-label { font-size:11px; color:#8a90a2; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:8px; }
.metric-value { font-family:'JetBrains Mono',monospace; font-size:32px; font-weight:600; color:#1a1d2e; line-height:1; }
.notice-box { background:white; border-left:3px solid #4a90d9; border-radius:0 8px 8px 0; padding:13px 16px; font-size:13px; color:#8a90a2; line-height:1.75; margin-bottom:24px; }
.pill-up   { background:#e8f7ef; color:#3db87a; padding:3px 12px; border-radius:20px; font-family:monospace; font-weight:600; }
.pill-down { background:#fdf0f1; color:#e05c6a; padding:3px 12px; border-radius:20px; font-family:monospace; font-weight:600; }
.pill-flat { background:#f0f2f7; color:#8a90a2; padding:3px 12px; border-radius:20px; font-family:monospace; font-weight:600; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🎫 everglow offline MA Fansign")
st.markdown("<p style='color:#8a90a2;margin-top:-12px'>MusicArt · everglow offline MA Fansign</p>", unsafe_allow_html=True)
st.markdown("""<div class="notice-box">
Please monitor sales changes closely in the last 5–10 minutes for any supplementary orders.
The recommended cut is calculated from the median of all data sources — for reference only.
Contact us: <strong>vx: qx12423</strong>
</div>""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    threshold = st.number_input("💧 Inflation Threshold", min_value=0, value=0, step=1)
    quota     = st.number_input("👤 Quota Slots", min_value=1, value=15, step=1)
    st.markdown("---")
    st.markdown("*Auto-refreshes every 30s*")

def fetch_gist():
    url  = f"https://api.github.com/gists/{GIST_ID}"
    resp = requests.get(url, headers={"Accept": "application/vnd.github.v3+json"}, timeout=10)
    raw  = resp.json()["files"]["musicart_data.json"]["content"]
    return json.loads(raw)

try:
    gist = fetch_gist()
    updated_at = gist.get("updated_at", "—")
    products   = gist.get("products", {})
except Exception as e:
    st.error(f"Could not read data: {e}")
    gist       = {}
    updated_at = "—"
    products   = {}

# ── Stats ─────────────────────────────────────────────────────────────────────
first_product = list(products.values())[0] if products else {}
latest_sales  = first_product.get("latest_sales", "—")

cut = "—"
if threshold and quota and isinstance(latest_sales, int):
    c = round((latest_sales - threshold) / quota)
    cut = str(c) if c > 0 else "—"

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">💧 Inflation Threshold</div>
        <div class="metric-value">{threshold if threshold else "—"}</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">👤 Quota Slots</div>
        <div class="metric-value">{quota}</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">🏷 Recommended CUT</div>
        <div class="metric-value">{cut}</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-label">📊 Total Sales</div>
        <div class="metric-value">{latest_sales}</div>
    </div>""", unsafe_allow_html=True)

st.markdown(f"<p style='font-size:12px;color:#8a90a2;font-family:monospace;margin-top:4px'>🟢 Data from: {updated_at}</p>", unsafe_allow_html=True)

# ── Sales log ─────────────────────────────────────────────────────────────────
st.markdown("### 📋 Real-Time Sales Log")

all_history = []
for name, info in products.items():
    for h in info.get("history", []):
        all_history.append({**h, "product": name})

all_history.sort(key=lambda x: x["time"], reverse=True)

if not all_history:
    st.info("📡 Waiting for first data from your monitor script...")
else:
    rows_html = []
    for r in all_history:
        if r["before"] is None:
            change = f"Initial: {r['after']}"
            pill   = '<span class="pill-flat">0</span>'
        else:
            change = f"{r['before']} → {r['after']}"
            diff   = r["diff"]
            if diff > 0:
                pill = f'<span class="pill-up">+{diff}</span>'
            elif diff < 0:
                pill = f'<span class="pill-down">{diff}</span>'
            else:
                pill = '<span class="pill-flat">0</span>'

        rows_html.append(f"""
        <tr style="border-bottom:1px solid #f3f4f7">
            <td style="padding:12px 16px;font-family:monospace;font-size:12px;color:#8a90a2">{r['time']}</td>
            <td style="padding:12px 16px;font-weight:500">{r['product']}</td>
            <td style="padding:12px 16px;font-family:monospace;font-size:12px;color:#8a90a2">{change}</td>
            <td style="padding:12px 16px">{pill}</td>
        </tr>""")

    st.markdown(f"""
    <div style="background:white;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,0.06);overflow:hidden">
    <table style="width:100%;border-collapse:collapse">
        <thead><tr style="background:#fafbfc;border-bottom:1px solid #e8eaef">
            <th style="padding:10px 16px;text-align:left;font-size:11px;color:#b0b6c8;font-weight:600;text-transform:uppercase">Time</th>
            <th style="padding:10px 16px;text-align:left;font-size:11px;color:#b0b6c8;font-weight:600;text-transform:uppercase">Product</th>
            <th style="padding:10px 16px;text-align:left;font-size:11px;color:#b0b6c8;font-weight:600;text-transform:uppercase">Stock Change</th>
            <th style="padding:10px 16px;text-align:left;font-size:11px;color:#b0b6c8;font-weight:600;text-transform:uppercase">Units Sold</th>
        </tr></thead>
        <tbody>{''.join(rows_html)}</tbody>
    </table></div>""", unsafe_allow_html=True)

time.sleep(30)
st.rerun()
