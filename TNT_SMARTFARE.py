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
    "Motorbike": {"icon": "fa-motorcycle",   "name": "Xe máy",       "seats": "1 chỗ",     "base": 12000, "km_rate": 4000,  "speed": 2.5},
    "Car4":      {"icon": "fa-car",          "name": "Ô tô 4 chỗ",   "seats": "4 chỗ",     "base": 25000, "km_rate": 11000, "speed": 2.8},
    "Car7":      {"icon": "fa-van-shuttle",  "name": "Ô tô 7 chỗ",   "seats": "7 chỗ",     "base": 32000, "km_rate": 14000, "speed": 3.0},
    "Luxury":    {"icon": "fa-car-side",     "name": "Luxury Car",   "seats": "4 chỗ VIP", "base": 30000, "km_rate": 13000, "speed": 2.5},
    
}
if 'vehicle' not in st.session_state:
    st.session_state.vehicle = "Motorbike"
def get_automated_demand():
    now = datetime.now()
    hour = now.hour
    minute = now.minute
    time_float = hour + minute / 60.0
    weekday = now.weekday()  # 0 là Thứ 2, 6 là Chủ nhật

    # 1. Giả lập Nhu cầu cơ bản theo giờ (Sử dụng hàm hình chuông - Bell Curve)
    # Cao điểm sáng (7h30) và chiều (17h30)
    morning_peak = 9.0 * np.exp(-((time_float - 7.5)**2) / (2 * 1.5**2))
    evening_peak = 9.5 * np.exp(-((time_float - 17.5)**2) / (2 * 2.0**2))
    
    demand_score = max(morning_peak, evening_peak)

    # 2. Điều chỉnh theo ngày trong tuần
    if weekday >= 5:  # Cuối tuần nhu cầu đi chơi dàn trải hơn
        demand_score = max(demand_score, 7.0 if 10 <= hour <= 21 else 3.0)
    
    # 3. Thêm một chút biến động ngẫu nhiên (Random nhẹ) 
    # Giả lập việc đôi khi có một nhóm sinh viên tan học sớm hoặc sự kiện
    noise = np.random.uniform(-0.5, 0.5)
    
    # Đảm bảo kết quả nằm trong khoảng [1, 10]
    final_demand = round(max(1.0, min(10.0, demand_score + noise)), 1)
    return final_demand

# ============================================================
# 4. FUZZY LOGIC + AI TRAFFIC (ĐÃ FIX GIỜ VN)
# ============================================================
@st.cache_resource
def init_fuzzy():
    distance = ctrl.Antecedent(np.arange(0, 51, 1), 'distance')
    traffic = ctrl.Antecedent(np.arange(0, 11, 1), 'traffic')
    weather = ctrl.Antecedent(np.arange(0, 11, 1), 'weather')
    price = ctrl.Consequent(np.arange(0, 101, 1), 'price')
    demand = ctrl.Antecedent(np.arange(0, 11, 1), 'demand')

    distance.automf(3, names=['short', 'medium', 'long'])
    traffic.automf(3, names=['low', 'medium', 'high'])
    weather['good'] = fuzz.trimf(weather.universe, [0, 0, 5])
    weather['bad'] = fuzz.trimf(weather.universe, [5, 10, 10])
    price.automf(3, names=['low', 'medium', 'high'])
    demand['low'] = fuzz.trapmf(demand.universe, [0, 0, 2, 4])
    demand['medium'] = fuzz.trimf(demand.universe, [3, 5, 7])
    demand['high'] = fuzz.trapmf(demand.universe, [6, 8, 10, 10])

    rules = [
    # Nhóm 1: Ưu tiên giảm giá khi Nhu cầu thấp (Bất kể kẹt xe hay không)
    ctrl.Rule(demand['low'] & (traffic['low'] | traffic['medium']), price['low']),
    ctrl.Rule(demand['low'] & traffic['high'], price['medium']),
    
    # Nhóm 2: Nhu cầu trung bình (Giá ổn định)
    ctrl.Rule(demand['medium'] & traffic['low'], price['low']),
    ctrl.Rule(demand['medium'] & traffic['medium'], price['medium']),
    ctrl.Rule(demand['medium'] & traffic['high'], price['high']),
    
    # Nhóm 3: Nhu cầu cao (Tăng giá mạnh - Giờ cao điểm)
    ctrl.Rule(demand['high'] & traffic['low'], price['medium']),
    ctrl.Rule(demand['high'] & (traffic['medium'] | traffic['high']), price['high']),
    
    # Nhóm 4: Trường hợp đặc biệt (Mưa + Nhu cầu cao = Giá cực cao)
    ctrl.Rule(weather['bad'] & demand['high'], price['high']),
    # Nhóm 5: Sự kết hợp giữa Thời tiết và Giao thông (Cực kỳ quan trọng)
    # Trời mưa + Đường kẹt = Giá cao nhất (để gọi tài xế ra đường)
    ctrl.Rule(weather['bad'] & traffic['high'], price['high']),
    
    # Trời mưa + Nhu cầu trung bình = Giá vẫn nên cao
    ctrl.Rule(weather['bad'] & demand['medium'], price['high']),
    
    # Nhóm 6: Bảo vệ giá khi đường cực vắng
    # Nếu đường rất vắng và nhu cầu cũng thấp thì chắc chắn giá phải rẻ nhất
    ctrl.Rule(traffic['low'] & demand['low'], price['low']),
    
    # Nhóm 7: Luật bù trừ
    # Nếu đường kẹt nhưng nhu cầu cực thấp (ví dụ đêm khuya), giá chỉ nên ở mức trung bình
    ctrl.Rule(traffic['high'] & demand['low'], price['medium'])
]
    return ctrl.ControlSystemSimulation(ctrl.ControlSystem(rules))

