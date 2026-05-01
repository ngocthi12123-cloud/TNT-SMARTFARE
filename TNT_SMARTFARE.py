# copy từ app5
# này dùng cho github
import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from geopy.geocoders import Nominatim
from datetime import datetime
from zoneinfo import ZoneInfo
import math

# ============================================================
# TIMEZONE VIỆT NAM
# ============================================================
VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")

# ============================================================
# 1. CẤU HÌNH TRANG
# ============================================================
st.set_page_config(
    page_title="TNT SMARTFARE",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="collapsed"
)

# ============================================================
# 2. (GIỮ NGUYÊN CSS CỦA BẠN)
# ============================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<style>
:root {
    --navy-900: #060b1f;
    --navy-800: #0a1330;
    --navy-700: #111c44;
    --navy-600: #1a2655;
    --gold: #f5c842;
    --gold-bright: #ffd86b;
    --gold-deep: #b8860b;
    --blue-electric: #3b82f6;
    --blue-glow: #60a5fa;
    --text-primary: #f8fafc;
    --text-secondary: #cbd5e1;
    --text-muted: #94a3b8;
    --glass: rgba(255, 255, 255, 0.06);
    --glass-border: rgba(255, 255, 255, 0.12);
    --gold-grad: linear-gradient(135deg, #f5c842 0%, #ffd86b 50%, #b8860b 100%);
}

.stApp {
    background:
        radial-gradient(ellipse at top left, rgba(59, 130, 246, 0.18) 0%, transparent 45%),
        radial-gradient(ellipse at bottom right, rgba(245, 200, 66, 0.12) 0%, transparent 45%),
        linear-gradient(180deg, #060b1f 0%, #0a1330 50%, #060b1f 100%);
    color: var(--text-primary);
    font-family: 'Plus Jakarta Sans', sans-serif;
}

#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1400px; }

.hero-wrap {
    position: relative;
    background: linear-gradient(135deg, rgba(10, 19, 48, 0.9) 0%, rgba(17, 28, 68, 0.85) 100%);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 32px 40px;
    margin-bottom: 24px;
    overflow: hidden;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}
.hero-wrap::before {
    content: '';
    position: absolute; top: -50%; right: -10%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(245, 200, 66, 0.25) 0%, transparent 70%);
    filter: blur(40px);
}
.hero-wrap::after {
    content: '';
    position: absolute; bottom: -50%; left: -10%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.25) 0%, transparent 70%);
    filter: blur(40px);
}
.hero-content { position: relative; z-index: 2; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px; }
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 42px; font-weight: 900;
    background: var(--gold-grad);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0; letter-spacing: -1px;
    line-height: 1.1;
}
.hero-sub { font-size: 14px; color: var(--text-secondary); margin-top: 8px; letter-spacing: 0.5px; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(245, 200, 66, 0.12);
    border: 1px solid rgba(245, 200, 66, 0.4);
    color: var(--gold-bright);
    padding: 6px 14px; border-radius: 50px;
    font-size: 11px; font-weight: 700; letter-spacing: 1.5px;
    text-transform: uppercase; margin-bottom: 12px;
}
.hero-badge .dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--gold-bright);
    box-shadow: 0 0 10px var(--gold-bright);
    animation: pulse 1.8s ease-in-out infinite;
}
@keyframes pulse { 0%,100% { opacity: 1; transform: scale(1);} 50% { opacity: 0.5; transform: scale(1.4);} }

.hero-stats { display: flex; gap: 28px; }
.stat-item { text-align: right; }
.stat-val { font-family: 'Playfair Display', serif; font-size: 24px; font-weight: 800; color: var(--gold-bright); }
.stat-lbl { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1.2px; }

.panel-title {
    font-size: 13px; font-weight: 700; color: var(--gold-bright);
    text-transform: uppercase; letter-spacing: 2px;
    margin-bottom: 16px; display: flex; align-items: center; gap: 10px;
}
.panel-title i { color: var(--gold); font-size: 16px; }

[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 20px !important;
    backdrop-filter: blur(16px);
}
/* Đổi màu chữ tiêu đề 'Điểm đón' và 'Điểm đến' */
[data-testid="stWidgetLabel"] p {
    color: #f8fafc !important;
    font-weight: 700 !important; /* Làm chữ đậm lên cho rõ */
    text-shadow: 0px 0px 5px rgba(0,0,0,0.5); /* Thêm chút bóng cho nổi bật */
}

/* ĐOẠN ĐÃ SỬA */
.stTextInput input, .stTextArea textarea {
    background: #ffffff !important; /* Đổi nền sang trắng để hiện chữ đen */
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    color: #000000 !important; /* Đổi chữ sang đen */
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.25s ease;
}

/* Đảm bảo khi focus vào ô cũng giữ màu đen */
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(245, 200, 66, 0.15) !important;
    background: #ffffff !important;
    color: #000000 !important;
}

