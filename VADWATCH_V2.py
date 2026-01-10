# ================= IMPORTS =================
import streamlit as st
import swisseph as swe
import datetime
import pytz
import math
import pandas as pd
from collections import defaultdict
import hashlib

# ================= PAGE CONFIG (MUST BE FIRST) =================
st.set_page_config(
    page_title="🪐 वेदिक ग्रह घड़ी — Drik Panchang",
    layout="wide",
    page_icon="🪐"
)

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

# ================= CONFIG =================
LAT, LON = 19.07598, 72.87766  # Mumbai
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
    ("चन्द्र", swe.MOON, "च."),
    ("मंगल", swe.MARS, "मं."),
    ("बुध", swe.MERCURY, "बु."),
    ("बृहस्पति", swe.JUPITER, "बृह"),
    ("शुक्र", swe.VENUS, "शु"),
    ("शनि", swe.SATURN, "शनि"),
    ("राहु", swe.MEAN_NODE, "रा.")
]

# ================= FUNCTIONS =================
def nakshatra_pada(lon):
    nak_size = 13 + 1/3
    pada_size = nak_size / 4
    idx = int(lon // nak_size) % 27
    pada = int((lon % nak_size) // pada_size) + 1
    return NAKSHATRAS[idx][0], NAKSHATRAS[idx][1], pada

def get_positions(dt_utc):
    jd = swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60
    )

    pos, retro = {}, {}
    ay = swe.get_ayanamsa_ut(jd)

    for name, code, sym in PLANETS:
        r, _ = swe.calc_ut(jd, code)
        lon = (r[0] - ay) % 360
        pos[name] = lon
        retro[name] = r[3] < 0

    pos["केतु"] = (pos["राहु"] + 180) % 360
    retro["केतु"] = retro["राहु"]

    return pos, retro, jd

def generate_mini_clock():
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.datetime.now(ist)
    now_utc = now_ist.astimezone(pytz.utc)

    pos, retro, _ = get_positions(now_utc)

    cx, cy = 150, 150
    BASE_R = 85

    svg = f"""
    <svg width="300" height="300" viewBox="0 0 300 300">
        <circle cx="{cx}" cy="{cy}" r="140" fill="#050b18" stroke="#3fa9f5" stroke-width="4"/>
        <circle cx="{cx}" cy="{cy}" r="110" fill="none" stroke="#88c9ff" stroke-width="2"/>
    """

    for i in range(12):
        ang = math.radians(90 - i * 30)
        x = cx + 110 * math.cos(ang)
        y = cy - 110 * math.sin(ang)
        svg += f"<line x1='{cx}' y1='{cy}' x2='{x}' y2='{y}' stroke='#ffd700'/>"

    for name, code, sym in PLANETS:
        ang = math.radians(90 - pos[name])
        px = cx + BASE_R * math.cos(ang)
        py = cy - BASE_R * math.sin(ang)
        color = "#ff4d4d" if retro.get(name) else "#79e887"

        svg += f"""
        <circle cx="{px}" cy="{py}" r="6" fill="{color}"/>
        <text x="{px}" y="{py+2}" font-size="7" text-anchor="middle" fill="black">{sym}</text>
        """

    svg += "</svg>"
    return svg, now_ist

def generate_svg(pos, retro):
    cx, cy = 350, 350
    svg = f'<svg width="700" height="700" viewBox="0 0 700 700">'

    svg += f'<circle cx="{cx}" cy="{cy}" r="330" fill="#0a1e3a"/>'
    svg += f'<circle cx="{cx}" cy="{cy}" r="270" fill="#050b18" stroke="#88c9ff" stroke-width="3"/>'

    for i in range(12):
        ang = math.radians(90 - i * 30)
        x = cx + 260 * math.cos(ang)
        y = cy - 260 * math.sin(ang)
        svg += f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" stroke="#ffd700" stroke-width="2"/>'

    for i in range(12):
        ang = math.radians(90 - (i * 30 + 15))
        x = cx + 210 * math.cos(ang)
        y = cy - 210 * math.sin(ang)
        svg += f'<text x="{x}" y="{y}" fill="#00e6ff" font-size="22" text-anchor="middle">{SIGNS[i]}</text>'

    groups = defaultdict(list)
    for name, code, sym in PLANETS:
        groups[int(pos[name] // 30)].append((name, sym))

    groups[int(pos["केतु"] // 30)].append(("केतु", "के."))

    for rashi, plist in groups.items():
        ang = math.radians(90 - (rashi * 30 + 15))
        for i, (name, sym) in enumerate(plist):
            r = 200 - i * 18
            px = cx + r * math.cos(ang)
            py = cy - r * math.sin(ang)
            color = "#ff4d4d" if retro.get(name) else "#79e887"

            svg += f'''
            <circle cx="{px}" cy="{py}" r="11" fill="{color}"/>
            <text x="{px}" y="{py}" font-size="11" text-anchor="middle" dominant-baseline="middle">{sym}</text>
            '''

    svg += "</svg>"
    return svg

# ================= UI =================
st.title("🪐 वेदिक ग्रह घड़ी — Drik Panchang")

c1, c2, c3 = st.columns(3)
today = datetime.date.today()

date = c1.date_input(
    "तारीख़",
    value=st.session_state.sel_date,
    min_value=today - datetime.timedelta(days=365*500),
    max_value=today + datetime.timedelta(days=365*500)
)

sel_time = c2.time_input("समय", value=st.session_state.sel_time)

if c3.button("अब"):
    now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    st.session_state.sel_date = now.date()
    st.session_state.sel_time = now.time()
    st.rerun()

ist = pytz.timezone("Asia/Kolkata")
dt_ist = ist.localize(datetime.datetime.combine(date, sel_time))
dt_utc = dt_ist.astimezone(pytz.utc)

pos, retro, jd = get_positions(dt_utc)

ascmc, _ = swe.houses_ex(jd, LAT, LON, b'P', FLAGS)
lagna_deg = ascmc[0] % 360
lagna_sign = SIGNS[int(lagna_deg // 30)]

left, right = st.columns([2, 1])

with left:
    st.components.v1.html(generate_svg(pos, retro), height=720)

with right:
    moon_nak, moon_lord, moon_pada = nakshatra_pada(pos["चन्द्र"])
    st.table(pd.DataFrame([
        ["चन्द्र नक्षत्र", moon_nak],
        ["नक्षत्र पद", moon_pada],
        ["नक्षत्र स्वामी", moon_lord],
        ["लग्न", lagna_sign],
        ["लग्न अंश", f"{lagna_deg:.2f}°"],
        ["समय (IST)", dt_ist.strftime("%d-%b-%Y %H:%M")]
    ], columns=["तत्व", "मान"]))

with st.sidebar:
    live_clock_on = st.toggle("Enable Live Clock", value=False)

if live_clock_on:
    st.autorefresh(interval=1000, key="live_clock")
    svg, now_ist = generate_mini_clock()
    st.components.v1.html(svg, height=300)
    st.caption("Live IST: " + now_ist.strftime("%H:%M:%S"))

st.success("IST समय: " + dt_ist.strftime("%d-%b-%Y %H:%M:%S"))

st.markdown("""
---
### *Gaurav Singh Yadav*  
**Quant Trader | Energy & Commodity Intelligence**  
📧 yadav.gauravsingh@gmail.com  
<sub>Built with ❤️ using Swiss Ephemeris & Streamlit</sub>
""")
