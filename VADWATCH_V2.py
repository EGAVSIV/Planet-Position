# ================= IMPORTS =================
import streamlit as st
import swisseph as swe
import datetime
import pytz
import math
import pandas as pd
from collections import defaultdict
import hashlib
from streamlit_autorefresh import st_autorefresh

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
LAT, LON = 19.07598, 72.87766
FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
swe.set_sid_mode(swe.SIDM_LAHIRI)

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
    nak = 13 + 1/3
    pada = nak / 4
    i = int(lon // nak) % 27
    p = int((lon % nak) // pada) + 1
    return NAKSHATRAS[i][0], NAKSHATRAS[i][1], p

def get_positions(dt_utc):
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute/60)

    pos, retro = {}, {}
    ay = swe.get_ayanamsa_ut(jd)

    for name, code, sym in PLANETS:
        r, _ = swe.calc_ut(jd, code)
        pos[name] = (r[0] - ay) % 360
        retro[name] = r[3] < 0

    pos["केतु"] = (pos["राहु"] + 180) % 360
    retro["केतु"] = retro["राहु"]

    return pos, retro, jd

# ================= UI INPUT =================
st.title("🪐 वेदिक ग्रह घड़ी — Drik Panchang")

c1, c2, c3 = st.columns(3)
today = datetime.date.today()

date = c1.date_input("तारीख़", today)
time_ = c2.time_input("समय")

if c3.button("अब"):
    now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    date, time_ = now.date(), now.time()

ist = pytz.timezone("Asia/Kolkata")
dt_ist = ist.localize(datetime.datetime.combine(date, time_))
dt_utc = dt_ist.astimezone(pytz.utc)

# ================= CORE CALCULATION (IMPORTANT) =================
pos, retro, jd = get_positions(dt_utc)

ascmc, _ = swe.houses_ex(jd, LAT, LON, b'P', FLAGS)
lagna_deg = ascmc[0] % 360
lagna_sign = SIGNS[int(lagna_deg // 30)]

# ================= LAYOUT =================
left, right = st.columns([2,1])

with right:
    st.subheader("🌙 ज्योतिष सार")
    moon_nak, moon_lord, moon_pada = nakshatra_pada(pos["चन्द्र"])

    st.table(pd.DataFrame([
        ["चन्द्र नक्षत्र", moon_nak],
        ["नक्षत्र पद", moon_pada],
        ["नक्षत्र स्वामी", moon_lord],
        ["लग्न", lagna_sign],
        ["लग्न अंश", f"{lagna_deg:.2f}°"],
        ["समय (IST)", dt_ist.strftime("%d-%b-%Y %H:%M")]
    ], columns=["तत्व","मान"]))

    st.subheader("🪐 ग्रह स्थिति")
    rows = []

    for p, c, s in PLANETS:
        nak, lord, pada = nakshatra_pada(pos[p])
        rows.append([p, f"{pos[p]:.2f}°", SIGNS[int(pos[p]//30)],
                     f"{nak} (पद {pada})",
                     "🔁 वक्री" if retro[p] else "➡️ मार्गी"])

    nak, lord, pada = nakshatra_pada(pos["केतु"])
    rows.append(["केतु", f"{pos['केतु']:.2f}°",
                 SIGNS[int(pos["केतु"]//30)],
                 f"{nak} (पद {pada})",
                 "🔁 वक्री"])

    st.table(pd.DataFrame(rows,
             columns=["ग्रह","डिग्री","राशि","नक्षत्र","स्थिति"]))

with st.sidebar:
    live = st.toggle("Enable Live Clock")

if live:
    st_autorefresh(interval=1000, key="clock")

st.success("IST समय: " + dt_ist.strftime("%d-%b-%Y %H:%M:%S"))

st.markdown("""
---
### *Gaurav Singh Yadav*
**Quant Trader | Energy & Commodity Intelligence**
""")