.stButton > button {
    background: var(--gold-grad) !important;
    color: var(--navy-900) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    padding: 12px 24px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    letter-spacing: 0.3px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 6px 20px rgba(245, 200, 66, 0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 28px rgba(245, 200, 66, 0.45) !important;
    filter: brightness(1.08);
}
.stButton > button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.06) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--glass-border) !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    border-color: var(--gold) !important;
}

/* Đổi màu chữ của các tùy chọn chọn xe (Radio buttons) */
.stRadio div[role="radiogroup"] label p {
    color: #f8fafc !important;
    font-weight: 500 !important;
}

.stMarkdown h2, .stMarkdown h3, [data-testid="stHeading"] {
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

[data-testid="stAlertContainer"] {
    background: rgba(34, 197, 94, 0.1) !important;
    border: 1px solid rgba(34, 197, 94, 0.3) !important;
    color: #86efac !important;
    border-radius: 12px !important;
}

.veh-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px; }
.veh-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid var(--glass-border);
    border-radius: 14px;
    padding: 12px;
    text-align: center;
    transition: all 0.25s ease;
}
.veh-card.active {
    background: rgba(245, 200, 66, 0.1);
    border-color: var(--gold);
    box-shadow: 0 0 0 2px rgba(245, 200, 66, 0.2);
}
.veh-card i { font-size: 22px; color: var(--gold-bright); }
.veh-card .name { font-size: 12px; font-weight: 700; margin-top: 6px; color: var(--text-primary);}
.veh-card .seats { font-size: 10px; color: var(--text-muted); margin-top: 2px;}

.result-shell {
    margin-top: 24px;
    background: linear-gradient(135deg, rgba(10, 19, 48, 0.8) 0%, rgba(26, 38, 85, 0.9) 100%);
    border: 1px solid var(--glass-border);
    border-radius: 28px;
    padding: 32px;
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.06);
    position: relative;
    overflow: hidden;
    animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes slideUp { from { opacity: 0; transform: translateY(16px);} to { opacity: 1; transform: translateY(0);} }
.result-shell::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: var(--gold-grad);}
.result-grid { display: grid; grid-template-columns: 1fr auto; gap: 24px; align-items: center; }

.ai-pill {
    display: inline-flex; align-items: center; gap: 8px;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(96, 165, 250, 0.1));
    border: 1px solid rgba(96, 165, 250, 0.4);
    color: var(--blue-glow);
    padding: 6px 14px; border-radius: 50px;
    font-size: 11px; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase;
}

.price-label { color: var(--text-muted); font-size: 13px; margin-top: 14px; letter-spacing: 0.5px;text-align: center; /* THÊM DÒNG NÀY */
    width: 100%;        /* THÊM DÒNG NÀY */}

.price-mega {
    font-family: 'Playfair Display', serif;
    font-size: 56px; font-weight: 900;
    background: var(--gold-grad);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1; letter-spacing: -2px;
    margin-top: 4px;
    text-align: center; /* THÊM DÒNG NÀY */
    width: 100%;        /* THÊM DÒNG NÀY */
    display: block;
}
.price-currency { font-size: 22px; color: var(--gold); font-weight: 700; margin-left: 6px; }

.confirm-btn {
    background: var(--gold-grad);
    color: var(--navy-900);
    border: none; padding: 18px 36px; border-radius: 16px;
    font-weight: 800; font-size: 14px; letter-spacing: 1.5px;
    cursor: pointer;
    box-shadow: 0 10px 30px rgba(245, 200, 66, 0.35);
    transition: all 0.3s ease;
    text-transform: uppercase;
    font-family: 'Plus Jakarta Sans', sans-serif;
    display: inline-flex; align-items: center; gap: 10px;
}
.confirm-btn:hover { transform: translateY(-3px); box-shadow: 0 16px 40px rgba(245, 200, 66, 0.5);}

.meta-row {
    margin-top: 24px; padding-top: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    display: flex; flex-wrap: wrap; gap: 24px;
}
.meta-item { display: flex; align-items: center; gap: 10px; }
.meta-icon {
    width: 38px; height: 38px; border-radius: 10px;
    background: rgba(245, 200, 66, 0.1);
    border: 1px solid rgba(245, 200, 66, 0.25);
    display: flex; align-items: center; justify-content: center;
    color: var(--gold-bright); font-size: 14px;
}
.meta-text .lbl { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px;}
.meta-text .val { font-size: 15px; color: var(--text-primary); font-weight: 700; margin-top: 2px;}

.empty-state {
    text-align: center; padding: 50px 30px;
    background: var(--glass);
    border: 1px dashed var(--glass-border);
    border-radius: 24px;
    margin-top: 24px;
}
.empty-state i { font-size: 48px; color: var(--gold); margin-bottom: 16px; }
.empty-state h3 { color: var(--text-primary); font-weight: 700; margin: 0; }
.empty-state p { color: var(--text-muted); margin-top: 8px; }