sim = init_fuzzy()
geolocator = Nominatim(user_agent="tnt_grab_pro_v6")

# ============================================================
# FIX: AI TRAFFIC THEO GIỜ VIỆT NAM
# ============================================================
def get_address(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), timeout=10)
        return location.address if location else f"{lat:.4f}, {lon:.4f}"
    except Exception:
        return f"{lat:.4f}, {lon:.4f}"

def get_smart_traffic(dist_km, start_coords, end_coords):
    import random
    from datetime import datetime
    import math

    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()  # 0=Mon

    # =========================
    # 1. BASE THEO GIỜ
    # =========================
    # =========================
    # 1. BASE THEO GIỜ (Cập nhật mới)
    # =========================
    if 7 <= hour <= 9:
        base = 7.5
    elif 11 <= hour <= 13:
        base = 5.5
    elif 14 <= hour <= 16:
        base = 4.0
    elif 17 <= hour <= 19:
        base = 8.0 # Cao điểm gắt
    elif 19 < hour <= 21:
        base = 6.3
    elif 22 <= hour or hour <= 4:
        base = 1.5
    else:
        base = 4.5

    # =========================
    # 2. THEO NGÀY
    # =========================
    if weekday >= 5:  # cuối tuần
        if 9 <= hour <= 21:
            base += 1.0
        else:
            base -= 0.5

    
    # =========================
    # 3. THEO KHOẢNG CÁCH (Chỉnh lại: Khoảng cách xa không nên làm tăng mật độ)
    # =========================
    # Mật độ giao thông thường phụ thuộc vào địa điểm hơn là tổng quãng đường.
    # Nên giảm bớt trọng số này.
    if dist_km > 15:
        base += 0.5 
    elif dist_km < 2:
        base -= 0.5

    # =========================
    # 4. HIỆU ỨNG TRUNG TÂM TP (Quận 1) - Tối ưu lại
    # =========================
    center = (10.7769, 106.7009)
    def calc_distance(a, b):
        return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

    d_start = calc_distance(start_coords, center)
    d_end = calc_distance(end_coords, center)

    # Thay vì cộng 0.7, hãy dùng hệ số để giá trị không bị vọt quá cao
    if d_start < 0.05 or d_end < 0.05:
        # Giới hạn: Nếu đã là giờ cao điểm (7.5) thì chỉ tăng nhẹ
        if base >= 7.0:
            base += 0.3 
        else:
            base += 0.7

    # =========================
    # 5. THỜI TIẾT
    # =========================
    if st.session_state.get("rain_toggle", False):
        base += 1.5

    # =========================
    # 6. RANDOM THÔNG MINH
    # =========================
    noise = random.uniform(-0.8, 0.8)

    traffic = base + noise

    return round(min(10, max(1, traffic)), 1)


# ============================================================
# 5. SESSION (GIỮ NGUYÊN)
# ============================================================

