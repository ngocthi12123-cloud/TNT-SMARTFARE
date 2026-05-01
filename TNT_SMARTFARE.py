import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from geopy.geocoders import Nominatim
from datetime import datetime
import math

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
# 2. CSS PREMIUM DARK + MOBILE OPTIMIZATION
# ============================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@700;800;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

<style>
:root {
    --navy-900: #060b1f; --navy-800: #0a1330; --navy-700: #111c44;
    --gold: #f5c842; --gold-bright: #ffd86b; --text-primary: #f8fafc;
    --glass: rgba(255, 255, 255, 0.06); --glass-border: rgba(255, 255, 255, 0.12);
}

/* ẨN CÁC THÀNH PHẦN THỪA CỦA STREAMLIT ĐỂ GIỐNG APP */
#MainMenu, footer, header, [data-testid="stHeader"] { visibility: hidden; display: none !important; }
.block-container { padding: 1rem 0.5rem !important; max-width: 1400px; }

.stApp {
    background: radial-gradient(ellipse at top left, rgba(59, 130, 246, 0.18) 0%, transparent 45%),
                linear-gradient(180deg, #060b1f 0%, #0a1330 100%);
    color: var(--text-primary);
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* TỐI ƯU NÚT BẤM CHO DI ĐỘNG */
.stButton > button {
    width: 100% !important;
    height: 3.5rem !important;
    background: linear-gradient(135deg, #f5c842 0%, #b8860b 100%) !important;
    color: #060b1f !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    border: none !important;
}

/* INPUT ĐEN TRÊN NỀN TRẮNG DỄ ĐỌC */
.stTextInput input {
    background: #ffffff !important;
    color: #000000 !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

/* HERO SECTION RESPONSIVE */
.hero-wrap {
    background: rgba(10, 19, 48, 0.8);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 15px;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    background: linear-gradient(135deg, #f5c842, #ffd86b);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* KẾT QUẢ GIÁ TIỀN */
.result-shell {
    background: linear-gradient(135deg, rgba(10, 19, 48, 0.9), rgba(26, 38, 85, 0.9));
    border-radius: 24px;
    padding: 20px;
    margin-top: 15px;
    border-top: 2px solid var(--gold);
}
.price-mega { font-size: 38px !important; font-weight: 900; color: var(--gold-bright); }

/* MOBILE BREAKPOINTS */
@media (max-width: 640px) {
    .hero-stats { gap: 10px; }
    .stat-val { font-size: 18px; }
    .map-wrap { height: 350px !important; }
    .result-grid { grid-template-columns: 1fr !important; gap: 15px; text-align: center; }
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. DỮ LIỆU & LOGIC (GIỮ NGUYÊN)
# ============================================================
VEHICLES = {
    "Bike":      {"icon": "fa-bicycle",      "name": "Xe điện",  "seats": "1 chỗ",     "base": 10000, "km_rate": 4000,  "speed": 3.0},
    "Motorbike": {"icon": "fa-motorcycle",   "name": "Xe máy",       "seats": "1 chỗ",     "base": 12000, "km_rate": 4000,  "speed": 2.5},
    "Car4":      {"icon": "fa-car",          "name": "Ô tô 4 chỗ",   "seats": "4 chỗ",     "base": 25000, "km_rate": 11000, "speed": 2.8},
    "Car7":      {"icon": "fa-van-shuttle",  "name": "Ô tô 7 chỗ",   "seats": "7 chỗ",     "base": 32000, "km_rate": 14000, "speed": 3.0},
    "Luxury":    {"icon": "fa-car-side",     "name": "Luxury Car",   "seats": "4 chỗ VIP", "base": 30000, "km_rate": 13000, "speed": 2.5},
    "SUV":       {"icon": "fa-truck-pickup", "name": "SUV cao cấp",  "seats": "5 chỗ",     "base": 35000, "km_rate": 15000, "speed": 2.6},
}

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
geolocator = Nominatim(user_agent="tnt_smartfare_mobile")

def get_address(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), timeout=10)
        return location.address if location else f"{lat:.4f}, {lon:.4f}"
    except: return f"{lat:.4f}, {lon:.4f}"

def get_ai_traffic():
    hour = datetime.now().hour + datetime.now().minute / 60.0
    def peak(x, mu, sig): return math.exp(-pow(x - mu, 2) / (2 * pow(sig, 2)))
    score = (9.5 * peak(hour, 7.5, 1.2) + 7.0 * peak(hour, 12.0, 1.0) + 10.0 * peak(hour, 18.0, 1.5))
    return round(max(1.5, min(10.0, score)), 1)

# ============================================================
# 4. TRẠNG THÁI & HIỂN THỊ
# ============================================================
if 'start_coords' not in st.session_state: st.session_state.start_coords = [10.7769, 106.7009]
if 'end_coords' not in st.session_state: st.session_state.end_coords = [10.8231, 106.6297]
if 'start_addr' not in st.session_state: st.session_state.start_addr = "Quận 1, TP.HCM"
if 'end_addr' not in st.session_state: st.session_state.end_addr = "Quận Tân Bình, TP.HCM"
if 'vehicle' not in st.session_state: st.session_state.vehicle = "Car4"

auto_tf = get_ai_traffic()
current_time = datetime.now().strftime("%H:%M")

# HERO HEADER
st.markdown(f"""
<div class="hero-wrap">
    <div class="hero-title">TNT SMARTFARE 💎</div>
    <div style="display:flex; justify-content: space-between; margin-top:10px;">
        <div style="color:#94a3b8; font-size:12px;">{current_time} • Mật độ: {auto_tf}/10</div>
        <div style="color:#ffd86b; font-size:12px; font-weight:700;">AI ACTIVE</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Giao diện chính (Tự động chuyển cột trên Mobile)
col_map, col_ctrl = st.columns([1.5, 1])

with col_map:
    st.markdown('<div class="map-wrap">', unsafe_allow_html=True)
    m = folium.Map(location=st.session_state.start_coords, zoom_start=13, tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google")
    folium.Marker(st.session_state.start_coords, icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(st.session_state.end_coords, icon=folium.Icon(color='red')).add_to(m)
    
    dist = 0
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{st.session_state.start_coords[1]},{st.session_state.start_coords[0]};{st.session_state.end_coords[1]},{st.session_state.end_coords[0]}?overview=full&geometries=geojson"
        res = requests.get(url, timeout=5).json()
        if 'routes' in res:
            dist = res['routes'][0]['distance'] / 1000
            coords = [(p[1], p[0]) for p in res['routes'][0]['geometry']['coordinates']]
            folium.PolyLine(coords, color="#f5c842", weight=6).add_to(m)
    except: pass

    map_data = st_folium(m, height=400, width="100%", key="mobile_map")
    st.markdown('</div>', unsafe_allow_html=True)

with col_ctrl:
    st.text_input("📍 Điểm đón", value=st.session_state.start_addr, key="s_in")
    st.text_input("🏁 Điểm đến", value=st.session_state.end_addr, key="e_in")
    
    veh_choice = st.selectbox("Chọn xe", list(VEHICLES.keys()), 
                             format_func=lambda x: f"{VEHICLES[x]['name']} ({VEHICLES[x]['seats']})")
    st.session_state.vehicle = veh_choice
    is_raining = st.toggle("🌧️ Trời mưa")

# TÍNH GIÁ & HIỂN THỊ KẾT QUẢ
v = VEHICLES[st.session_state.vehicle]
if dist > 0:
    sim.input['distance'] = min(dist, 50)
    sim.input['traffic'] = auto_tf
    sim.input['weather'] = 8 if is_raining else 2
    sim.compute()
    surge = 1 + (sim.output['price'] / 100)
    final_price = max(0, round(((v['base'] + dist * v['km_rate']) * surge) / 1000) * 1000)
    
    st.markdown(f"""
    <div class="result-shell">
        <div class="result-grid">
            <div>
                <div style="color:#94a3b8; font-size:14px;">Giá dự kiến (x{surge:.2f})</div>
                <div class="price-mega">{final_price:,} <span style="font-size:20px;">VNĐ</span></div>
            </div>
            <button class="stButton" style="margin-top:10px;">XÁC NHẬN ĐẶT XE</button>
        </div>
        <div style="display:flex; justify-content:space-between; margin-top:15px; color:#cbd5e1; font-size:12px;">
            <span><i class="fa-solid fa-route"></i> {dist:.1f} km</span>
            <span><i class="fa-regular fa-clock"></i> {max(1, int(dist * v['speed']))} phút</span>
            <span><i class="fa-solid fa-car"></i> {v['name']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><center style='color:#666; font-size:10px;'>TNT SMARTFARE v2.0 Mobile Optimized</center>", unsafe_allow_html=True)
