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

# ... (PHẦN CSS GIỮ NGUYÊN, KHÔNG ĐỔI)

# ============================================================
# 3. DỮ LIỆU XE (GIỮ NGUYÊN)
# ============================================================

# ... (VEHICLES giữ nguyên)

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
