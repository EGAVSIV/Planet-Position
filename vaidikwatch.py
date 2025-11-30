import streamlit as st
import numpy as np
from PIL import Image
import pygame
import pygame.freetype
import swisseph as swe
import pytz, datetime, math
from streamlit_autorefresh import st_autorefresh

# Auto Refresh every 60 sec
st_autorefresh(interval=60 * 1000)

st.set_page_config(page_title="वेदिक ग्रह घड़ी", layout="wide")

# ------------------------ CONFIG ------------------------
LAT = 19.0760
LON = 72.8777
ELEV = 14

SIGNS = ["मेष","वृषभ","मिथुन","कर्क","सिंह","कन्या",
         "तुला","वृश्चिक","धनु","मकर","कुंभ","मीन"]

NAKSHATRAS=[ ... your same list ... ]

PLANETS={ ... same as before ...}

PLANET_COLOR={ ... same ... }

swe.set_sid_mode(swe.SIDM_LAHIRI,0,0)

# ------------------------ Compute Positions ------------------------
def compute_positions(custom_dt=None):
    if custom_dt is None:
        ist = pytz.timezone("Asia/Kolkata")
        custom_dt = datetime.datetime.now(ist)

    jd = swe.julday(custom_dt.year,
                    custom_dt.month,
                    custom_dt.day,
                    custom_dt.hour + custom_dt.minute/60) - (5.5/24)

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
    return pos,retro,custom_dt

# ---------------- Nakshatra ----------------
def nakshatra_info(lon):
    each=13+1/3
    idx=int(lon//each)%27
    pd=int((lon%each)//(each/4))+1
    return *NAKSHATRAS[idx], pd

# ---------------- DRAW PYGAME CHART ----------------
pygame.init(); pygame.freetype.init()

def draw_chart(pos,retro):
    SIZE = 820
    surf = pygame.Surface((SIZE,SIZE), pygame.SRCALPHA)
    cx=cy=SIZE//2; R=255

    f  = pygame.freetype.SysFont("Nirmala UI",26,bold=True)
    f2 = pygame.freetype.SysFont("Nirmala UI",19,bold=True)

    for r in range(R-40, R+40):
        pygame.draw.circle(
            surf,(10,10+r//4,120+r//3,255),(cx,cy),r,2
        )

    for i in range(12):
        ang = math.radians(90-i*30)
        x = cx+(R+25)*math.cos(ang)
        y = cy-(R+25)*math.sin(ang)
        f.render_to(surf,(x,y),SIGNS[i],(240,240,240))

    for pname in pos:
        sid=pos[pname]
        ang=math.radians(90-sid)
        x = cx+(R-15)*math.cos(ang)
        y = cy-(R-15)*math.sin(ang)

        color = pygame.Color(PLANET_COLOR[pname])
        pygame.draw.circle(surf,color,(int(x),int(y)),22)

        symbol = PLANET_SYMBOL[pname]
        f.render_to(surf,(x-12,y-14),symbol,(0,0,0))

        nak,lord,pd = nakshatra_info(sid)
        f2.render_to(surf,(x-25,y-45),nak,(255,230,160))

        if retro[pname]:
            f2.render_to(surf,(x-6,y+26),"℞",(255,80,80))

    return surf

# ------------------------ UI ------------------------
st.markdown("<h1 style='color:yellow'>वेदिक ग्रह घड़ी</h1>",unsafe_allow_html=True)

# Date + Time Selector
colA,colB,colC = st.columns(3)

sel_date = colA.date_input("Select Date")
sel_time = colB.time_input("Select Time")

if colC.button("Now"):
    sel_date = datetime.date.today()
    sel_time = datetime.datetime.now().time()

# combine selected date + time
dt = datetime.datetime.combine(sel_date, sel_time)

pos,retro,used_time = compute_positions(dt)

col1,col2 = st.columns([1.5,1])

with col1:
    surface = draw_chart(pos,retro)
    arr = pygame.surfarray.array3d(surface)
    arr = np.rot90(arr)
    st.image(arr,use_container_width=True)

with col2:
    st.subheader("ग्रह तालिका")
    rows=[]
    for p in pos:
        lon=pos[p]
        nak,lord,pd=nakshatra_info(lon)
        rows.append([p,
            PLANET_SYMBOL[p],
            f"{lon:.4f}°",
            SIGNS[int(lon//30)],
            nak,
            "Retro" if retro[p] else "Direct"
        ])

    st.dataframe(rows)

st.success("Updated: " + used_time.strftime("%d-%b-%Y %H:%M:%S"))

