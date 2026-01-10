import streamlit as st
import swisseph as swe
import datetime, pytz, math
import pandas as pd
from collections import defaultdict
import hashlib
from streamlit_autorefresh import st_autorefresh


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
st.set_page_config(
    page_title="🪐 वेदिक ग्रह घड़ी — Drik Panchang",
    layout="wide",
    page_icon="🪐"
)

# ================= ROTATING QUOTES =================
QUOTES = [
    "भीड़ में सब लोग अच्छे नहीं होते और अच्छे लोगों की कभी भीड़ नहीं होती",
    "हमारी समस्या का समाधान सिर्फ हमारे पास है, दूसरों के पास तो सिर्फ सुझाव है",
    "जब तक तुम्हारे पास पैसा है तब तक दुनिया पूछेगी भाई तू कैसा है",
    "कोई काम तब तक ही असंभव लगता है जब तक कि वह हो नहीं जाता",
    "आपकी किस्मत आपको मौका देगी पर आपकी मेहनत सब को चौंका देगी",
    "ना किसी से ईर्ष्या ना किसी से होड़, मेरी अपनी मंजिल मेरी अपनी दौड़",
    "काम ऐसा करो कि नाम हो जाए या फिर नाम ऐसा करो कि काम हो जाए",
    "याद रखना कमजोर हम नहीं हमारा वक्त है। हम जब भी उठेंगे तूफान बन कर उड़ेंगे।",
    "मेहनत इंसान को मजबूत बनाता है फिर चाहे वह इंसान कितना भी कमजोर क्यों न हो",
    "अगर आप उस इंसान की तलाश में हैं जो आपकी जिंदगी बदलेगा तो आइना देख ले"
]

if "quote_index" not in st.session_state:
    st.session_state.quote_index = 0

# ================= LOCATION DATA =================
LOCATIONS = {
    "Andhra Pradesh – Amaravati": (16.5412, 80.5154),
    "Assam – Dispur": (26.1445, 91.7362),
    "Bihar – Patna": (25.5941, 85.1376),
    "Gujarat – Gandhinagar": (23.2156, 72.6369),
    "Haryana – Chandigarh": (30.7333, 76.7794),
    "Karnataka – Bengaluru": (12.9716, 77.5946),
    "Kerala – Thiruvananthapuram": (8.5241, 76.9366),
    "Madhya Pradesh – Bhopal": (23.2599, 77.4126),
    "Maharashtra – Mumbai": (19.0760, 72.8777),
    "Odisha – Bhubaneswar": (20.2961, 85.8245),
    "Punjab – Chandigarh": (30.7333, 76.7794),
    "Rajasthan – Jaipur": (26.9124, 75.7873),
    "Tamil Nadu – Chennai": (13.0827, 80.2707),
    "Telangana – Hyderabad": (17.3850, 78.4867),
    "Uttar Pradesh – Lucknow": (26.8467, 80.9462),
    "West Bengal – Kolkata": (22.5726, 88.3639),
}
with st.sidebar:
    # ================= LOCATION =================
    st.markdown("### 📍 स्थान चयन (Location)")

    selected_location = st.selectbox(
        "राज्य / राजधानी चुनें",
        list(LOCATIONS.keys()),
        index=list(LOCATIONS.keys()).index("Maharashtra – Mumbai")
    )

    LAT, LON = LOCATIONS[selected_location]

    st.caption(f"Latitude: {LAT:.4f}°")
    st.caption(f"Longitude: {LON:.4f}°")

    # ================= QUOTE ROTATOR =================
    st.markdown("---")

    st_autorefresh(interval=15000, key="quote_refresh")

    st.session_state.quote_index = (
        st.session_state.quote_index + 1
    ) % len(QUOTES)

    st.markdown(
        f"""
        <div style="
            margin-top: 12px;
            padding: 14px;
            border-radius: 10px;
            background: linear-gradient(145deg, #0b132b, #1c2541);
            color: #f5f5f5;
            font-size: 15px;
            line-height: 1.6;
            text-align: center;
            box-shadow: 0 0 15px rgba(63,169,245,0.35);
        ">
            💬 <em>{QUOTES[st.session_state.quote_index]}</em>
        </div>
        """,
        unsafe_allow_html=True
    )