if 'start_coords' not in st.session_state: st.session_state.start_coords = [10.7769, 106.7009]
if 'end_coords' not in st.session_state: st.session_state.end_coords = [10.8231, 106.6297]
if 'start_addr' not in st.session_state: st.session_state.start_addr = "Quận 1, TP.HCM"
if 'end_addr' not in st.session_state: st.session_state.end_addr = "Quận Tân Bình, TP.HCM"
if 'vehicle' not in st.session_state: st.session_state.vehicle = "Luxury"
dist = 0
try:
    # Key API GraphHopper của bạn
    url = f"https://graphhopper.com/api/1/route?point={st.session_state.start_coords[0]},{st.session_state.start_coords[1]}&point={st.session_state.end_coords[0]},{st.session_state.end_coords[1]}&vehicle=car&key=79ebf81c-8a0b-4e39-8f89-f7805f154c98"
    res = requests.get(url).json()
    if "paths" in res:
        dist = res["paths"][0]["distance"] / 1000 # Đổi sang km
except:
    dist = 0 # Nếu lỗi thì mặc định là 0
# ============================================================
# 6. HERO HEADER (ĐÃ FIX GIỜ VN)
# ============================================================

auto_tf = get_smart_traffic(
    dist,
    st.session_state.start_coords,
    st.session_state.end_coords
)
current_time = datetime.now().strftime("%H:%M")
# Bước 2: AI tự động tính toán nhu cầu khách hàng theo giờ
auto_demand = get_automated_demand()

# Bước 3: Lấy thời gian hiện tại để hiển thị lên giao diện
current_time = datetime.now().strftime("%H:%M")

# Bước 4: Nạp tất cả vào "Bộ não" Logic mờ để tính toán
sim.input['traffic'] = auto_tf
sim.input['demand'] = auto_demand
# Nếu bạn có nút check mưa, hãy thay True/False vào đây
sim.input['weather'] = 8 if st.session_state.get('is_raining', False) else 2

sim.compute()

# Bước 5: Tính toán hệ số biến động giá (Surge)
# 0.7 là mức tối thiểu (Giảm giá 30% khi vắng khách)
surge = 0.8 + (sim.output['price'] / 120)
surge = min(1.5, surge)
sim.compute()
v = VEHICLES[st.session_state.vehicle]
    # Công thức chuẩn giống Grab
if dist <= 2:
    total = v['base']
else:
    total = v['base'] + (dist - 2) * v['km_rate']

# Áp dụng surge
    total *= surge
# làm tròn đẹp
final_price = max(0, round(total / 1000) * 1000)

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
# ============================================================
# 7. LAYOUT CHÍNH
# ============================================================
if 'dist' not in locals(): dist = 0
col_map, col_ctrl = st.columns([2.2, 1], gap="medium")

with col_ctrl:
    st.markdown('<div class="panel-title"><i class="fa-solid fa-route"></i> Lộ trình của bạn</div>', unsafe_allow_html=True)
    with st.container(border=True):
        s_input = st.text_input("📍 Điểm đón", value=st.session_state.start_addr, key="s_in")
        e_input = st.text_input("🏁 Điểm đến", value=st.session_state.end_addr, key="e_in")

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("Tìm địa chỉ", use_container_width=True, key="search_btn"):
                try:
                    l1 = geolocator.geocode(s_input)
                    l2 = geolocator.geocode(e_input)
                    if l1:
                        st.session_state.start_coords = [l1.latitude, l1.longitude]
                        st.session_state.start_addr = l1.address
                    if l2:
                        st.session_state.end_coords = [l2.latitude, l2.longitude]
                        st.session_state.end_addr = l2.address
                    st.rerun()
                except Exception:
                    st.warning("Không tìm được địa chỉ.")
        with col_b2:
            if st.button("Reset Map", use_container_width=True, type="secondary", key="reset_btn"):
                st.session_state.start_coords = [10.7769, 106.7009]
                st.session_state.end_coords = [10.8231, 106.6297]
                st.rerun()

    st.markdown('<div class="panel-title" style="margin-top:18px;"><i class="fa-solid fa-car-rear"></i> Chọn phương tiện</div>', unsafe_allow_html=True)
    with st.container(border=True):
        veh_keys = list(VEHICLES.keys())
        idx = veh_keys.index(st.session_state.vehicle) if st.session_state.vehicle in veh_keys else 0
        chosen = st.radio(
            "Loại xe",
            options=veh_keys,
            format_func=lambda x: f"{VEHICLES[x]['name']} · {VEHICLES[x]['seats']}",
            index=idx,
            label_visibility="collapsed",
            key="vehicle_radio"
        )
        st.session_state.vehicle = chosen

        v_info = VEHICLES[chosen]
        st.markdown(f'<div style="display:flex;align-items:center;gap:14px;padding:14px;background:rgba(245,200,66,0.08);border:1px solid rgba(245,200,66,0.3);border-radius:14px;margin-top:10px;"><div style="width:50px;height:50px;border-radius:12px;background:rgba(245,200,66,0.15);display:flex;align-items:center;justify-content:center;"><i class="fa-solid {v_info["icon"]}" style="font-size:24px;color:#ffd86b;"></i></div><div><div style="color:#ffd86b;font-weight:700;font-size:15px;">{v_info["name"]}</div><div style="color:#94a3b8;font-size:12px;">Mở cửa: {v_info["base"]:,}đ • Mỗi km: {v_info["km_rate"]:,}đ</div></div></div>', unsafe_allow_html=True)


    st.markdown('<div class="panel-title" style="margin-top:18px;"><i class="fa-solid fa-sliders"></i> Tùy chọn & Ưu đãi</div>', unsafe_allow_html=True)
    with st.container(border=True):
        is_raining = st.toggle("🌧️ Đang có mưa/bão", value=False, key="rain_toggle")

        promo_code = st.text_input("🎟️ Mã giảm giá", placeholder="Nhập mã giảm giá", key="promo").upper()
        discount_val = 0
        if promo_code == "UEH":
            st.success("✅ Mã UEH: Giảm 20.000đ")
            discount_val = 20000
        elif promo_code == "LUONGVE":
            st.success("✅ Mã LUONGVE: Giảm 10%")
        elif promo_code != "":
            st.warning("⚠️ Mã không hợp lệ.")