.map-wrap {
    border-radius: 20px; overflow: hidden;
    border: 1px solid var(--glass-border);
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
}
iframe { border-radius: 20px !important; }

::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-track { background: var(--navy-900); }
::-webkit-scrollbar-thumb { background: var(--navy-600); border-radius: 5px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold-deep); }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. DỮ LIỆU XE (GIỮ NGUYÊN)
# ============================================================
VEHICLES = {
    "Bike":      {"icon": "fa-bicycle",      "name": "Xe điện",  "seats": "1 chỗ",     "base": 10000, "km_rate": 4000,  "speed": 3.0},
    "Motorbike": {"icon": "fa-motorcycle",   "name": "Xe máy",       "seats": "1 chỗ",     "base": 12000, "km_rate": 4000,  "speed": 2.5},
    "Car4":      {"icon": "fa-car",          "name": "Ô tô 4 chỗ",   "seats": "4 chỗ",     "base": 25000, "km_rate": 11000, "speed": 2.8},
    "Car7":      {"icon": "fa-van-shuttle",  "name": "Ô tô 7 chỗ",   "seats": "7 chỗ",     "base": 32000, "km_rate": 14000, "speed": 3.0},
    "Luxury":    {"icon": "fa-car-side",     "name": "Luxury Car",   "seats": "4 chỗ VIP", "base": 30000, "km_rate": 13000, "speed": 2.5},
    "SUV":       {"icon": "fa-truck-pickup", "name": "SUV cao cấp",  "seats": "5 chỗ",     "base": 35000, "km_rate": 15000, "speed": 2.6},
}


# ============================================================
# 4. FUZZY LOGIC + AI TRAFFIC (ĐÃ FIX GIỜ VN)
# ============================================================

@st.cache_resource
def init_fuzzy():
    distance = ctrl.Antecedent(np.arange(0, 51, 1), 'distance')
    traffic = ctrl.Antecedent(np.arange(0, 11, 1), 'traffic')
    weather = ctrl.Antecedent(np.arange(0, 11, 1), 'weather')
    price = ctrl.Consequent(np.arange(0, 101, 1), 'price')

    distance.automf(3, names=['short', 'medium', 'long'])
    traffic.automf(3, names=['low', 'medium', 'high'])
    weather['good'] = fuzz.trimf(weather.universe, [0, 0, 5])
    weather['bad'] = fuzz.trimf(weather.universe, [5, 10, 10])
    price.automf(3, names=['low', 'medium', 'high'])

    rules = [
        ctrl.Rule(traffic['high'] | weather['bad'], price['high']),
        ctrl.Rule(traffic['low'] & weather['good'], price['low']),
        ctrl.Rule(distance['medium'] & traffic['medium'], price['medium']),
        ctrl.Rule(distance['long'], price['high'])
    ]
    return ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))

sim = init_fuzzy()
geolocator = Nominatim(user_agent="tnt_grab_pro_v6")

# ============================================================
# FIX: AI TRAFFIC THEO GIỜ VIỆT NAM
# ============================================================
def get_ai_traffic():
    now = datetime.now(VN_TZ)
    hour = now.hour + now.minute / 60.0

    def peak(x, mu, sig):
        return math.exp(-((x - mu) ** 2) / (2 * (sig ** 2)))

    score = (
        9.5 * peak(hour, 7.5, 1.2) +
        7.0 * peak(hour, 12.0, 1.0) +
        10.0 * peak(hour, 18.0, 1.5)
    )

    return round(max(1.5, min(10.0, score)), 1)

# ============================================================
# 5. SESSION (GIỮ NGUYÊN)
# ============================================================

if 'start_coords' not in st.session_state: st.session_state.start_coords = [10.7769, 106.7009]
if 'end_coords' not in st.session_state: st.session_state.end_coords = [10.8231, 106.6297]
if 'start_addr' not in st.session_state: st.session_state.start_addr = "Quận 1, TP.HCM"
if 'end_addr' not in st.session_state: st.session_state.end_addr = "Quận Tân Bình, TP.HCM"
if 'vehicle' not in st.session_state: st.session_state.vehicle = "Luxury"

# ============================================================
# 6. HERO HEADER (ĐÃ FIX GIỜ VN)
# ============================================================

auto_tf = get_ai_traffic()
current_time = datetime.now(VN_TZ).strftime("%H:%M")

st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-content">
    <div>
      <div class="hero-badge"><span class="dot"></span> AI POWERED · FUZZY LOGIC ENGINE</div>
      <h1 class="hero-title">TNT SMARTFARE</h1>
      <div class="hero-sub">Hệ thống định vị thông minh · Tính cước phí mờ</div>
    </div>
    <div class="hero-stats">
      <div class="stat-item">
        <div class="stat-val">{current_time}</div>
        <div class="stat-lbl">Thời gian</div>
      </div>
      <div class="stat-item">
        <div class="stat-val">{auto_tf}/10</div>
        <div class="stat-lbl">Mật độ</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
