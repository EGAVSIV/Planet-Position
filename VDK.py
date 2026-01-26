
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


def get_true_moon_lon_and_speed(jd):
    ay = swe.get_ayanamsa_ut(jd)

    r, _ = swe.calc_ut(
        jd,
        swe.MOON,
        swe.FLG_SWIEPH | swe.FLG_TRUEPOS | swe.FLG_SPEED
    )

    moon_lon = (r[0] - ay) % 360
    moon_speed = abs(r[3])  # deg/day

    return moon_lon, moon_speed


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

# ================= NORTH INDIAN KUNDALI (FINAL FIXED) =================



HOUSE_BOXES = {
    1:  (360, 200),   # Top-center (Lagna)

    2:  (210, 120),   # Top-left
    12: (500, 120),   # Top-right

    3:  (120, 180),   # Middle-left
    11: (600, 160),   # Middle-right

    4:  (220, 270),   # Inner-left
    7:  (360, 390),   # Center-bottom (inside diamond)
    10: (510, 270),   # Inner-right

    5:  (100, 370),   # Bottom-left
    6:  (210, 420),   # Bottom-center-left
    9:  (560, 380),   # Bottom-right

    8:  (520, 450),   # Bottom tip
}


def rashi_number_from_deg(deg):
    return int(deg // 30) + 1

def planet_house_from_rashi(planet_rashi, lagna_rashi):
    return ((planet_rashi - lagna_rashi) % 12) + 1
def deg_in_rashi(lon):
    return lon % 30




def draw_north_indian_kundali_CORRECT():
    return """
    <svg width="720" height="520" viewBox="0 0 720 520">

    <!-- OUTER RECTANGLE -->
    <rect x="60" y="60" width="600" height="400"
          fill="white" stroke="black" stroke-width="3"/>

    <!-- MAIN DIAMOND -->
    <polygon points="360,60 660,260 360,460 60,260"
             fill="none" stroke="black" stroke-width="3"/>

    <!-- INNER CROSS -->
    <line x1="60" y1="60" x2="660" y2="460"
          stroke="black" stroke-width="3"/>

    <line x1="660" y1="60" x2="60" y2="460"
          stroke="black" stroke-width="3"/>

    </svg>
    """




def generate_lagna_number(lagna_deg):
    lagna_rashi = rashi_number_from_deg(lagna_deg)
    x, y = HOUSE_BOXES[1]
    return f"""
    <text x="{x}" y="{y-18}"
          font-size="16"
          fill="red"
          font-weight="bold"
          text-anchor="middle">
        {lagna_rashi}
    </text>
    """

def generate_rashi_numbers(lagna_deg):
    lagna_rashi = rashi_number_from_deg(lagna_deg)
    svg_txt = ""

    for house, (x, y) in HOUSE_BOXES.items():

        # 🔥 SKIP Lagna house (House 1)
        if house == 1:
            continue

        rashi_num = ((lagna_rashi + house - 2) % 12) + 1

        svg_txt += f"""
        <text x="{x}" y="{y-22}"
              font-size="13"
              fill="#666"
              font-weight="bold"
              text-anchor="middle">
            {rashi_num}
        </text>
        """

    return svg_txt



def generate_north_indian_kundali(pos, lagna_deg):
    lagna_rashi = rashi_number_from_deg(lagna_deg)
    svg = draw_north_indian_kundali_CORRECT()

    house_map = defaultdict(list)

    for planet, lon in pos.items():
        planet_rashi = rashi_number_from_deg(lon)
        house = planet_house_from_rashi(planet_rashi, lagna_rashi)

        house_map[house].append({
            "name": planet,
            "deg": deg_in_rashi(lon),
            "retro": retro.get(planet, False)
        })

    planet_text = ""

    for house, planets in house_map.items():
        x, y = HOUSE_BOXES[house]

        for i, p in enumerate(planets):
            retro_mark = " ℞" if p["retro"] else ""
            planet_text += f"""
            <text x="{x}" y="{y + i*16}"
                  font-size="13"
                  font-weight="500"
                  text-anchor="middle"
                  fill="black">
                {p["name"]} {p["deg"]:.1f}°{retro_mark}
            </text>
            """


    svg = svg.replace(
        "</svg>",
        generate_lagna_number(lagna_deg)
        + generate_rashi_numbers(lagna_deg)
        + planet_text
        + "</svg>"
    )
    return svg


# ================= MAIN KUNDALI =================
st.subheader("🪐 जन्म कुंडली (North Indian Style)")
st.components.v1.html(
    generate_north_indian_kundali(pos, lagna_deg),
    height=720
)

# ================= D9 (NAVAMSHA) =================
MOVABLE = [0,3,6,9]
FIXED   = [1,4,7,10]
DUAL    = [2,5,8,11]

def get_d9_sign(lon):
    rashi = int(lon // 30)
    part  = int((lon % 30) // (30/9))

    if rashi in MOVABLE:
        return (rashi + part) % 12
    elif rashi in FIXED:
        return (rashi + 8 + part) % 12
    else:  # dual
        return (rashi + 4 + part) % 12

def get_d10_sign(lon):
    rashi = int(lon // 30)
    part  = int((lon % 30) // 3)

    if rashi % 2 == 0:
        return (rashi + part) % 12
    else:
        return (rashi + 9 - part) % 12



def get_d9_positions(pos):
    return {p: get_d9_sign(lon) * 30 for p, lon in pos.items()}

def generate_d9_kundali(pos, lagna_deg):
    d9_pos = get_d9_positions(pos)
    d9_lagna_deg = get_d9_sign(lagna_deg) * 30
    return generate_north_indian_kundali(d9_pos, d9_lagna_deg)

def get_d10_positions(pos):
    return {p: get_d10_sign(lon) * 30 for p, lon in pos.items()}


def generate_d10_kundali(pos, lagna_deg):
    d10_pos = get_d10_positions(pos)
    d10_lagna_deg = get_d10_sign(lagna_deg) * 30
    return generate_north_indian_kundali(d10_pos, d10_lagna_deg)



st.subheader("🪐 D9 — नवांश कुंडली")
st.components.v1.html(
    generate_d9_kundali(pos, lagna_deg),
    height=720
)





st.subheader("🪐 D10 — दशांश कुंडली (Career)")
st.components.v1.html(
    generate_d10_kundali(pos, lagna_deg),
    height=720
)



DASHA_SEQ = [
    ("केतु",7), ("शुक्र",20), ("सूर्य",6), ("चन्द्र",10),
    ("मंगल",7), ("राहु",18), ("बृहस्पति",16),
    ("शनि",19), ("बुध",17)
]

DASHA_YEARS = dict(DASHA_SEQ)
TOTAL_VIMSHOTTARI = 120.0
SIDEREAL_YEAR = 365.25636



def vimshottari_dasha(jd, moon_lon):
    # Nakshatra calculation
    nak_index = int(moon_lon // NAK_SIZE)
    lord = NAKSHATRAS[nak_index][1]

    # True Moon longitude + speed
    moon_lon_true, moon_speed = get_true_moon_lon_and_speed(jd)

    # Exact Nakshatra start longitude
    nak_start_lon = nak_index * NAK_SIZE
    delta_deg = (moon_lon_true - nak_start_lon) % NAK_SIZE

    # Nakshatra start JD (Drik method)
    nak_start_jd = jd - (delta_deg / moon_speed)

    start_idx = [p for p, _ in DASHA_SEQ].index(lord)

    dashas = []
    start = nak_start_jd

    for i in range(9):
        planet, years = DASHA_SEQ[(start_idx + i) % 9]
        end = start + years * 365.25636  # sidereal year
        dashas.append((planet, start, end))
        start = end

    return dashas

def compute_sub_dasha(start_jd, main_lord, main_years, level=1, max_level=5):
    """
    level:
    1 = Mahadasha
    2 = Antardasha
    3 = Pratyantar
    4 = Sukshma
    5 = Prana
    """

    seq = [p for p, _ in DASHA_SEQ]
    start_idx = seq.index(main_lord)

    results = []
    curr_start = start_jd

    for i in range(9):
        lord = seq[(start_idx + i) % 9]
        sub_years = (main_years * DASHA_YEARS[lord]) / TOTAL_VIMSHOTTARI
        curr_end = curr_start + sub_years * SIDEREAL_YEAR

        node = {
            "level": level,
            "lord": lord,
            "start": curr_start,
            "end": curr_end
        }

        if level < max_level:
            node["children"] = compute_sub_dasha(
                curr_start,
                lord,
                sub_years,
                level + 1,
                max_level
            )

        results.append(node)
        curr_start = curr_end

    return results





st.subheader("⏳ Vimshottari Mahadasha")

dashas = vimshottari_dasha(jd, pos["चन्द्र"])
rows = []
for p, s, e in dashas:
    rows.append([
        p,
        swe.revjul(s)[0:3],
        swe.revjul(e)[0:3]
    ])

st.table(pd.DataFrame(rows, columns=["दशा", "आरंभ", "समाप्ति"]))

st.subheader("🔹 Antardasha (Current Mahadasha)")

today_jd = jd

# find running Mahadasha
for md_lord, md_start, md_end in dashas:
    if md_start <= today_jd < md_end:
        current_md = (md_lord, md_start, md_end)
        break

antar_tree = compute_sub_dasha(
    start_jd=current_md[1],
    main_lord=current_md[0],
    main_years=DASHA_YEARS[current_md[0]],
    max_level=2
)

antar_rows = []
for a in antar_tree:
    antar_rows.append([
        a["lord"],
        swe.revjul(a["start"])[0:3],
        swe.revjul(a["end"])[0:3]
    ])

st.table(pd.DataFrame(
    antar_rows,
    columns=["अंतर दशा", "आरंभ", "समाप्ति"]
))


st.subheader("🔸 Pratyantar Dasha")

running_antar = None
for a in antar_tree:
    if a["start"] <= today_jd < a["end"]:
        running_antar = a
        break

if running_antar:
    praty_rows = []
    for p in running_antar["children"]:
        praty_rows.append([
            p["lord"],
            swe.revjul(p["start"])[0:3],
            swe.revjul(p["end"])[0:3]
        ])

    st.table(pd.DataFrame(
        praty_rows,
        columns=["प्रत्यंतर", "आरंभ", "समाप्ति"]
    ))



ASHTAKA_RULES = {
    "सूर्य": [1,2,4,7,8,9,10,11],
    "चन्द्र": [2,3,5,6,9,10,11],
    "मंगल": [1,2,4,7,8,9,10,11],
    "बुध": [1,3,5,6,9,10,11],
    "बृहस्पति": [2,5,7,9,10,11],
    "शुक्र": [1,2,3,4,5,8,9,11,12],
    "शनि": [3,5,6,10,11]
}


def calculate_sarvashtakavarga(pos, lagna_deg):
    sav = [0]*12

    for planet, houses in ASHTAKA_RULES.items():
        planet_rashi = rashi_number_from_deg(pos[planet])
        lagna_rashi = rashi_number_from_deg(lagna_deg)
        base_house = planet_house_from_rashi(planet_rashi, lagna_rashi)
        for h in houses:
            sav[(base_house + h - 2) % 12] += 1

    return sav


st.subheader("📊 Sarvashtakavarga")

sav = calculate_sarvashtakavarga(pos, lagna_deg)

df = pd.DataFrame({
    "राशि": SIGNS,
    "अंक": sav
})

st.bar_chart(df.set_index("राशि"))


