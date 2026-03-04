import streamlit as st
import requests
import time
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
PRODUCTS = {
    "everglow offline": "3530663",
}
CART_ID  = "ml5al9hn6ex"
INTERVAL = 30

API_URL = "https://app.malltail.com/global_shopping/api.php"
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-GB,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "http://www.musicart.kr",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="everglow offline MA Fansign",
    page_icon="🎫",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.main { background: #f0f2f7; }

.metric-card {
    background: white;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 8px;
}
.metric-label {
    font-size: 11px;
    color: #8a90a2;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 32px;
    font-weight: 600;
    color: #1a1d2e;
    line-height: 1;
}
.notice-box {
    background: white;
    border-left: 3px solid #4a90d9;
    border-radius: 0 8px 8px 0;
    padding: 13px 16px;
    font-size: 13px;
    color: #8a90a2;
    line-height: 1.75;
    margin-bottom: 24px;
}
.pill-up   { background:#e8f7ef; color:#3db87a; padding:3px 12px; border-radius:20px; font-family:monospace; font-weight:600; }
.pill-down { background:#fdf0f1; color:#e05c6a; padding:3px 12px; border-radius:20px; font-family:monospace; font-weight:600; }
.pill-flat { background:#f0f2f7; color:#8a90a2; padding:3px 12px; border-radius:20px; font-family:monospace; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🎫 everglow offline MA Fansign")
st.markdown("<p style='color:#8a90a2;margin-top:-12px'>MusicArt · everglow offline MA Fansign</p>", unsafe_allow_html=True)

st.markdown("""
<div class="notice-box">
Please monitor sales changes closely in the last 5–10 minutes for any supplementary orders.
The recommended cut is calculated from the median of all data sources — for reference only, not a guaranteed cut-off line.
If quota numbers seem incorrect or data hasn't updated in a while, contact us: <strong>vx: qx12423</strong>
</div>
""", unsafe_allow_html=True)

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    threshold = st.number_input("💧 Inflation Threshold", min_value=0, value=0, step=1)
    quota     = st.number_input("👤 Quota Slots", min_value=1, value=15, step=1)
    interval  = st.number_input("⏱ Interval (sec)", min_value=5, value=INTERVAL, step=5)
    st.markdown("---")
    st.markdown("**Running:** fetches every " + str(interval) + "s")
    st.markdown("*Keep this tab open to continue monitoring*")

# ── State init ────────────────────────────────────────────────────────────────
if "records"    not in st.session_state: st.session_state.records    = []
if "prev_sales" not in st.session_state: st.session_state.prev_sales = {}
if "run_count"  not in st.session_state: st.session_state.run_count  = 0

# ── Fetch ─────────────────────────────────────────────────────────────────────
def fetch_sales(uid):
    hdrs = HEADERS.copy()
    hdrs["referer"] = f"http://www.musicart.kr/shop/shopdetail.html?branduid={uid}"
    payload = {
        "action": "product", "g-recaptcha": "", "_": "makeshop",
        "cookieConsent": "true", "productInfo": "[]",
        "browser_language": "en-gb", "isMobile": "false",
        "uid": uid, "cart_id": CART_ID, "country": "SG",
    }
    r    = requests.post(API_URL, headers=hdrs, data=payload, timeout=10)
    data = r.json()
    if data.get("status") != "success":
        return None, data.get("message", "error")
    sales = int(data["data"][0]["options"]["basic"][0].get("sto_order_stock", 0))
    return sales, None

# ── Do one fetch cycle ────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
latest_sales = {}

for name, uid in PRODUCTS.items():
    try:
        sales, err = fetch_sales(uid)
        if err:
            st.warning(f"[{name}] API error: {err}")
            continue
        prev = st.session_state.prev_sales.get(name)
        latest_sales[name] = sales
        if prev is None:
            st.session_state.records.append({
                "time": now_str, "product": name,
                "before": None, "after": sales, "diff": None
            })
        elif sales != prev:
            diff = sales - prev
            st.session_state.records.append({
                "time": now_str, "product": name,
                "before": prev, "after": sales, "diff": diff
            })
        st.session_state.prev_sales[name] = sales
    except Exception as e:
        st.error(f"[{name}] {e}")

st.session_state.run_count += 1

# ── Stats row ─────────────────────────────────────────────────────────────────
total = list(latest_sales.values())[0] if latest_sales else st.session_state.prev_sales.get(list(PRODUCTS.keys())[0], "—")
cut   = "—"
if threshold and quota and isinstance(total, int):
    c = round((total - threshold) / quota)
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
        <div class="metric-value">{total}</div>
    </div>""", unsafe_allow_html=True)

# ── Last updated ──────────────────────────────────────────────────────────────
st.markdown(f"<p style='font-size:12px;color:#8a90a2;font-family:monospace;margin-top:4px'>🟢 Last updated: {now_str} &nbsp;·&nbsp; check #{st.session_state.run_count}</p>", unsafe_allow_html=True)

# ── Sales log table ───────────────────────────────────────────────────────────
st.markdown("### 📋 Real-Time Sales Log")

records = st.session_state.records
if not records:
    st.info("📡 Waiting for first data...")
else:
    rows = []
    for r in reversed(records):
        if r["diff"] is None:
            change = f"Initial: {r['after']}"
            pill   = f'<span class="pill-flat">0</span>'
        else:
            change = f"{r['before']} → {r['after']}"
            sign   = "+" if r["diff"] > 0 else ""
            cls    = "pill-up" if r["diff"] > 0 else "pill-down"
            pill   = f'<span class="{cls}">{sign}{r["diff"]}</span>'
        rows.append(f"""
        <tr style="border-bottom:1px solid #f3f4f7">
            <td style="padding:12px 16px;font-family:monospace;font-size:12px;color:#8a90a2">{r['time']}</td>
            <td style="padding:12px 16px;font-weight:500">{r['product']}</td>
            <td style="padding:12px 16px;font-family:monospace;font-size:12px;color:#8a90a2">{change}</td>
            <td style="padding:12px 16px">{pill}</td>
        </tr>""")

    st.markdown(f"""
    <div style="background:white;border-radius:14px;box-shadow:0 2px 12px rgba(0,0,0,0.06);overflow:hidden">
    <table style="width:100%;border-collapse:collapse">
        <thead>
            <tr style="background:#fafbfc;border-bottom:1px solid #e8eaef">
                <th style="padding:10px 16px;text-align:left;font-size:11px;color:#b0b6c8;font-weight:600;text-transform:uppercase;letter-spacing:0.4px">Time</th>
                <th style="padding:10px 16px;text-align:left;font-size:11px;color:#b0b6c8;font-weight:600;text-transform:uppercase;letter-spacing:0.4px">Product</th>
                <th style="padding:10px 16px;text-align:left;font-size:11px;color:#b0b6c8;font-weight:600;text-transform:uppercase;letter-spacing:0.4px">Stock Change</th>
                <th style="padding:10px 16px;text-align:left;font-size:11px;color:#b0b6c8;font-weight:600;text-transform:uppercase;letter-spacing:0.4px">Units Sold</th>
            </tr>
        </thead>
        <tbody>{''.join(rows)}</tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

# ── Auto-refresh ──────────────────────────────────────────────────────────────
time.sleep(int(interval))
st.rerun()