#LAT, LON = 19.07598, 72.87766  # Mumbai
FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
swe.set_sid_mode(swe.SIDM_LAHIRI)

# ================= SESSION DEFAULTS =================
if "sel_date" not in st.session_state:
    st.session_state.sel_date = datetime.date.today()

if "sel_time" not in st.session_state:
    st.session_state.sel_time = datetime.datetime.now(
        pytz.timezone("Asia/Kolkata")
    ).time()

# ================= ROTATING QUOTES =================


if "quote_index" not in st.session_state:
    st.session_state.quote_index = 0



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
    nak_size = 13 + 1/3
    pada_size = nak_size / 4
    idx = int(lon // nak_size) % 27
    pada = int((lon % nak_size) // pada_size) + 1
    return NAKSHATRAS[idx][0], NAKSHATRAS[idx][1], pada

def get_positions(dt_utc):
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                    dt_utc.hour + dt_utc.minute/60)

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

def generate_svg(pos, retro):
    from collections import defaultdict

    cx, cy = 350, 350

    # Radii
    OUTER_R = 330
    INNER_R = 270
    LINE_R  = 260
    TEXT_R  = 210
    BASE_PLANET_R = 200
    STACK_GAP = 18

    svg = f"""
    <svg width="700" height="700" viewBox="0 0 700 700"
         style="margin:auto;display:block">

    <defs>
        <radialGradient id="glow">
            <stop offset="70%" stop-color="#0a1e3a"/>
            <stop offset="100%" stop-color="#3fa9f5"/>
        </radialGradient>
    </defs>

    <circle cx="{cx}" cy="{cy}" r="{OUTER_R}" fill="url(#glow)"/>
    <circle cx="{cx}" cy="{cy}" r="{INNER_R}"
            fill="#050b18"
            stroke="#88c9ff"
            stroke-width="3"/>
    """

    # =================================================
    # 🔶 RASHI DIVIDER LINES
    # =================================================
    for i in range(12):
        ang = math.radians(90 - i * 30)
        x = cx + LINE_R * math.cos(ang)
        y = cy - LINE_R * math.sin(ang)

        svg += f"""
        <line x1="{cx}" y1="{cy}"
              x2="{x}" y2="{y}"
              stroke="#ffd700"
              stroke-width="2"/>
        """

    # =================================================
    # 🔷 RASHI NAMES (CENTERED)
    # =================================================
    for i in range(12):
        ang = math.radians(90 - (i * 30 + 15))
        x = cx + TEXT_R * math.cos(ang)
        y = cy - TEXT_R * math.sin(ang)

        svg += f"""
        <text x="{x}" y="{y}"
              fill="#00e6ff"
              font-size="22"
              font-weight="bold"
              text-anchor="middle"
              dominant-baseline="middle">
            {SIGNS[i]}
        </text>
        """

    # =================================================
    # 🪐 PLANETS (INCLUDING KETU) — NO OVERLAP
    # =================================================

    groups = defaultdict(list)

    # --- Main planets ---
    for name, code, sym in PLANETS:
        rashi = int(pos[name] // 30)
        groups[rashi].append((name, sym))

    # --- ADD KETU ---
    groups[int(pos["केतु"] // 30)].append(("केतु", "के."))

    # --- Draw planets ---
    for rashi, plist in groups.items():

        ang = math.radians(90 - (rashi * 30 + 15))

        for i, (name, sym) in enumerate(plist):
            r = BASE_PLANET_R - i * STACK_GAP

            px = cx + r * math.cos(ang)
            py = cy - r * math.sin(ang)

            # 🔴 Retrograde = Red | 🟢 Direct = Green
            color = "#ff4d4d" if retro.get(name, False) else "#79e887"

            svg += f"""
            <circle cx="{px}" cy="{py}"
                    r="11"
                    fill="{color}"
                    stroke="#0b3d1f"
                    stroke-width="1"/>

            <text x="{px}" y="{py}"
                  font-size="11"
                  font-weight="bold"
                  fill="black"
                  text-anchor="middle"
                  dominant-baseline="middle">
                {sym}
            </text>
            """

    svg += "</svg>"
    return svg






# ================= UI =================
st.title("🪐 वेदिक ग्रह घड़ी — Drik Panchang")

c1, c2, c3 = st.columns(3)
today = datetime.date.today()
date = c1.date_input(
    "तारीख़",
    value=st.session_state.sel_date,
    min_value=today - datetime.timedelta(days=365*500),     # ✅ NO PAST LIMIT
    max_value=today + datetime.timedelta(days=365*500)     # ✅ NO FUTURE LIMIT
)

time = c2.time_input("समय",value=st.session_state.sel_time)

if c3.button("अब"):
    now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    st.session_state.sel_date = now.date()
    st.session_state.sel_time = now.time()
    st.rerun()

ist = pytz.timezone("Asia/Kolkata")
dt_ist = ist.localize(datetime.datetime.combine(date, time))
dt_utc = dt_ist.astimezone(pytz.utc)   # ✅ REQUIRED

 


pos, retro, jd = get_positions(dt_utc)

# ===== CORRECT DRIK PANCHANG LAGNA =====
ascmc, _ = swe.houses_ex(jd, LAT, LON, b'P', FLAGS)
lagna_deg = ascmc[0] % 360
lagna_sign = SIGNS[int(lagna_deg // 30)]

# ================= LAYOUT =================
left, right = st.columns([2, 1])

with left:
    st.components.v1.html(generate_svg(pos, retro), height=720)


with right:
    st.subheader("🌙 ज्योतिष सार")

    moon_nak, moon_lord, moon_pada = nakshatra_pada(pos["चन्द्र"])

    summary = [
        ["चन्द्र नक्षत्र", str(moon_nak)],
        ["नक्षत्र पद", str(moon_pada)],          # ✅ cast to string
        ["नक्षत्र स्वामी", str(moon_lord)],
        ["लग्न", str(lagna_sign)],
        ["लग्न अंश", f"{lagna_deg:.2f}°"],
        ["समय (IST)", dt_ist.strftime("%d-%b-%Y %H:%M")]
    ]

#st.table(pd.DataFrame(summary, columns=["तत्व", "मान"]))

    st.table(pd.DataFrame(summary, columns=["तत्व", "मान"]))

    st.subheader("🪐 ग्रह स्थिति")
    rows = []

# --- Main planets ---
    for p, code, sym in PLANETS:
        nak, lord, pada = nakshatra_pada(pos[p])
        rows.append([
            p,
            f"{pos[p]:.2f}°",
            SIGNS[int(pos[p]//30)],
            f"{nak} (पद {pada})",
            "🔁 वक्री" if retro[p] else "➡️ मार्गी"
        ])

    # --- ADD KETU (Shadow Planet) ---
    nak, lord, pada = nakshatra_pada(pos["केतु"])
    rows.append([
            "केतु",
        f"{pos['केतु']:.2f}°",
        SIGNS[int(pos["केतु"]//30)],
        f"{nak} (पद {pada})",
        "🔁 वक्री" if retro["केतु"] else "➡️ मार्गी"
        ])


    st.table(pd.DataFrame(
        rows,
        columns=["ग्रह","डिग्री","राशि","नक्षत्र","स्थिति"]
    ))

st.success("IST समय: " + dt_ist.strftime("%d-%b-%Y %H:%M:%S"))

st.markdown("""
---
### *Gaurav Singh Yadav*  
**Quant Trader | Energy & Commodity Intelligence**  
📧 yadav.gauravsingh@gmail.com  
<sub>Built with ❤️ using Swiss Ephemeris & Streamlit</sub>
""")
