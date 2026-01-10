import streamlit as st
import swisseph as swe
import datetime, pytz, math
import pandas as pd
from collections import defaultdict
import hashlib

# ================= LOGIN =================
def hash_pwd(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

USERS = st.secrets["users"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Login Required")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u in USERS and hash_pwd(p) == USERS[u]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="🪐 वेदिक ग्रह घड़ी — Drik Panchang",
    layout="wide",
    page_icon="🪐"
)

# ================= ASTRO CONFIG =================
LAT, LON = 19.07598, 72.87766
FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
swe.set_sid_mode(swe.SIDM_LAHIRI)

# ================= SESSION DEFAULTS =================
if "sel_date" not in st.session_state:
    st.session_state.sel_date = datetime.date.today()

if "sel_time" not in st.session_state:
    st.session_state.sel_time = datetime.datetime.now(
        pytz.timezone("Asia/Kolkata")
    ).time()

# ================= DATA =================
SIGNS = ["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या",
         "तुला","वृश्चिक","धनु","मकर","कुंभ","मीन"]

NAKSHATRAS = [
("अश्विनी","केतु"),("भरणी","शुक्र"),("कृत्तिका","सूर्य"),
("रोहिणी","चन्द्र"),("मृगशिरा","मंगल"),("आर्द्रा","राहु"),
("पुनर्वसु","बृहस्पति"),("पुष्य","शनि"),("आश्लेषा","बुध"),
("मघा","केतु"),("पूर्व फाल्गुनी","शुक्र"),("उत्तर फाल्गुनी","सूर्य"),
("हस्त","चन्द्र"),("चित्रा","मंगल"),("स्वाति","राहु"),
("विशाखा","बृहस्पति"),("अनुराधा","शनि"),("ज्येष्ठा","बुध"),
("मूला","केतु"),("पूर्वाषाढा","शुक्र"),("उत्तराषाढा","सूर्य"),
("श्रवण","चन्द्र"),("धनिष्ठा","मंगल"),("शतभिषा","राहु"),
("पूर्वभाद्रपदा","बृहस्पति"),("उत्तरभाद्रपदा","शनि"),("रेवती","बुध")
]

PLANETS = [
("सूर्य", swe.SUN, "सू."),
("चन्द्र", swe.MOON,"च."),
("मंगल", swe.MARS,"मं."),
("बुध", swe.MERCURY,"बु."),
("बृहस्पति", swe.JUPITER,"बृह"),
("शुक्र", swe.VENUS,"शु"),
("शनि", swe.SATURN,"शनि"),
("राहु", swe.MEAN_NODE,"रा.")
]

# ================= FUNCTIONS =================
def nakshatra_pada(lon):
    size = 13 + 1/3
    pada = size / 4
    idx = int(lon // size) % 27
    pad = int((lon % size) // pada) + 1
    return NAKSHATRAS[idx][0], NAKSHATRAS[idx][1], pad

def get_positions(dt_utc):
    jd = swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute/60
    )

    pos, retro = {}, {}
    ay = swe.get_ayanamsa_ut(jd)

    for name, code, sym in PLANETS:
        r, _ = swe.calc_ut(jd, code)
        pos[name] = (r[0] - ay) % 360
        retro[name] = r[3] < 0

    pos["केतु"] = (pos["राहु"] + 180) % 360
    retro["केतु"] = retro["राहु"]

    return pos, retro, jd

# ================= MINI LIVE CLOCK =================
def generate_mini_clock():
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.datetime.now(ist)
    pos, retro, _ = get_positions(now_ist.astimezone(pytz.utc))

    cx, cy = 150, 150
    R = 85

    svg = f"""
    <svg width="260" height="260" viewBox="0 0 300 300">
        <circle cx="{cx}" cy="{cy}" r="140" fill="#050b18" stroke="#3fa9f5" stroke-width="4"/>
        <circle cx="{cx}" cy="{cy}" r="110" fill="none" stroke="#88c9ff" stroke-width="2"/>
    """

    for i in range(12):
        a = math.radians(90 - i*30)
        x = cx + 110*math.cos(a)
        y = cy - 110*math.sin(a)
        svg += f"<line x1='{cx}' y1='{cy}' x2='{x}' y2='{y}' stroke='#ffd700'/>"

    for name, code, sym in PLANETS:
        a = math.radians(90 - pos[name])
        px = cx + R*math.cos(a)
        py = cy - R*math.sin(a)
        color = "#ff4d4d" if retro[name] else "#79e887"
        svg += f"<circle cx='{px}' cy='{py}' r='6' fill='{color}'/>"
        svg += f"<text x='{px}' y='{py+2}' font-size='7' text-anchor='middle'>{sym}</text>"

    svg += "</svg>"
    return svg, now_ist

# ================= MAIN CLOCK SVG =================
def generate_svg(pos, retro):
    cx, cy = 350, 350
    svg = f"""
    <svg width="700" height="700" viewBox="0 0 700 700">
    <defs>
        <radialGradient id="g">
            <stop offset="70%" stop-color="#0a1e3a"/>
            <stop offset="100%" stop-color="#3fa9f5"/>
        </radialGradient>
    </defs>
    <circle cx="{cx}" cy="{cy}" r="330" fill="url(#g)"/>
    <circle cx="{cx}" cy="{cy}" r="270" fill="#050b18" stroke="#88c9ff" stroke-width="3"/>
    """

    for i in range(12):
        a = math.radians(90 - i*30)
        svg += f"<line x1='{cx}' y1='{cy}' x2='{cx+260*math.cos(a)}' y2='{cy-260*math.sin(a)}' stroke='#ffd700'/>"

    for i in range(12):
        a = math.radians(90 - (i*30+15))
        svg += f"<text x='{cx+210*math.cos(a)}' y='{cy-210*math.sin(a)}' fill='#00e6ff' font-size='22' text-anchor='middle'>{SIGNS[i]}</text>"

    groups = defaultdict(list)
    for n,_,s in PLANETS:
        groups[int(pos[n]//30)].append((n,s))
    groups[int(pos["केतु"]//30)].append(("केतु","के."))

    for r, plist in groups.items():
        a = math.radians(90 - (r*30+15))
        for i,(n,s) in enumerate(plist):
            rr = 200 - i*18
            x = cx + rr*math.cos(a)
            y = cy - rr*math.sin(a)
            col = "#ff4d4d" if retro.get(n,False) else "#79e887"
            svg += f"<circle cx='{x}' cy='{y}' r='11' fill='{col}'/>"
            svg += f"<text x='{x}' y='{y}' font-size='11' text-anchor='middle'>{s}</text>"

    svg += "</svg>"
    return svg

# ================= UI =================
st.title("🪐 वेदिक ग्रह घड़ी — Drik Panchang")

c1,c2,c3 = st.columns(3)
date = c1.date_input("तारीख़", st.session_state.sel_date)
time_sel = c2.time_input("समय", st.session_state.sel_time)

if c3.button("अब"):
    now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    st.session_state.sel_date = now.date()
    st.session_state.sel_time = now.time()
    st.rerun()

dt_ist = pytz.timezone("Asia/Kolkata").localize(
    datetime.datetime.combine(date, time_sel)
)
pos, retro, jd = get_positions(dt_ist.astimezone(pytz.utc))

left,right = st.columns([2,1])
with left:
    st.components.v1.html(generate_svg(pos, retro), height=720)

with st.sidebar:
    st.markdown("### ⏱️ Live Planet Clock")
    live = st.toggle("Enable Live Clock", False)

if live:
    st.autorefresh(interval=1000, key="clock")
    svg, now = generate_mini_clock()
    st.markdown(f"""
    <div style="position:fixed;bottom:20px;right:20px;
         width:260px;height:260px;border-radius:50%;
         background:#050b18;border:3px solid #3fa9f5;
         box-shadow:0 0 25px rgba(63,169,245,0.6);z-index:9999">
         {svg}
    </div>
    """, unsafe_allow_html=True)
    st.caption("Live IST: " + now.strftime("%H:%M:%S"))

st.success("IST समय: " + dt_ist.strftime("%d-%b-%Y %H:%M:%S"))

st.markdown("""
---
### *Gaurav Singh Yadav*  
**Quant Trader | Energy & Commodity Intelligence**  
📧 yadav.gauravsingh@gmail.com  
<sub>Built with ❤️ using Swiss Ephemeris & Streamlit</sub>
""")