with col_map:
    st.markdown('<div class="panel-title"><i class="fa-solid fa-map-location-dot"></i> Bản đồ trực tiếp</div>', unsafe_allow_html=True)
    
    # Khởi tạo bản đồ
    m = folium.Map(
        location=st.session_state.start_coords,
        zoom_start=13,
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google Maps"
    )

    # Thêm Marker
    folium.Marker(st.session_state.start_coords, tooltip="Điểm đón", icon=folium.Icon(color='green', icon='play', prefix='fa')).add_to(m)
    folium.Marker(st.session_state.end_coords, tooltip="Điểm đến", icon=folium.Icon(color='red', icon='flag-checkered', prefix='fa')).add_to(m)

    # TÍNH TOÁN LỘ TRÌNH VỚI GRAPHHOPPER
    dist = 0
    p1, p2 = st.session_state.start_coords, st.session_state.end_coords
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{p1[1]},{p1[0]};{p2[1]},{p2[0]}?overview=full&geometries=geojson"
        res = requests.get(url, timeout=10).json()
        if 'routes' in res and len(res['routes']) > 0:
            route = res['routes'][0]
            dist = route['distance'] / 1000
            coords = [(p[1], p[0]) for p in route['geometry']['coordinates']]
            folium.PolyLine(coords, color="#ffd86b", weight=4, opacity=0.95).add_to(m)
            m.fit_bounds([p1, p2])
    except Exception:
        pass

    # HIỂN THỊ BẢN ĐỒ (Quan trọng: width=None để nó tự fill khung CSS)
    st.markdown('<div class="map-wrap">', unsafe_allow_html=True)
    map_output = st_folium(m, height=500, width=None, key="tnt_map")
    st.markdown('</div>', unsafe_allow_html=True)

    # XỬ LÝ CLICK CHUỘT (Sửa lỗi loop)
def get_address(lat, lon):
    try:
        # Thêm country_codes để giới hạn phạm vi tìm kiếm tại Việt Nam
        location = geolocator.reverse((lat, lon), timeout=10, language='vi')
        return location.address if location else f"{lat:.4f}, {lon:.4f}"
    except Exception:
        return f"{lat:.4f}, {lon:.4f}"

