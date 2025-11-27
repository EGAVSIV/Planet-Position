import streamlit as st
import numpy as np
from PIL import Image
import pygame
import pygame.freetype
import swisseph as swe
import pytz, datetime, math

# ---------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------
st.set_page_config(page_title="वेदिक ग्रह घड़ी — Streamlit", layout="wide")

LAT = 19.0760
LON = 72.8777
ELEV = 14

SIGNS = ["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या","तुला","वृश्चिक",
         "धनु","मकर","कुंभ","मीन"]

NAKSHATRAS = [
("अश्विनी","केतु"),("भरणी","शुक्र"),("कृत्तिका","सूर्य"),
("रोहिणी","चन्द्र"),("मृगशिरा","मंगल"),("आर्द्रा","राहु"),
("पुनर्वसु","बृहस्पति"),("पुष्य","शनि"),("आश्लेषा","बुध"),
("मघा","केतु"),("पूर्व फाल्गुनी","शुक्र"),("उत्तर फाल्गुनी","सूर्य"),
("हस्त","चन्द्र"),("चित्रा","मंगल"),("स्वाति","राहु"),
("विशाखा","बृहस्पति"),("अनुराधा","शनि"),("ज्येष्ठा","बुध"),
("मूला","केतु"),("पूर्वाषाढा","शुक्र"),("उत्तराषाढा","सूर्य"),
("श्रवण","चन्द्र"),("धनिष्ठा","मंगल"),("शतभिषा","राहु"),
("पूर्वभाद्रपदा","बृहस्पति"),("उत्तरभाद्रपदा","शनि"),("रेवती","बुध"),
]

PLANETS = {
"सूर्य":(swe.SUN,"🜚"),"चन्द्र":(swe.MOON,"☽"),"मंगल":(swe.MARS,"♂"),
"बुध":(swe.MERCURY,"☿"),"बृहस्पति":(swe.JUPITER,"♃"),
"शुक्र":(swe.VENUS,"♀"),"शनि":(swe.SATURN,"♄"),
"राहु":(swe.TRUE_NODE,"☊")
}

PLANET_SYMBOL={
"सूर्य":"🜚","चन्द्र":"☽","मंगल":"♂","बुध":"☿","बृहस्पति":"♃",
"शुक्र":"♀","शनि":"♄","राहु":"☊","केतु":"☋",
}

PLANET_COLOR={
"सूर्य":"#FFB86B","चन्द्र":"#BFE9FF","मंगल":"#FF8A8A","बुध":"#B6FF9C",
"बृहस्पति":"#FFD88A","शुक्र":"#F9B0FF","शनि":"#C0C8FF",
"राहु":"#FFCF66","केतु":"#FFCF66"
}

swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)

# ---------------------------------------------------------------------
# ASTRO
# ---------------------------------------------------------------------
def compute_positions():
    ist = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(ist)
    jd = swe.julday(now.year,now.month,now.day,
                    now.hour+now.minute/60+now.second/3600)-(5.5/24)

    pos={}; retro={}
    for pname,(code,_) in PLANETS.items():
        r=swe.calc_ut(jd,code)
        lon=r[0][0]; sp=r[0][3]
        ay=swe.get_ayanamsa_ut(jd)
        sid=(lon-ay)%360
        pos[pname]=sid
        retro[pname]=(sp<0)

    pos["केतु"]=(pos["राहु"]+180)%360
    retro["केतु"]=retro["राहु"]

    return pos,retro,now

def nakshatra_info(lon):
    each=13+1/3
    idx=int(lon//each)%27
    pd=int((lon%each)//(each/4))+1
    return *NAKSHATRAS[idx], pd

# ---------------------------------------------------------------------
# DRAW planet ring using Pygame (high quality)
# ---------------------------------------------------------------------
pygame.init()
pygame.freetype.init()

def draw_chart(pos,retro):

    SIZE = 820
    surf = pygame.Surface((SIZE,SIZE), pygame.SRCALPHA)
    cx=cy=SIZE//2; R=255

    f  = pygame.freetype.SysFont("Nirmala UI",26,bold=True)
    f2 = pygame.freetype.SysFont("Nirmala UI",19,bold=True)

    # ring gradient
    for r in range(R-40, R+40):
        pygame.draw.circle(
            surf,
            (10,10+r//4,120+r//3,255),
            (cx,cy),
            r,
            width=2
        )

    # signs
    for i in range(12):
        ang = math.radians(90-i*30)
        x = cx+(R+25)*math.cos(ang)
        y = cy-(R+25)*math.sin(ang)
        f.render_to(surf,(x,y),SIGNS[i],(240,240,240))

        pygame.draw.line(
            surf,(240,240,40),
            (cx,cy),
            (cx+(R-15)*math.cos(ang),cy-(R-15)*math.sin(ang)),2
        )

    # planets
    for pname in pos:
        sid=pos[pname]
        ang=math.radians(90-sid)
        x = cx+(R-15)*math.cos(ang)
        y = cy-(R-15)*math.sin(ang)

        color = pygame.Color(PLANET_COLOR[pname])
        pygame.draw.circle(surf,color,(int(x),int(y)),20)

        symbol = PLANET_SYMBOL[pname]
        f.render_to(surf,(x-12,y-14),symbol,(0,0,0))

        nak,lord,pd = nakshatra_info(sid)
        f2.render_to(surf,(x-25,y-45),nak,(255,230,160))

        if retro[pname]:
            pygame.draw.circle(
                surf,(255,60,60,90),(int(x),int(y)),28,3
            )
            f2.render_to(surf,(x-6,y+26),"℞",(255,80,80))

    return surf

# ---------------------------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------------------------
st.title("वेदिक ग्रह घड़ी — Streamlit Version (3D Hindi UI)")

if st.button("Refresh"):
    st.rerun()

pos, retro, now = compute_positions()

col1, col2 = st.columns([1.5,1])

with col1:
    surface = draw_chart(pos,retro)
    arr = pygame.surfarray.array3d(surface)
    arr = np.rot90(arr)
    st.image(arr,use_container_width=True)

with col2:
    st.subheader("Planet Table")
    rows=[]
    for p in pos:
        lon=pos[p]
        nak,lord,pd=nakshatra_info(lon)
        rows.append([
            p,
            PLANET_SYMBOL[p],
            f"{lon:.4f}°",
            SIGNS[int(lon//30)],
            nak,
            "Retro" if retro[p] else "Direct"
        ])
    st.dataframe(rows,
         hide_index=True,
         column_config={
            0:"ग्रह",1:"प्रतीक",2:"Longitude",
            3:"राशि",4:"नक्षत्र",5:"Motion"
         })

st.info("Last updated: " + now.strftime("%d-%b-%Y %H:%M:%S IST"))
