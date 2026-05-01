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
# 2. CSS PREMIUM DARK + GLASSMORPHISM (Cập nhật màu Label)
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

/* ĐỔI MÀU LABEL (Điểm đón, Điểm đến, Mã giảm giá) SANG VÀNG */
.stWidgetLabel p {
    color: var(--gold-bright) !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
}

/* Ô NHẬP LIỆU: Nền trắng, Chữ đen */
.stTextInput input, .stTextArea textarea {
    background: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #1a1a1a !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    font-weight: 500 !important;
}

.hero-wrap {
    position: relative;
    background: linear-gradient(135deg, rgba(10, 19, 48, 0.9) 0%, rgba(17, 28, 68, 0.85) 100%);
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 32px 40px;
    margin-bottom: 24px;
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 42px; font-weight: 900;
    background: var(--gold-grad);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.panel-title {
    font-size: 13px; font-weight: 700; color: var(--gold-bright);
    text-transform: uppercase; letter-spacing: 2px;
    margin-bottom: 16px; display: flex; align-items: center; gap: 10px;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--glass) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: 20px !important;
}

.stButton > button {
    background: var(--gold-grad) !important;
    color: var(--navy-900) !important;
    border-radius: 12px !important;
    font-weight: 800 !important;
    transition: all 0.3s ease;
}

.result-shell {
    margin-top: 24px;
    background: linear-gradient(135deg, rgba(10, 19, 48, 0.8) 0%, rgba(26, 38, 85, 0.9) 100%);
    border: 1px solid var(--glass-border);
    border-radius: 28px;
    padding: 32px;
    position: relative;
}
.result-shell::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: var(--gold-grad);}

</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. DỮ LIỆU & HÀM HỖ TRỢ
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
geolocator = Nominatim(user_agent="tnt_smartfare_v6")

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
# 4. TRẠNG THÁI & GIAO DIỆN
# ============================================================
if 'start_coords' not in st.session_state: st.session_state.start_coords = [10.7769, 106.7009]
if 'end_coords' not in st.session_state: st.session_state.end_coords = [10.8231, 106.6297]
if 'start_addr' not in st.session_state: st.session_state.start_addr = "Quận 1, TP.HCM"
if 'end_addr' not in st.session_state: st.session_state.end_addr = "Quận Tân Bình, TP.HCM"
if 'vehicle' not in st.session_state: st.session_state.vehicle = "Luxury"

auto_tf = get_ai_traffic()

