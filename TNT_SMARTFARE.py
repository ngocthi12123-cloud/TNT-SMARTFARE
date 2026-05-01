import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
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
# 2. CSS TỐI ƯU GIAO DIỆN (MOBILE & DESKTOP)
# ============================================================
st.markdown("""
<style>
    /* Tổng thể nền và font */
    .stApp {
        background: linear-gradient(180deg, #060b1f 0%, #0a1330 100%);
        color: #f8fafc;
    }
    
    /* Ẩn các thành phần thừa của Streamlit */
    #MainMenu, footer, header, [data-testid="stHeader"] { visibility: hidden; display: none !important; }
    .block-container { padding: 1rem !important; }

    /* Header sang trọng */
    .header-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 20px;
        text-align: center;
    }
    .header-title {
        font-size: 24px;
        font-weight: 800;
        background: linear-gradient(135deg, #f5c842, #ffd86b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Ô nhập liệu dễ nhìn */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 10px !important;
    }
    
    /* Box kết quả tính tiền */
    .result-card {
        background: linear-gradient(135deg, #111c44 0%, #0a1330 100%);
        border-top: 3px solid #f5c842;
        border-radius: 20px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    .price-text {
        font-size: 40px;
        font-weight: 900;
        color: #ffd86b;
        margin: 10px 0;
    }
    
    /* Nút bấm vàng gold */
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #f5c842 0%, #b8860b 100%) !important;
        color: #060b1f !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        height: 50px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. LOGIC TÍNH TOÁN (FUZZY LOGIC)
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
VEHICLES = {
    "Motorbike": {"name": "Xe máy", "base": 12000, "km_rate": 4000, "speed": 2.5},
    "Car4": {"name": "Ô tô 4 chỗ", "base": 25000, "km_rate": 11000, "speed": 2.8},
    "Car7": {"name": "Ô tô 7 chỗ", "base": 32000, "km_rate": 14000, "speed": 3.0}
}

def get_ai_traffic():
    hour = datetime.now().hour + datetime.now().minute / 60.0
    score = (9.5 * math.exp(-pow(hour - 7.5, 2) / 2.88) + 10.0 * math.exp(-pow(hour - 18.0, 2) / 4.5))
    return round(max(1.5, min(10.0, score)), 1)

# ============================================================
# 4. GIAO DIỆN HIỂN THỊ
# ============================================================
st.markdown('<div class="header-box"><div class="header-title">TNT SMARTFARE 💎</div></div>', unsafe_allow_html=True)

# Khởi tạo tọa độ mặc định (Quận 1 và Tân Bình)
start_coords = [10.7769, 106.7009]
end_coords = [10.8231, 106.6297]

col1, col2 = st.columns([1.2, 1], gap="medium")

with col1:
    m = folium.Map(location=start_coords, zoom_start=12, tiles="cartodbpositron")
    folium.Marker(start_coords, tooltip="Điểm đón", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(end_coords, tooltip="Điểm đến", icon=folium.Icon(color="red")).add_to(m)
    
    # Tính khoảng cách
    dist = 0
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full"
        res = requests.get(url, timeout=3).json()
        dist = res['routes'][0]['distance'] / 1000
    except:
        dist = geodesic(start_coords, end_coords).km * 1.2 # Dự phòng nếu lỗi API bản đồ

    st_folium(m, height=400, width="100%")

with col2:
    st.text_input("📍 Điểm đón", value="Quận 1, TP.HCM")
    st.text_input("🏁 Điểm đến", value="Quận Tân Bình, TP.HCM")
    veh_choice = st.selectbox("Chọn loại xe", list(VEHICLES.keys()), format_func=lambda x: VEHICLES[x]['name'])
    is_raining = st.toggle("🌧️ Trời mưa")
    
    # TÍNH GIÁ
    v = VEHICLES[veh_choice]
    traffic_score = get_ai_traffic()
    
    sim.input['distance'] = min(dist, 50)
    sim.input['traffic'] = traffic_score
    sim.input['weather'] = 8 if is_raining else 2
    sim.compute()
    
    surge = 1 + (sim.output['price'] / 100)
    price = round(((v['base'] + dist * v['km_rate']) * surge) / 1000) * 1000
    
    # BOX HIỂN THỊ KẾT QUẢ
    st.markdown(f"""
    <div class="result-card">
        <div style="font-size:14px; color:#94a3b8;">Giá dự kiến (Hệ số x{surge:.2f})</div>
        <div class="price-text">{price:,} VNĐ</div>
        <div style="display:flex; justify-content:space-between; margin-bottom:15px;">
            <span> quãng đường: <b>{dist:.1f} km</b></span>
            <span> thời gian: <b>{int(dist * v['speed'])} phút</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("XÁC NHẬN ĐẶT XE"):
        st.balloons()
        st.success("Đã gửi yêu cầu đặt xe!")

st.markdown("<br><center style='color:#444; font-size:10px;'>TNT SMARTFARE v3.0 - UEH LOGISTICS PROJECT</center>", unsafe_allow_html=True)
