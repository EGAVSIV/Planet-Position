import streamlit as st
import swisseph as swe
import datetime, pytz, math

st.set_page_config(page_title="🪐 वेदिक ग्रह घड़ी — वेब संस्करण", layout="wide")

# -------------------------------------
# ASTRO DATA
# -------------------------------------

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
("सूर्य", swe.SUN, "🜚"),
("चन्द्र", swe.MOON,"☽"),
("मंगल", swe.MARS,"♂"),
("बुध", swe.MERCURY,"☿"),
("बृहस्पति", swe.JUPITER,"♃"),
("शुक्र", swe.VENUS,"♀"),
("शनि", swe.SATURN,"♄"),
("राहु", swe.MEAN_NODE,"☊")
]

COL = {
"सूर्य":"#ffcc66","चन्द्र":"#cce6ff","मंगल":"#ff9999",
"बुध":"#ccffcc","बृहस्पति":"#ffe6b3","शुक्र":"#ffccff",
"शनि":"#c2c2ff","राहु":"#ffd27f","केतु":"#ffd27f"
}

swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)

# -------------------------------------
# ASTRO FUNCTIONS
# -------------------------------------

def get_positions(dt):
    jd = swe.julday(dt.year, dt.month, dt.day,
                    dt.hour + dt.minute/60) - 5.5/24
    pos = {}
    for name, code, sym in PLANETS:
        r = swe.calc_ut(jd, code)
        ay = swe.get_ayanamsa_ut(jd)
        pos[name] = (r[0][0] - ay) % 360

    pos["केतु"] = (pos["राहु"] + 180) % 360
    return pos


def nakshatra_of(lon):
    size = 13 + 1/3
    idx = int(lon // size) % 27
    return NAKSHATRAS[idx][0]

# -------------------------------------
# SVG GENERATOR (CIRCULAR CHAKRA)
# -------------------------------------

def generate_svg(pos):

    svg = """
    <svg width="650" height="650" viewBox="0 0 650 650" style="margin:auto; display:block">
        <circle cx="325" cy="325" r="300" stroke="#999" stroke-width="4" fill="none"/>

        <!-- Zodiac Segments -->
    """

    # Draw 12 zodiac divisions
    for i in range(12):
        angle_deg = 90 - (i*30)
        rad = math.radians(angle_deg)
        x = 325 + 300 * math.cos(rad)
        y = 325 - 300 * math.sin(rad)

        svg += f"""
        <line x1="325" y1="325" x2="{x}" y2="{y}"
              stroke="#ffaa00" stroke-width="3"/>
        """

        # Print zodiac name midway
        x2 = 325 + 200 * math.cos(rad)
        y2 = 325 - 200 * math.sin(rad)

        svg += f"""
        <text x="{x2}" y="{y2}" fill="#00e6ff" font-size="22" text-anchor="middle"
              dominant-baseline="middle">{SIGNS[i]}</text>
        """

    # Planets
    for name, code, sym in PLANETS:
        lon = pos[name]
        ang = math.radians(90 - lon)
        px = 325 + 240 * math.cos(ang)
        py = 325 - 240 * math.sin(ang)

        nak = nakshatra_of(lon)
        color = COL[name]

        svg += f"""
        <circle cx="{px}" cy="{py}" r="26" fill="{color}" stroke="black" stroke-width="2"/>
        <text x="{px}" y="{py}" font-size="22" text-anchor="middle"
              dominant-baseline="middle">{sym}</text>

        <text x="{px}" y="{py + 36}" fill="white" font-size="18"
              text-anchor="middle" dominant-baseline="middle">{name}</text>

        <text x="{px}" y="{py - 36}" fill="#fff099" font-size="16"
              text-anchor="middle" dominant-baseline="middle">{nak}</text>
        """

    svg += "</svg>"
    return svg


# -------------------------------------
# STREAMLIT UI
# -------------------------------------

st.title("🪐 वेदिक ग्रह घड़ी — Circular Chakra HTML Version")

col1, col2, col3 = st.columns(3)
date = col1.date_input("तारीख़ चुनें")
time = col2.time_input("समय चुनें")

if col3.button("अब"):
    now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
    date, time = now.date(), now.time()

dt = datetime.datetime.combine(date, time)
pos = get_positions(dt)

# Chakra Output
svg = generate_svg(pos)
st.components.v1.html(svg, height=700)

# Table
st.subheader("ग्रह तालिका")

table = []
for p, code, sym in PLANETS:
    table.append([
        p,
        sym,
        f"{pos[p]:.2f}°",
        SIGNS[int(pos[p]//30)],
        nakshatra_of(pos[p])
    ])

st.table(table)

st.success("समय (IST): " + dt.strftime("%d-%b-%Y %H:%M:%S"))