# Hero Header
st.markdown(f"""
<div class="hero-wrap">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <h1 class="hero-title">TNT SMARTFARE 💎</h1>
            <p style="color:var(--text-secondary);">Hệ thống định giá Logistics thông minh</p>
        </div>
        <div style="text-align:right;">
            <div style="font-size:24px; color:var(--gold-bright); font-weight:800;">{auto_tf}/10</div>
            <div style="font-size:11px; color:var(--text-muted);">MẬT ĐỘ GIAO THÔNG</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_map, col_ctrl = st.columns([2.2, 1], gap="medium")

with col_ctrl:
    st.markdown('<div class="panel-title"><i class="fa-solid fa-route"></i> Lộ trình</div>', unsafe_allow_html=True)
    with st.container(border=True):
        # Ô nhập liệu có label màu vàng, text màu đen nền trắng
        s_input = st.text_input("📍 Điểm đón", value=st.session_state.start_addr)
        e_input = st.text_input("🏁 Điểm đến", value=st.session_state.end_addr)
        
        c1, c2 = st.columns(2)
        if c1.button("Tìm địa chỉ", use_container_width=True):
            try:
                l1, l2 = geolocator.geocode(s_input), geolocator.geocode(e_input)
                if l1: st.session_state.start_coords, st.session_state.start_addr = [l1.latitude, l1.longitude], l1.address
                if l2: st.session_state.end_coords, st.session_state.end_addr = [l2.latitude, l2.longitude], l2.address
                st.rerun()
            except: st.error("Lỗi tìm kiếm")
        if c2.button("Làm mới", use_container_width=True, type="secondary"):
            st.session_state.start_coords, st.session_state.end_coords = [10.7769, 106.7009], [10.8231, 106.6297]
            st.rerun()

    st.markdown('<div class="panel-title" style="margin-top:15px;"><i class="fa-solid fa-car"></i> Phương tiện</div>', unsafe_allow_html=True)
    with st.container(border=True):
        chosen = st.radio("Chọn xe", options=list(VEHICLES.keys()), 
                          format_func=lambda x: f"{VEHICLES[x]['name']}", label_visibility="collapsed")
        st.session_state.vehicle = chosen
        v_info = VEHICLES[chosen]
        st.info(f"Mở cửa: {v_info['base']:,}đ | Cước: {v_info['km_rate']:,}đ/km")

    st.markdown('<div class="panel-title" style="margin-top:15px;"><i class="fa-solid fa-tags"></i> Ưu đãi</div>', unsafe_allow_html=True)
    with st.container(border=True):
        is_raining = st.toggle("🌧️ Thời tiết xấu", value=False)
        promo = st.text_input("🎟️ Mã giảm giá (VD: UEH)", placeholder="Nhập mã...").upper()

with col_map:
    st.markdown('<div class="panel-title"><i class="fa-solid fa-map"></i> Bản đồ trực tiếp</div>', unsafe_allow_html=True)
    m = folium.Map(location=st.session_state.start_coords, zoom_start=13, 
                   tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google")
    
    folium.Marker(st.session_state.start_coords, icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(st.session_state.end_coords, icon=folium.Icon(color='red')).add_to(m)

    dist = 0
    try:
        p1, p2 = st.session_state.start_coords, st.session_state.end_coords
        url = f"http://router.project-osrm.org/route/v1/driving/{p1[1]},{p1[0]};{p2[1]},{p2[0]}?overview=full&geometries=geojson"
        res = requests.get(url).json()
        if 'routes' in res:
            route = res['routes'][0]
            dist = route['distance'] / 1000
            coords = [(p[1], p[0]) for p in route['geometry']['coordinates']]
            folium.PolyLine(coords, color="#f5c842", weight=6).add_to(m)
    except: pass

    st_folium(m, height=500, width="100%", key="map")

# ============================================================
# 5. TÍNH TOÁN & HIỂN THỊ KẾT QUẢ
# ============================================================
if dist > 0:
    v = VEHICLES[st.session_state.vehicle]
    sim.input['distance'] = min(dist, 50)
    sim.input['traffic'] = auto_tf
    sim.input['weather'] = 8 if is_raining else 2
    sim.compute()

    surge = 1 + (sim.output['price'] / 100)
    total = (v['base'] + dist * v['km_rate']) * surge
    if promo == "UEH": total -= 20000
    
    final_p = max(0, round(total / 1000) * 1000)
    
    st.markdown(f"""
    <div class="result-shell">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <p style="color:var(--text-muted); margin:0;">Cước phí dự kiến</p>
                <h2 style="color:var(--gold); font-size:48px; margin:0;">{final_p:,} <span style="font-size:20px;">VNĐ</span></h2>
            </div>
            <button style="background:var(--gold-grad); border:none; padding:15px 30px; border-radius:12px; font-weight:800; cursor:pointer;">
                ĐẶT XE NGAY
            </button>
        </div>
        <div style="display:flex; gap:30px; margin-top:20px; border-top:1px solid rgba(255,255,255,0.1); padding-top:20px;">
            <div><small style="color:var(--text-muted);">QUÃNG ĐƯỜNG</small><br><b>{dist:.1f} km</b></div>
            <div><small style="color:var(--text-muted);">HỆ SỐ AI</small><br><b>x{surge:.2f}</b></div>
            <div><small style="color:var(--text-muted);">THỜI GIAN</small><br><b>{int(dist*v['speed'])} phút</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
