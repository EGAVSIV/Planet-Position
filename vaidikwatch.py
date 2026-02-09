
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
from streamlit_autorefresh import st_autorefresh
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
    page_title="🪐 वेदिक ग्रह घड़ी — द्रिक पंचांग",
    layout="wide",
    page_icon="🪐"
)
col_logo, col_ticker = st.columns([0.22, 0.78])

with col_logo:
    st.image("Assets/sgy1.png", width=220)

set_bg_image("Assets/BG11.png")

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
    """
    Load latitude / longitude from INDIALL.json or INDIALL.parquet
    Columns required:
    District | State | Latitude | Longitude
    """
    if os.path.exists("INDIALL.parquet"):
        df = pd.read_parquet("INDIALL.parquet")
    elif os.path.exists("INDIALL.json"):
        df = pd.read_json("INDIALL.json")
    else:
        st.error("❌ INDIALL.json or INDIALL.parquet not found")
        st.stop()

    # Safety: normalize column names
    df.columns = df.columns.str.strip()

    # Create label for dropdown
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

# MUST EXIST BEFORE SIDEBAR
if "name_style_idx" not in st.session_state:
    st.session_state.name_style_idx = 0

with st.sidebar:
    # ================= LOCATION =================
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

    # ================= QUOTE LANGUAGE =================
    st.markdown("---")
    quote_lang = st.radio(
        "उद्धरण भाषा/Quote Language",
        ["हिंदी", "English"],
        horizontal=True
    )
    st.session_state.quote_lang = quote_lang

    # ================= NAME ROTATOR =================
    st.markdown("---")

    st_autorefresh(interval=5000, key="name_refresh")

    st.session_state.name_style_idx = (
        st.session_state.name_style_idx + 1
    ) % len(NAME_STYLES)

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

    # ================= QUOTE ROTATOR =================
    st_autorefresh(interval=5000, key="quote_refresh")

    st.session_state.quote_index = (
        st.session_state.quote_index + 1
    ) % len(ACTIVE_QUOTES)

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

    # राशियाँ
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

    # ग्रह stacking
    groups = defaultdict(list)

    for name, code, sym in PLANETS:
        rashi = int(pos[name] // 30)
        groups[rashi].append((name, sym))

    groups[int(pos["केतु"] // 30)].append(("केतु", "के."))

    for rashi, plist in groups.items():
        ang = math.radians(90 - (rashi * 30 + 15))

        for i, (name, sym) in enumerate(plist):
            r = BASE_PLANET_R - i * STACK_GAP

            px = cx + r * math.cos(ang)
            py = cy - r * math.sin(ang)

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
    st.subheader("🌙 ज्योतिष सार")

    moon_nak, moon_lord, moon_pada = nakshatra_pada(pos["चन्द्र"])

    summary = [
        ["चन्द्र नक्षत्र", str(moon_nak)],
        ["नक्षत्र पद", str(moon_pada)],
        ["नक्षत्र स्वामी", str(moon_lord)],
        ["लग्न", str(lagna_sign)],
        ["लग्न अंश", f"{lagna_deg:.2f}°"],
        ["समय (IST)", dt_ist.strftime("%d-%b-%Y %H:%M")]
    ]

    st.table(pd.DataFrame(summary, columns=["तत्व", "मान"]))

    st.subheader("🪐 ग्रह स्थिति")
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

def unique_events(events):
    seen = set()
    final = []

    for e in events:
        key = (e["aspect"], e["planets"])
        if key not in seen:
            seen.add(key)
            final.append(e)

    return final

def zodiac_sign(deg):
    return ZODIACS[int(deg // 30)]

def detect_aspects(pos):
    events = []

    planets = list(pos.keys())

    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1, p2 = planets[i], planets[j]
            s1 = zodiac_sign(pos[p1])
            s2 = zodiac_sign(pos[p2])

            if s1 == s2:
                events.append(f"{p1} ☌ {p2} (Conjunction in {s1})")
            elif ASPECTS["Opposition"].get(s1) == s2:
                events.append(f"{p1} ☍ {p2} (Opposition {s1}–{s2})")

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

ASPECT_STYLE = {
    "Conjunction": {
        "icon": "🟢",
        "color": "#2ecc71"
    },
    "Opposition": {
        "icon": "🔴",
        "color": "#e74c3c"
    }
}

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

st.subheader("🔭 Upcoming Conjunctions & Oppositions (Next 10 Days)")

events = upcoming_aspects(
    start_dt_utc=dt_utc,
    days=10,
    step_minutes=30
)

ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.datetime.now(ist)

ASPECT_STYLE = {
    "Conjunction": {"icon": "🟢", "color": "#2ecc71"},
    "Opposition": {"icon": "🔴", "color": "#e74c3c"}
}

if not events:
    st.caption("No major conjunctions or oppositions in the next 10 days.")
else:
    grouped = defaultdict(list)
    for e in events:
        t_ist = e["time"].astimezone(ist)
        grouped[t_ist.date()].append((e, t_ist))

    html = """
    <style>
    @keyframes blink {
        0% { box-shadow: 0 0 6px red; }
        50% { box-shadow: 0 0 18px red; }
        100% { box-shadow: 0 0 6px red; }
    }
    </style>
    """

    for event_date in sorted(grouped.keys()):
        html += f"""
        <h4 style="color:#00e6ff; margin:12px 0 6px 0;">
            📅 {event_date.strftime('%d %b %Y')}
        </h4>
        """

        for e, t in grouped[event_date]:
            style = ASPECT_STYLE[e["aspect"]]
            delta = t - now_ist
            hours_left = delta.total_seconds() / 3600

            if delta.total_seconds() > 0:
                days = delta.days
                hrs, rem = divmod(delta.seconds, 3600)
                mins = rem // 60
                countdown = f"{days}d {hrs}h {mins}m"
            else:
                countdown = "Started"

            blink = "animation: blink 1.2s infinite;" if 0 < hours_left <= 24 else ""

            html += f"""
            <div style="
                margin-bottom: 14px;
                padding: 12px 14px;
                border-radius: 10px;
                background: #0b132b;
                border-left: 6px solid {style['color']};
                {blink}
            ">
                <div style="
                    font-size: 16px;
                    font-weight: 600;
                    color: {style['color']};
                ">
                    {style['icon']} {e['planets']} — {e['aspect']}
                </div>

                <div style="margin-top:4px; font-size:14px; color:#dddddd;">
                    🕒 {t.strftime('%H:%M IST')}
                </div>

                <div style="
                    margin-top:4px;
                    font-size:13px;
                    color:#ffcc00;
                ">
                    ⏳ {countdown}
                </div>
            </div>
            """

    st.components.v1.html(html, height=520, scrolling=True)

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

ist = pytz.timezone("Asia/Kolkata")
now_ist = datetime.datetime.now(ist)

if not events:
    st.caption("No planetary sign or nakshatra changes in the next 10 days.")
else:
    grouped = defaultdict(list)
    for e in events:
        t = e["time"].astimezone(ist)
        grouped[t.date()].append((e, t))

    html = ""

    for d in sorted(grouped.keys()):
        html += f"""
        <h4 style="color:#00e6ff; margin:12px 0 6px 0;">
            📅 {d.strftime('%d %b %Y')}
        </h4>
        """

        for e, t in grouped[d]:
            delta = t - now_ist
            hrs_left = delta.total_seconds() / 3600

            blink = "animation: blink 1.2s infinite;" if 0 < hrs_left <= 24 else ""

            badge_color = "#3498db" if e["type"] == "Zodiac Change" else "#9b59b6"
            icon = "♈" if e["type"] == "Zodiac Change" else "🌟"

            html += f"""
            <div style="
                margin-bottom: 12px;
                padding: 12px 14px;
                border-radius: 10px;
                background: #0b132b;
                border-left: 6px solid {badge_color};
                {blink}
            ">
                <div style="font-size:16px; font-weight:600; color:{badge_color};">
                    {icon} {e['planet']} — {e['type']}
                </div>

                <div style="font-size:14px; color:#dddddd; margin-top:4px;">
                    {e['from']} → <b>{e['to']}</b>
                </div>

                <div style="font-size:13px; color:#ffcc00; margin-top:4px;">
                    🕒 {t.strftime('%H:%M IST')}
                </div>
            </div>
            """

    st.components.v1.html(html, height=520, scrolling=True)

RASHI_NUM = {
    "मेष": 1, "वृषभ": 2, "मिथुन": 3, "कर्क": 4,
    "सिंह": 5, "कन्या": 6, "तुला": 7, "वृश्चिक": 8,
    "धनु": 9, "मकर": 10, "कुंभ": 11, "मीन": 12
}

HOUSE_BOXES = {
    1:(270,360),
    2:(120,360),
    3:(180,460),
    4:(270,500),
    5:(350,420),
    6:(350,260),
    7:(270,200),
    8:(180,240),
    9:(430,500),
    10:(580,360),
    11:(430,200),
    12:(350,140),
}

def build_rashi_sequence(lagna_sign):
    start = SIGNS.index(lagna_sign)
    return {i+1: SIGNS[(start+i) % 12] for i in range(12)}

def build_house_rashi_map(lagna_sign):
    start = SIGNS.index(lagna_sign)
    return {house: SIGNS[(start + house - 1) % 12] for house in range(1, 13)}

def planet_house(planet_deg, lagna_deg):
    return int(((planet_deg - lagna_deg) % 360) // 30) + 1

def draw_north_indian_kundali_CORRECT():
    svg = """
    <svg width="700" height="700" viewBox="0 0 700 700">

      <rect x="50" y="50" width="600" height="600"
            fill="white" stroke="#ff7a00" stroke-width="3"/>

      <line x1="350" y1="50"  x2="650" y2="350"
            stroke="#ff7a00" stroke-width="3"/>
      <line x1="650" y1="350" x2="350" y2="650"
            stroke="#ff7a00" stroke-width="3"/>
      <line x1="350" y1="650" x2="50"  y2="350"
            stroke="#ff7a00" stroke-width="3"/>
      <line x1="50"  y1="350" x2="350" y2="50"
            stroke="#ff7a00" stroke-width="3"/>

      <line x1="200" y1="200" x2="500" y2="200"
            stroke="#ff7a00" stroke-width="3"/>
      <line x1="500" y1="200" x2="500" y2="500"
            stroke="#ff7a00" stroke-width="3"/>
      <line x1="500" y1="500" x2="200" y2="500"
            stroke="#ff7a00" stroke-width="3"/>
      <line x1="200" y1="500" x2="200" y2="200"
            stroke="#ff7a00" stroke-width="3"/>

      <line x1="200" y1="200" x2="500" y2="500"
            stroke="#ff7a00" stroke-width="3"/>
      <line x1="500" y1="200" x2="200" y2="500"
            stroke="#ff7a00" stroke-width="3"/>

      <text x="350" y="150" text-anchor="middle" fill="#ff7a00">12th</text>
      <text x="260" y="210" fill="#ff7a00">2nd</text>
      <text x="160" y="320" fill="#ff7a00">3rd</text>
      <text x="160" y="430" fill="#ff7a00">4th</text>
      <text x="260" y="540" fill="#ff7a00">5th</text>
      <text x="320" y="620" text-anchor="middle" fill="#ff7a00">6th</text>
      <text x="380" y="620" text-anchor="middle" fill="#ff7a00">7th</text>
      <text x="470" y="540" fill="#ff7a00">8th</text>
      <text x="560" y="430" fill="#ff7a00">9th</text>
      <text x="560" y="320" fill="#ff7a00">10th</text>
      <text x="470" y="210" fill="#ff7a00">11th</text>
      <text x="350" y="360" text-anchor="middle" fill="#ff7a00">
        Rising / 1st
      </text>

    </svg>
    """
    return svg

# ========= NEW: simple wrapper used in UI =========
def generate_north_indian_kundali(pos, lagna_deg, lagna_sign):
    """
    अभी placeholder: सिर्फ़ basic North-Indian chart layout दिखाता है.
    आप चाहें तो बाद में pos/lagna का उपयोग करके ग्रह/राशि भी plot कर सकते हैं।
    """
    return draw_north_indian_kundali_CORRECT()

st.subheader("🪐 जन्म कुंडली (North Indian Style)")

st.components.v1.html(
    generate_north_indian_kundali(pos, lagna_deg, lagna_sign),
    height=720
)
