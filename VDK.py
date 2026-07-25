import os
# ==================================================
# Python 3.13 compatibility patch for Streamlit
# imghdr was removed in Python 3.13
# ==================================================
import sys
if sys.version_info >= (3, 13):
    import types
    imghdr = types.ModuleType("imghdr")
    imghdr.what = lambda *args, **kwargs: None
    sys.modules["imghdr"] = imghdr
# ==================================================

import streamlit as st
import swisseph as swe
import datetime, pytz, math
import pandas as pd
from collections import defaultdict
import hashlib
import base64

def set_bg_image(image_path: str):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ================= CONFIG =================
st.set_page_config(
    page_title=" जन्म कुंडली और गृह स्थिति व द्रिक पंचांग",
    layout="wide",
    page_icon="🪐"
)
col_logo, col_ticker = st.columns([0.22, 0.78])

with col_logo:
    st.image("Assets/Raosaab.png", width=220)

set_bg_image("Assets/ASTW.png")

# ================= SOLID CARD STYLING =================
st.markdown("""
<style>

/* Solid Card Container */
.solid-card {
    background-color: #0f172a;  /* solid dark navy */
    border: 2px solid #00e6ff;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 0 18px rgba(0,230,255,0.35);
    margin-bottom: 15px;
}

/* Card Title */
.solid-title {
    font-size: 18px;
    font-weight: 600;
    color: #00e6ff;
    margin-bottom: 10px;
}

/* Table Styling */
.solid-card table {
    color: white;
}

.solid-card thead tr th {
    background-color: #1e293b !important;
    color: #00e6ff !important;
}

.solid-card tbody tr td {
    background-color: #111827 !important;
    color: #f1f5f9 !important;
}

/* Dataframe fix */
div[data-testid="stDataFrame"] {
    background-color: #0f172a !important;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ================= ROTATING QUOTES =================
QUOTES = [
    "भीड़ में सब लोग अच्छे नहीं होते और अच्छे लोगों की कभी भीड़ नहीं होती",
    "हमारी समस्या का समाधान सिर्फ हमारे पास है, दूसरों के पास तो सिर्फ सुझाव है",
    "कोई काम तब तक ही असंभव लगता है जब तक कि वह हो नहीं जाता",
    "आपकी किस्मत आपको मौका देगी पर आपकी मेहनत सब को चौंका देगी",
    "ना किसी से ईर्ष्या ना किसी से होड़, मेरी अपनी मंजिल मेरी अपनी दौड़",
    "काम ऐसा करो कि नाम हो जाए या नाम ऐसा करो कि काम हो जाए",
    "याद रखना कमजोर हम नहीं, हमारा वक्त है",
    "मेहनत इंसान को मजबूत बनाती है",
    "अगर जिंदगी बदलनी है तो सबसे पहले सोच बदलो",
    "खुद पर भरोसा रखो, यही सबसे बड़ी ताकत है",
    "जो समय की कदर करता है, समय उसी की कदर करता है",
    "संघर्ष जितना बड़ा होगा, जीत उतनी ही शानदार होगी",
    "खामोशी से मेहनत करो, शोर खुद बन जाएगा",
    "हार तब होती है जब मान लिया जाए",
    "आज का दर्द ही कल की ताकत बनेगा",
    "किस्मत उन्हीं का साथ देती है जो खुद पर भरोसा रखते हैं",
    "जो मिला है उसी में खुश रहना भी एक कला है",
    "रास्ते खुद बनते हैं जब हौसले मजबूत होते हैं",
    "हर दिन एक नया मौका है खुद को बेहतर बनाने का"
]

EN_QUOTES = [
    "Discipline is choosing between what you want now and what you want most.",
    "Success is built quietly while the world is sleeping.",
    "Your future depends on what you do today, not tomorrow.",
    "Consistency beats motivation every single time.",
    "Hard work makes luck predictable.",
    "Don’t wait for opportunity. Create it.",
    "The pain you feel today will be your strength tomorrow.",
    "Focus on progress, not perfection.",
    "Small steps daily create massive results.",
    "Your mindset decides your market results.",
    "Dreams don’t work unless you do.",
    "Patience is also a trading strategy.",
    "Risk is unavoidable, regret is optional.",
    "Winners manage emotions, losers manage excuses.",
    "Time rewards discipline, not desperation.",
    "Stay humble, stay hungry.",
    "Success loves preparation.",
    "Your habits define your destiny.",
    "Master yourself before mastering markets.",
    "Calm minds make powerful decisions."
]

if "quote_index" not in st.session_state:
    st.session_state.quote_index = 0


@st.cache_data(show_spinner=False)
def load_india_locations():
    if os.path.exists("INDIALL.parquet"):
        df = pd.read_parquet("INDIALL.parquet")
    elif os.path.exists("INDIALL.json"):
        df = pd.read_json("INDIALL.json")
    else:
        st.error("❌ INDIALL.json or INDIALL.parquet not found")
        st.stop()

    df.columns = df.columns.str.strip()
    df["label"] = df["District"] + " – " + df["State"]
    return df

# ================= LOCATION DATA =================
india_df = load_india_locations()

LOCATIONS = {
    row["label"]: (row["Latitude"], row["Longitude"])
    for _, row in india_df.iterrows()
}

NAME_STYLES = [
    {
        "font": "'Segoe UI', sans-serif",
        "color": "#00e6ff",
        "weight": "400",
        "text": "जय श्री राधे!<br><span style='font-size:16px; opacity:0.85;'>जय श्री कृष्णा! </span>"
    },
    {
        "font": "'Georgia', serif",
        "color": "#ffd166",
        "weight": "400",
        "text": "जय श्री राधे!<br><span style='font-size:16px; opacity:0.85;'>जय श्री कृष्णा! </span>"
    },
    {
        "font": "'Courier New', monospace",
        "color": "#9bf6ff",
        "weight": "400",
        "text": "जय श्री राधे!<br><span style='font-size:16px; opacity:0.85;'>जय श्री कृष्णा! </span>"
    },
    {
        "font": "'Trebuchet MS', sans-serif",
        "color": "#caffbf",
        "weight": "400",
        "text": "जय श्री राधे!<br><span style='font-size:16px; opacity:0.85;'>जय श्री कृष्णा! </span>"
    }
]

if "quote_lang" not in st.session_state:
    st.session_state.quote_lang = "Hindi"

if "name_style_idx" not in st.session_state:
    st.session_state.name_style_idx = 0

with st.sidebar:
    st.markdown("### 📍 स्थान चयन (Location)")

    location_keys = list(LOCATIONS.keys())

    default_index = 0
    for i, name in enumerate(location_keys):
        if "Mumbai" in name and "MAHARASHTRA" in name:
            default_index = i
            break

    selected_location = st.selectbox(
        "राज्य / राजधानी चुनें",
        list(LOCATIONS.keys()),
        index=default_index
    )

    LAT, LON = LOCATIONS[selected_location]

    st.caption(f"Latitude: {LAT:.4f}°")
    st.caption(f"Longitude: {LON:.4f}°")

    st.markdown("---")
    quote_lang = st.radio(
        "उद्धरण भाषा/Quote Language",
        ["हिंदी", "English"],
        horizontal=True
    )
    st.session_state.quote_lang = quote_lang

    st.markdown("---")

    if "name_style_time" not in st.session_state:
        st.session_state.name_style_time = datetime.datetime.now()

    now = datetime.datetime.now()

    if (now - st.session_state.name_style_time).seconds > 10:
        st.session_state.name_style_idx = (
            st.session_state.name_style_idx + 1
        ) % len(NAME_STYLES)
        st.session_state.name_style_time = now

    style = NAME_STYLES[st.session_state.name_style_idx]

    st.markdown(
        f"""
        <div style="
            margin-top: 10px;
            padding: 16px;
            border-radius: 14px;
            background: linear-gradient(145deg, #0e162e, #1b2a4a);
            box-shadow: 0 0 18px rgba(63,169,245,0.45);
            text-align: center;
        ">
            <div style="
                font-family: {style['font']};
                font-size: 14px;
                font-weight: {style['weight']};
                color: {style['color']};
                letter-spacing: 1px;
                transition: all 0.6s ease-in-out;
            ">
                {style['text']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    ACTIVE_QUOTES = QUOTES if quote_lang == "हिंदी" else EN_QUOTES

    if "quote_time" not in st.session_state:
        st.session_state.quote_time = datetime.datetime.now()

    now = datetime.datetime.now()

    if (now - st.session_state.quote_time).seconds > 5:
        st.session_state.quote_index = (
            st.session_state.quote_index + 1
        ) % len(ACTIVE_QUOTES)
        st.session_state.quote_time = now

    st.markdown(
        f"""
        <div style="
            margin-top: 12px;
            padding: 14px;
            border-radius: 10px;
            background: linear-gradient(145deg, #0b132b, #1c2541);
            color: #f5f5f5;
            font-size: 13px;
            line-height: 1.6;
            text-align: center;
            font-weight: 500;
            box-shadow: 0 0 15px rgba(63,169,245,0.35);
        ">
            💬 <em>{ACTIVE_QUOTES[st.session_state.quote_index]}</em>
        </div>
        """,
        unsafe_allow_html=True
    )

FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
swe.set_sid_mode(swe.SIDM_LAHIRI)
swe.set_ephe_path(".")

# ================= SESSION DEFAULTS =================
if "sel_date" not in st.session_state:
    st.session_state.sel_date = datetime.date.today()

if "sel_time" not in st.session_state:
    st.session_state.sel_time = datetime.datetime.now(
        pytz.timezone("Asia/Kolkata")
    ).time()

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

def get_true_moon_lon_and_speed(jd):
    ay = swe.get_ayanamsa_ut(jd)
    r, _ = swe.calc_ut(
        jd,
        swe.MOON,
        swe.FLG_SWIEPH | swe.FLG_TRUEPOS | swe.FLG_SPEED
    )
    moon_lon = (r[0] - ay) % 360
    moon_speed = abs(r[3])
    return moon_lon, moon_speed

def get_sun_moon_times(date, lat, lon):
    jd = swe.julday(date.year, date.month, date.day, 0)
    geopos = (lon, lat, 0)

    rs = swe.rise_trans(jd, swe.SUN, swe.CALC_RISE | swe.BIT_DISC_CENTER, geopos)
    ss = swe.rise_trans(jd, swe.SUN, swe.CALC_SET  | swe.BIT_DISC_CENTER, geopos)

    mr = swe.rise_trans(jd, swe.MOON, swe.CALC_RISE, geopos)
    ms = swe.rise_trans(jd, swe.MOON, swe.CALC_SET,  geopos)

    def jd_to_time(res):
        try:
            if res[0] != 0:
                return "—"
            y, m, d, h = swe.revjul(res[1][0])
            hour = int(h)
            minute = int((h - hour) * 60)
            dt_utc = datetime.datetime(y, m, d, hour, minute, tzinfo=pytz.utc)
            dt_ist = dt_utc.astimezone(pytz.timezone("Asia/Kolkata"))
            return dt_ist.strftime("%H:%M")
        except:
            return "—"

    sunrise  = jd_to_time(rs)
    sunset   = jd_to_time(ss)
    moonrise = jd_to_time(mr)
    moonset  = jd_to_time(ms)

    return sunrise, sunset, moonrise, moonset

TITHI_NAMES = ["प्रतिपदा","द्वितीया","तृतीया","चतुर्थी","पंचमी","षष्ठी","सप्तमी","अष्टमी","नवमी","दशमी","एकादशी","द्वादशी","त्रयोदशी","चतुर्दशी","पूर्णिमा","प्रतिपदा","द्वितीया","तृतीया","चतुर्थी","पंचमी","षष्ठी","सप्तमी","अष्टमी","नवमी","दशमी","एकादशी","द्वादशी","त्रयोदशी","चतुर्दशी","अमावस्या"]

def get_tithi(moon_lon, sun_lon):
    diff = (moon_lon - sun_lon) % 360
    tithi_index = int(diff / 12)
    return TITHI_NAMES[tithi_index]

CHOGHADIYA_DAY = [
"उद्वेग","चर","लाभ","अमृत",
"काल","शुभ","रोग","उद्वेग"
]

def get_running_choghadiya(current_time, sunrise, sunset):
    try:
        sr = datetime.datetime.strptime(sunrise,"%H:%M")
        ss = datetime.datetime.strptime(sunset,"%H:%M")
        now = datetime.datetime.strptime(current_time,"%H:%M")

        day_duration = (ss - sr).seconds / 8

        for i in range(8):
            start = sr + datetime.timedelta(seconds=i*day_duration)
            end = start + datetime.timedelta(seconds=day_duration)

            if start <= now <= end:
                return CHOGHADIYA_DAY[i]
    except:
        pass
    return "रात्रि चोघड़िया"

# ================= SVG GENERATOR WITH NON-OVERLAPPING LAYOUT =================
def generate_svg(pos, retro):
    cx, cy = 350, 350

    OUTER_R = 340
    INNER_R = 330
    LINE_R  = 330
    RASHI_R = 298       # Pushed to outer boundary (no overlap with planets)
    BASE_PLANET_R = 235 # Outer ring for planet badges
    STACK_GAP = 36     # Spacing between multiple planets in same sign

    # Current Moon Nakshatra in Clock Center
    moon_nak, _, moon_pada = nakshatra_pada(pos["चन्द्र"])

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

    <!-- Display Current Moon Nakshatra in Clock Center -->
    <text x="{cx}" y="{cy - 12}"
          fill="#ffd700"
          font-size="15"
          font-weight="bold"
          text-anchor="middle">
        नक्षत्र: {moon_nak}
    </text>
    <text x="{cx}" y="{cy + 12}"
          fill="#00e6ff"
          font-size="13"
          font-weight="bold"
          text-anchor="middle">
        (पद {moon_pada})
    </text>
    """

    # Sector Divider Lines
    for i in range(12):
        ang = math.radians(90 - i * 30)
        x = cx + LINE_R * math.cos(ang)
        y = cy - LINE_R * math.sin(ang)

        svg += f"""
        <line x1="{cx}" y1="{cy}"
              x2="{x}" y2="{y}"
              stroke="#ffd700"
              stroke-opacity="0.6"
              stroke-width="1.5"/>
        """

    # Zodiac Sign Names (Placed high up near outer edge)
    for i in range(12):
        ang = math.radians(90 - (i * 30 + 15))
        x = cx + RASHI_R * math.cos(ang)
        y = cy - RASHI_R * math.sin(ang)

        svg += f"""
        <text x="{x}" y="{y}"
              fill="#00e6ff"
              font-size="18"
              font-weight="bold"
              text-anchor="middle"
              dominant-baseline="middle">
            {SIGNS[i]}
        </text>
        """

    # Group Planets by Zodiac Sign
    groups = defaultdict(list)

    for name, code, sym in PLANETS:
        rashi = int(pos[name] // 30)
        groups[rashi].append((name, sym, pos[name]))

    ketu_deg = pos["केतु"]
    groups[int(ketu_deg // 30)].append(("केतु", "के.", ketu_deg))

    # Render Planet Badges, Degrees, and Nakshatra/Pada Labels
    for rashi, plist in groups.items():
        sector_deg = 90 - (rashi * 30 + 15)
        ang = math.radians(sector_deg)

        # SVG text rotation angle & auto-flip for readability
        raw_rot = -sector_deg
        norm_rot = raw_rot % 360

        # Auto-flip text if angle is upside-down (between 90° and 270°)
        if 90 < norm_rot < 270:
            rot_angle = raw_rot + 180
        else:
            rot_angle = raw_rot

        for i, (name, sym, lon) in enumerate(plist):
            r = BASE_PLANET_R - i * STACK_GAP

            px = cx + r * math.cos(ang)
            py = cy - r * math.sin(ang)

            deg_in_sign = lon % 30
            p_nak, _, p_pada = nakshatra_pada(lon)
            color = "#ff4d4d" if retro.get(name, False) else "#79e887"

            # Planet Badge Circle
            svg += f"""
            <circle cx="{px}" cy="{py}"
                    r="11"
                    fill="{color}"
                    stroke="#0b3d1f"
                    stroke-width="1"/>

            <!-- Planet Symbol -->
            <text x="{px}" y="{py}"
                  font-size="10"
                  font-weight="bold"
                  fill="black"
                  text-anchor="middle"
                  dominant-baseline="middle">
                {sym}
            </text>

            <!-- Planet Degree in Sign -->
            <text x="{px}" y="{py + 16}"
                  font-size="9"
                  font-weight="bold"
                  fill="#ffd700"
                  text-anchor="middle">
                {deg_in_sign:.1f}°
            </text>
            """

            # Planet Nakshatra & Pada Label (Placed cleanly below degree text)
            nak_r = r - 26
            tx = cx + nak_r * math.cos(ang)
            ty = cy - nak_r * math.sin(ang)

            svg += f"""
            <text x="{tx}" y="{ty}"
                  font-size="9"
                  font-weight="bold"
                  fill="#9bf6ff"
                  text-anchor="middle"
                  dominant-baseline="middle"
                  transform="rotate({rot_angle}, {tx}, {ty})">
                {p_nak} ({p_pada})
            </text>
            """

    svg += "</svg>"
    return svg

# ================= UI =================
st.title("🪐 वेदिक ग्रह घड़ी — द्रिक पंचांग ")

c1, c2, c3 = st.columns(3)
today = datetime.date.today()
date = c1.date_input(
    "तारीख़",
    value=st.session_state.sel_date,
    min_value=today - datetime.timedelta(days=365*500),
    max_value=today + datetime.timedelta(days=365*500)
)

time = c2.time_input("समय", value=st.session_state.sel_time)

st.session_state.sel_date = date
st.session_state.sel_time = time

if c3.button("अब"):
    now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    st.session_state.sel_date = now.date()
    st.session_state.sel_time = now.time()
    st.rerun()

ist = pytz.timezone("Asia/Kolkata")
dt_ist = ist.localize(datetime.datetime.combine(date, time))
dt_utc = dt_ist.astimezone(pytz.utc)

pos, retro, jd = get_positions(dt_utc)

ascmc, _ = swe.houses_ex(jd, LAT, LON, b'P', FLAGS)
lagna_deg = ascmc[0] % 360
lagna_sign = SIGNS[int(lagna_deg // 30)]

left, right = st.columns([2, 1])

with left:
    st.components.v1.html(generate_svg(pos, retro), height=720)

with right:
    st.markdown('<div class="solid-card">', unsafe_allow_html=True)
    st.markdown('<div class="solid-title">🌙 ज्योतिष सार</div>', unsafe_allow_html=True)

    moon_nak, moon_lord, moon_pada = nakshatra_pada(pos["चन्द्र"])
    sunrise, sunset, moonrise, moonset = get_sun_moon_times(date, LAT, LON)
    tithi = get_tithi(pos["चन्द्र"], pos["सूर्य"])
    current_time_str = dt_ist.strftime("%H:%M")
    choghadiya = get_running_choghadiya(current_time_str, sunrise, sunset)

    summary = [
        ["चन्द्र नक्षत्र", str(moon_nak)],
        ["नक्षत्र पद", str(moon_pada)],
        ["नक्षत्र स्वामी", str(moon_lord)],
        ["लग्न", str(lagna_sign)],
        ["लग्न अंश", f"{lagna_deg:.2f}°"],
        ["तिथि", tithi],
        ["चोघड़िया (चल रहा)", choghadiya],
        ["सूर्योदय", sunrise],
        ["सूर्यास्त", sunset],
        ["चंद्र उदय", moonrise],
        ["चंद्र अस्त", moonset],
        ["समय (IST)", dt_ist.strftime("%d-%b-%Y %H:%M")]
    ]

    st.table(pd.DataFrame(summary, columns=["तत्व", "मान"]))
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="solid-card">', unsafe_allow_html=True)
st.markdown('<div class="solid-title">🪐 ग्रह स्थिति</div>', unsafe_allow_html=True)
rows = []

for p, code, sym in PLANETS:
    nak, lord, pada = nakshatra_pada(pos[p])
    rows.append([
        p,
        f"{pos[p]:.2f}°",
        SIGNS[int(pos[p]//30)],
        f"{nak} (पद {pada})",
        "↺🔴 वक्री" if retro[p] else  "↻🟢मार्गी"
    ])

nak, lord, pada = nakshatra_pada(pos["केतु"])
rows.append([
    "केतु",
    f"{pos['केतु']:.2f}°",
    SIGNS[int(pos["केतु"]//30)],
    f"{nak} (पद {pada})",
    "↺🔴 वक्री" if retro["केतु"] else  "↻🟢मार्गी"
])

st.table(pd.DataFrame(
    rows,
    columns=["ग्रह","डिग्री","राशि","नक्षत्र","स्थिति"]
))
st.markdown('</div>', unsafe_allow_html=True)

ZODIACS = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

def angular_diff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)

ASPECTS = {
    "Conjunction": {z: z for z in ZODIACS},
    "Opposition": {
        "Aries": "Libra",
        "Taurus": "Scorpio",
        "Gemini": "Sagittarius",
        "Cancer": "Capricorn",
        "Leo": "Aquarius",
        "Virgo": "Pisces",
        "Libra": "Aries",
        "Scorpio": "Taurus",
        "Sagittarius": "Gemini",
        "Capricorn": "Cancer",
        "Aquarius": "Leo",
        "Pisces": "Virgo"
    }
}

def upcoming_aspects(start_dt_utc, days=5, step_minutes=30):
    events = []
    seen = set()

    total_steps = int((days * 24 * 60) / step_minutes)
    prev_pos = None

    for step in range(total_steps):
        dt = start_dt_utc + datetime.timedelta(minutes=step * step_minutes)
        pos, _, _ = get_positions(dt)

        if prev_pos is None:
            prev_pos = pos
            continue

        planets = list(pos.keys())

        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1, p2 = planets[i], planets[j]

                prev_diff = angular_diff(prev_pos[p1], prev_pos[p2])
                curr_diff = angular_diff(pos[p1], pos[p2])

                if prev_diff > 1 and curr_diff <= 1:
                    key = (p1, p2, "Conjunction")
                    if key not in seen:
                        seen.add(key)
                        events.append({
                            "aspect": "Conjunction",
                            "planets": f"{p1} ☌ {p2}",
                            "time": dt
                        })

                if prev_diff < 179 and curr_diff >= 179:
                    key = (p1, p2, "Opposition")
                    if key not in seen:
                        seen.add(key)
                        events.append({
                            "aspect": "Opposition",
                            "planets": f"{p1} ☍ {p2}",
                            "time": dt
                        })

        prev_pos = pos

    return events

def moon_sun_diff(moon_deg, sun_deg):
    diff = (moon_deg - sun_deg) % 360
    return min(diff, 360 - diff)

def detect_amavasya_purnima(start_dt_utc, days=30, step_minutes=15):
    events = {
        "Amavasya": {"start": None, "end": None},
        "Purnima": {"start": None, "end": None}
    }

    total_steps = int((days * 24 * 60) / step_minutes)
    prev_diff = None

    for step in range(total_steps):
        dt = start_dt_utc + datetime.timedelta(minutes=step * step_minutes)
        pos, _, _ = get_positions(dt)

        moon = pos["चन्द्र"]
        sun = pos["सूर्य"]
        diff = moon_sun_diff(moon, sun)

        if (
            prev_diff is not None
            and prev_diff > 12
            and diff <= 12
            and events["Amavasya"]["start"] is None
        ):
            events["Amavasya"]["start"] = dt

        if (
            events["Amavasya"]["start"]
            and prev_diff is not None
            and prev_diff > 0.5
            and diff <= 0.5
            and events["Amavasya"]["end"] is None
        ):
            events["Amavasya"]["end"] = dt

        if (
            prev_diff is not None
            and prev_diff < 168
            and diff >= 168
            and events["Purnima"]["start"] is None
        ):
            events["Purnima"]["start"] = dt

        if (
            events["Purnima"]["start"]
            and prev_diff is not None
            and prev_diff < 179.5
            and diff >= 179.5
            and events["Purnima"]["end"] is None
        ):
            events["Purnima"]["end"] = dt

        prev_diff = diff

        if all(v["end"] for v in events.values()):
            break

    return events

st.subheader("🌙 Amavasya & Purnima (Upcoming)")

events = detect_amavasya_purnima(dt_utc, days=30)
ist = pytz.timezone("Asia/Kolkata")

for name, data in events.items():
    if data["start"] and data["end"]:
        start_ist = data["start"].astimezone(ist)
        end_ist = data["end"].astimezone(ist)

        st.markdown(
            f"""
            **{name}**
            - 🟢 Start : {start_ist.strftime('%d-%b-%Y %H:%M IST')}
            - 🔴 End   : {end_ist.strftime('%d-%b-%Y %H:%M IST')}
            """
        )
    else:
        st.caption(f"{name} not found in the next 30 days.")

st.markdown('<div class="solid-card">', unsafe_allow_html=True)
st.markdown('<div class="solid-title">🔭 Upcoming Conjunctions & Oppositions (Next 10 Days)</div>', unsafe_allow_html=True)

events = upcoming_aspects(
    start_dt_utc=dt_utc,
    days=10,
    step_minutes=30
)

if not events:
    st.caption("No major conjunctions or oppositions in the next 10 days.")
else:
    rows = []
    for e in events:
        t_ist = e["time"].astimezone(ist)
        rows.append([
            t_ist.strftime("%d-%b-%Y"),
            t_ist.strftime("%H:%M"),
            e["aspect"],
            e["planets"]
        ])

    df_aspects = pd.DataFrame(
        rows,
        columns=["Date", "Time (IST)", "Aspect", "Planets"]
    )

    st.dataframe(
        df_aspects,
        use_container_width=True,
        hide_index=True
    )
st.markdown('</div>', unsafe_allow_html=True)

NAK_SIZE = 13 + 1/3

def zodiac_index(deg):
    return int(deg // 30)

def nakshatra_index(deg):
    return int(deg // NAK_SIZE)

def zodiac_name(deg):
    return SIGNS[zodiac_index(deg)]

def nakshatra_name(deg):
    return NAKSHATRAS[nakshatra_index(deg)][0]

def upcoming_sign_nakshatra_changes(start_dt_utc, days=10, step_minutes=30):
    events = []
    FAST_PLANETS = ["चन्द्र", "बुध", "शुक्र", "सूर्य"]

    total_steps = int((days * 24 * 60) / step_minutes)
    prev_pos = None

    for step in range(total_steps):
        dt = start_dt_utc + datetime.timedelta(minutes=step * step_minutes)
        pos, _, _ = get_positions(dt)

        if prev_pos is None:
            prev_pos = pos
            continue

        for planet in FAST_PLANETS:
            prev_sign = zodiac_name(prev_pos[planet])
            curr_sign = zodiac_name(pos[planet])

            if prev_sign != curr_sign:
                events.append({
                    "type": "Zodiac Change",
                    "planet": planet,
                    "from": prev_sign,
                    "to": curr_sign,
                    "time": dt
                })

            prev_nak = nakshatra_name(prev_pos[planet])
            curr_nak = nakshatra_name(pos[planet])

            if prev_nak != curr_nak:
                events.append({
                    "type": "Nakshatra Change",
                    "planet": planet,
                    "from": prev_nak,
                    "to": curr_nak,
                    "time": dt
                })

        prev_pos = pos

    return events

st.subheader("🪐 Planetary Transitions (Next 10 Days)")

events = upcoming_sign_nakshatra_changes(
    start_dt_utc=dt_utc,
    days=10,
    step_minutes=30
)

if not events:
    st.caption("No planetary sign or nakshatra changes in the next 10 days.")
else:
    rows = []
    for e in events:
        t_ist = e["time"].astimezone(ist)
        rows.append([
            t_ist.strftime("%d-%b-%Y"),
            t_ist.strftime("%H:%M"),
            e["planet"],
            e["type"],
            e["from"],
            e["to"]
        ])

    df_transitions = pd.DataFrame(
        rows,
        columns=[
            "Date",
            "Time (IST)",
            "Planet",
            "Change Type",
            "From",
            "To"
        ]
    )

    st.dataframe(
        df_transitions,
        use_container_width=True,
        hide_index=True
    )