# 2. KIỂM TRA CLICK CHUỘT THÔNG MINH (TRÁNH RERUN VÔ TẬN)
if map_output and map_output.get('last_object_clicked'):
    click_c = [map_output['last_object_clicked']['lat'], map_output['last_object_clicked']['lng']]
    
    # Tính khoảng cách Euclidean đơn giản để xem người dùng có thực sự muốn đổi điểm không
    d_start = math.sqrt((click_c[0]-st.session_state.start_coords[0])**2 + (click_c[1]-st.session_state.start_coords[1])**2)
    d_end = math.sqrt((click_c[0]-st.session_state.end_coords[0])**2 + (click_c[1]-st.session_state.end_coords[1])**2)
    
    threshold = 0.0001 # Một khoảng cách rất nhỏ
    if d_start > threshold and d_end > threshold:
        if d_start < d_end:
            st.session_state.start_coords = click_c
            st.session_state.start_addr = get_address(click_c[0], click_c[1])
        else:
            st.session_state.end_coords = click_c
            st.session_state.end_addr = get_address(click_c[0], click_c[1])
        st.rerun()
# ============================================================
# 8. TÍNH GIÁ + RESULT CARD
# ============================================================
# --- ĐOẠN TÍNH TOÁN VÀ HIỂN THỊ KẾT QUẢ ---
if dist > 0:
    base_fare = v['base'] if dist <= 2 else v['base'] + (dist - 2) * v['km_rate']
    # Surge chuẩn từ 1.0 đến 1.8 tùy vào kết quả AI
    ai_surge = 1.0 + (sim.output['price'] / 100) * 0.8 
    
    total = base_fare * ai_surge
    current_discount = st.session_state.get('discount_value', 0)
    # Áp dụng mã giảm giá cuối cùng
    if promo_code == "LUONGVE":
        total *= 0.9
    else:
        total -= current_discount


    final_price = max(0, round(total / 1000) * 1000)
    eta = max(1, int(dist * v['speed']))
    
    weather_icon = "fa-cloud-showers-heavy" if is_raining else "fa-sun"
    weather_text = "Mưa/Bão" if is_raining else "Trời tốt"
    promo_display = promo_code if promo_code else "Không có"
    st.markdown(f"""
    <div class="result-shell">
      <div class="result-grid">
        <div>
          <span class="ai-pill"><i class="fa-solid fa-microchip"></i> AI ANALYSIS · MẬT ĐỘ {auto_tf}/10 · HỆ SỐ x{surge:.2f}</span>
          <div class="price-label">Tổng cước phí dự kiến</div>
          <div class="price-mega">{final_price:,}<span class="price-currency">VNĐ</span></div>
        </div>
      </div>
      <div class="meta-row">
        <div class="meta-item">
          <div class="meta-icon"><i class="fa-solid {v['icon']}"></i></div>
          <div class="meta-text"><div class="lbl">Phương tiện</div><div class="val">{v['name']}</div></div>
        </div>
        <div class="meta-item">
          <div class="meta-icon"><i class="fa-solid fa-route"></i></div>
          <div class="meta-text"><div class="lbl">Quãng đường</div><div class="val">{dist:.1f} km</div></div>
        </div>
        <div class="meta-item">
          <div class="meta-icon"><i class="fa-regular fa-clock"></i></div>
          <div class="meta-text"><div class="lbl">Thời gian</div><div class="val">{eta} phút</div></div>
        </div>
        <div class="meta-item">
          <div class="meta-icon"><i class="fa-solid {weather_icon}"></i></div>
          <div class="meta-text"><div class="lbl">Thời tiết</div><div class="val">{weather_text}</div></div>
        </div>
        <div class="meta-item">
          <div class="meta-icon"><i class="fa-solid fa-ticket"></i></div>
          <div class="meta-text"><div class="lbl">Mã ưu đãi</div><div class="val">{promo_display}</div></div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-top: 20px;">
        <button class="confirm-btn" style="width: 100%; justify-content: center;">
            <i class="fa-solid fa-check-double"></i> XÁC NHẬN ĐẶT XE
        </button>
    </div>
""", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-state">
      <i class="fa-solid fa-location-crosshairs"></i>
      <h3>Chào mừng đến với TNT SMARTFARE 💎</h3>
      <p>Hãy kéo Marker trên bản đồ hoặc nhập địa chỉ điểm đón và điểm đến để bắt đầu tính cước phí thông minh.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 9. FOOTER
# ============================================================
st.markdown("""
<div style="text-align:center; margin-top:40px; padding:20px; color:#94a3b8; font-size:12px; letter-spacing:1px;">
  <i class="fa-solid fa-gem" style="color:#f5c842;"></i>
  &nbsp; TNT SMARTFARE · POWERED BY FUZZY LOGIC &nbsp;·&nbsp; © 2026
</div>
""", unsafe_allow_html=True)
