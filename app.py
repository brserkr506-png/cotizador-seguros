import streamlit as st
import pandas as pd
import numpy as np
from actuarial import cargar_tabla, calcular_conmutacion, calcular_seguro, calcular_anualidad_primas, calcular_prima_comercial
import json, os, hashlib
from datetime import datetime
import streamlit.components.v1 as components

# ───────────────────────── CONFIGURACIÓN INICIAL ─────────────────────────
st.set_page_config(page_title="RiskMetrics Studio", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

# ───────────────────────── ESTILO CYBER-GLASS Y ANIMACIONES ─────────────────────────
SP = "cubic-bezier(.22,1.25,.36,1)"
ROLL = "".join(f"@keyframes roll{d}{{from{{transform:translateY(0)}}to{{transform:translateY(-{d}em)}}}}.r{d}{{animation-name:roll{d}}}" for d in range(10))

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root{
    --sp:SPRING; --bg:#04070D; --tx:#F4F4F9; --mu:#94A3B8;
    --gl:rgba(15, 23, 42, 0.45); --bd:rgba(0, 229, 255, 0.15); 
    --ac:#00E5FF; --or:#FF6A00; --c1:#00E5FF; --c2:#0055FF; --c3:#1E293B;
    --sh:0 25px 50px -12px rgba(0, 229, 255, 0.15); --inp:rgba(15, 23, 42, 0.6);
    --mx: 50%; --my: 50%;
}

html,body{background:var(--bg);}
.stApp{background:transparent!important; color:var(--tx)}

/* Eliminar fondos grises/márgenes de Streamlit */
div[data-testid="stVerticalBlock"] > div, div[data-testid="stHorizontalBlock"] > div, div[data-testid="stColumn"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

html,body,.stApp,.stApp p,.stApp label,.stApp input,.stApp button,.stApp li,.stApp td,.stApp th,.stApp summary,.stApp h1,.stApp h2,.stApp h3{
    font-family:'Inter', system-ui, sans-serif;
}

/* Fondo animado (Blobs) */
.bg-blobs { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; overflow: hidden; pointer-events: none; }
.blob { position: absolute; filter: blur(120px); opacity: 0.35; border-radius: 50%; }
.blob1 { width: 60vw; height: 60vw; background: #0055FF; top: -20vh; left: -10vw; animation: float1 20s ease-in-out infinite alternate; }
.blob2 { width: 50vw; height: 50vw; background: #00E5FF; bottom: -20vh; right: -10vw; animation: float2 25s ease-in-out infinite alternate; }

@keyframes float1 { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(10vw, 15vh) scale(1.1); } }
@keyframes float2 { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(-15vw, -10vh) scale(1.2); } }

/* Destello que sigue al mouse */
.stApp::before {
    content:""; position:fixed; z-index:0; top:0; left:0; width:100vw; height:100vh;
    background: radial-gradient(circle at var(--mx) var(--my), rgba(0, 229, 255, 0.08) 0%, transparent 50%);
    pointer-events: none; transition: background 0.15s ease-out;
}

header[data-testid=stHeader]{background:transparent}
.block-container{position:relative;z-index:1;padding-top:2.2rem;max-width:1180px}

/* Sidebar de cristal */
[data-testid=stSidebar]{background:var(--gl)!important;backdrop-filter:blur(36px) saturate(1.6);border-right:1px solid var(--bd);border-radius:0 34px 34px 0}
[data-testid=stSidebar] [data-testid=stExpander] details{background:rgba(255,255,255,.03)}

h1,h2,h3{font-weight:700!important;color:var(--tx)!important;letter-spacing:-.02em}

/* Expanders y paneles de cristal */
[data-testid=stExpander] details{border:1px solid var(--bd)!important;border-radius:20px!important;background:var(--gl);backdrop-filter:blur(24px);box-shadow:var(--sh);overflow:hidden;transition:transform .5s var(--sp)}
[data-testid=stExpander] summary{font-weight:600;color:var(--ac);padding:.9rem 1.2rem}
[data-testid=stExpander] summary:hover{background:rgba(0,229,255,.08)}

/* Inputs y Formularios */
[data-baseweb=select]>div,[data-testid=stNumberInputContainer]{border-radius:14px!important;background:var(--inp)!important;color:var(--tx)!important;border:1px solid var(--bd)!important;transition:box-shadow .35s var(--sp),transform .35s var(--sp)}
[data-baseweb=select]>div:hover,[data-testid=stNumberInputContainer]:focus-within{box-shadow:0 0 0 3px rgba(0,229,255,.2);transform:scale(1.01)}
[data-testid=stNumberInput] input{background:transparent!important;color:var(--tx)!important}

[data-testid="stForm"] {background: rgba(10, 15, 30, 0.6); border: 1px solid rgba(255,255,255,0.05); border-radius: 24px; padding: 2.5rem; backdrop-filter: blur(20px); box-shadow: 0 30px 60px -15px rgba(0,0,0,0.8);}
[data-testid="stTextInput"] input {background: rgba(0,0,0,0.4) !important; border: 1px solid rgba(255,255,255,0.08) !important; color: #fff !important; border-radius: 12px !important; padding: 0.8rem 1rem !important; font-size: 1rem !important; transition: all 0.3s ease;}
[data-testid="stTextInput"] input:focus {border-color: var(--ac) !important; box-shadow: 0 0 15px rgba(0,229,255,0.2) !important; background: rgba(0,0,0,0.6) !important;}

/* Tabs del Login */
[data-testid=stTabs] [role=tablist]{gap:4px;background:rgba(0,0,0,0.4);padding:5px;border-radius:12px;border:1px solid rgba(255,255,255,0.05);width:100%;justify-content:center}
[data-testid=stTabs] [role=tab]{color:var(--mu);font-weight:600;border-radius:8px;padding:.5rem 1.5rem;transition:all .3s ease;flex:1;text-align:center;}
[data-testid=stTabs] [aria-selected=true]{background:rgba(255,255,255,0.1);color:#FFF;box-shadow:0 2px 10px rgba(0,0,0,0.2)}
[data-testid=stTabs] [data-baseweb=tab-highlight],[data-testid=stTabs] [data-baseweb=tab-border]{display:none}

/* ── LOGO ANIMADO ── */
.logo-wrapper { display: flex; flex-direction: column; align-items: center; text-align: center; }
.svg-logo { width: 320px; height: 320px; filter: drop-shadow(0 0 30px rgba(0,229,255,0.2)); transition: transform 0.1s ease-out; margin-bottom: 1rem; }

/* Anillos base */
.ring-bg { fill: none; stroke: rgba(0,229,255,0.08); stroke-width: 1; stroke-dasharray: 2 6; }
.ring-spin { fill: none; stroke: rgba(0,229,255,0.05); stroke-width: 1; transform-origin: center; animation: spin 15s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* Secuencia fluida (16s total) */
.frag { opacity: 0; transform-origin: center; animation-duration: 16s; animation-iteration-count: infinite; animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1); }
.f1 { animation-name: seq1; }
.f2 { animation-name: seq2; }
.f3 { animation-name: seq3; }
.f4 { animation-name: seq4; }

/* Trazo general */
.draw-loop { stroke-dasharray: 5000; stroke-dashoffset: 5000; }
.f1 .draw-loop { animation: draw1 16s linear infinite; }
.f2 .draw-loop { animation: draw2 16s linear infinite; }
.f3 .draw-loop { animation: draw3 16s linear infinite; }

/* Tiempos de visibilidad y transición */
@keyframes seq1 { 0%, 20% { opacity: 1; transform: scale(1); } 25%, 100% { opacity: 0; transform: scale(1.03); } }
@keyframes seq2 { 0%, 20% { opacity: 0; transform: scale(0.97); } 25%, 45% { opacity: 1; transform: scale(1); } 50%, 100% { opacity: 0; transform: scale(1.03); } }
@keyframes seq3 { 0%, 45% { opacity: 0; transform: scale(0.97); } 50%, 70% { opacity: 1; transform: scale(1); } 75%, 100% { opacity: 0; transform: scale(1.03); } }
@keyframes seq4 { 0%, 70% { opacity: 0; transform: scale(0.97); } 75%, 95% { opacity: 1; transform: scale(1); } 100% { opacity: 0; transform: scale(1.03); } }

@keyframes draw1 { 0% { stroke-dashoffset: 5000; } 15% { stroke-dashoffset: 0; } 100% { stroke-dashoffset: 0; } }
@keyframes draw2 { 0%, 20% { stroke-dashoffset: 5000; } 40% { stroke-dashoffset: 0; } 100% { stroke-dashoffset: 0; } }
@keyframes draw3 { 0%, 45% { stroke-dashoffset: 5000; } 65% { stroke-dashoffset: 0; } 100% { stroke-dashoffset: 0; } }

/* Animación del ECG (Cardiograma) */
.ecg-line { stroke-dasharray: 300; stroke-dashoffset: 300; animation: drawECG 3.2s linear infinite; }
@keyframes drawECG { 0% { stroke-dashoffset: 300; } 50%, 100% { stroke-dashoffset: -300; } }
.heart { animation: heartPulse 1.6s ease-in-out infinite; transform-origin: center; }
@keyframes heartPulse { 0%, 100% { transform: scale(1); filter: drop-shadow(0 0 10px rgba(0,229,255,0.5)); } 15% { transform: scale(1.05); filter: drop-shadow(0 0 20px rgba(0,229,255,0.8)); } 30% { transform: scale(1); filter: drop-shadow(0 0 10px rgba(0,229,255,0.5)); } 45% { transform: scale(1.03); filter: drop-shadow(0 0 15px rgba(0,229,255,0.7)); } }

/* Puntitos de dispersión */
.dot-anim { animation: dotPulse 2s infinite alternate; }
@keyframes dotPulse { 0% { r: 3; opacity: 0.7; } 100% { r: 6; opacity: 1; } }

/* Clases generales */
.gl{background:var(--gl);backdrop-filter:blur(28px) saturate(1.5);border:1px solid var(--bd);border-radius:28px;box-shadow:var(--sh);padding:1.6rem 1.8rem;transition:transform .5s var(--sp)}
.gl:hover{transform:translateY(-3px) scale(1.004)}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:.2rem 0 1.2rem}
.chip{padding:.38rem .95rem;border-radius:999px;background:rgba(0, 229, 255, 0.1);border:1px solid var(--bd);font-size:.95rem;font-weight:600;color:var(--ac);backdrop-filter:blur(16px)}
.hero{display:grid;grid-template-columns:1.5fr 1fr;gap:1.5rem;align-items:center;margin-bottom:1rem}
@media(max-width:760px){.hero{grid-template-columns:1fr}}
.lb{color:var(--mu);font-size:1.02rem;font-weight:600}
.sub{color:var(--mu);margin-top:.7rem;font-size:1.05rem;font-weight:500}
.vacio { text-align: center; padding: 3rem 1.8rem; display: flex; flex-direction: column; gap: 0.5rem; align-items: center; justify-content: center; }
.vacio b { font-size: 1.3rem; font-weight: 700; }
.vacio span { color: var(--mu); font-size: 1.05rem; }

/* Odómetro */
.odo{display:flex;align-items:flex-end;font-size:clamp(46px,7.5vw,96px);font-weight:700;letter-spacing:-.03em;line-height:1;font-variant-numeric:tabular-nums;color:var(--ac);margin-top:.3rem; text-shadow: 0 0 20px rgba(0,229,255,.4)}
.odo .dg{display:inline-block;height:1em;overflow:hidden}
.odo .st{display:flex;flex-direction:column;animation-duration:1.15s;animation-timing-function:SPRING;animation-fill-mode:both}
.odo i{display:block;height:1em;font-style:normal}
.odo .sp{display:inline-block;height:1em}
ROLL

/* Gráficos y barras */
.ringw{display:flex;gap:1.3rem;align-items:center;justify-content:center;flex-wrap:wrap}
.ring-c{width:150px;height:150px;border-radius:50%;background:conic-gradient(var(--c1) 0 var(--a),var(--c2) var(--a) var(--b),var(--c3) var(--b) 360deg);-webkit-mask:radial-gradient(circle,transparent 57%,#000 58%);mask:radial-gradient(circle,transparent 57%,#000 58%);animation:sweep 1.4s SPRING both}
@keyframes sweep{from{--a:0deg;--b:0deg;transform:rotate(-90deg) scale(.8)}to{transform:rotate(0) scale(1)}}
.lg{display:flex;flex-direction:column;gap:.5rem;font-size:1.02rem;font-weight:500;color:var(--tx)}
.lg span::before{content:"";display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:8px;background:var(--k)}

/* Barras de comparación */
.row{display:grid;grid-template-columns:150px 1fr 110px;gap:.9rem;align-items:center;margin:.7rem 0;font-size:1.02rem;font-weight:500;color:var(--tx)}
.bar{height:18px;border-radius:99px;background:rgba(130,140,170,.18);overflow:hidden}
.bar b{display:block;height:100%;width:var(--w);border-radius:99px;background:linear-gradient(90deg,#7FB2FF,var(--ac));animation:grow 1.1s SPRING both}
.row.on .bar b{background:linear-gradient(90deg,#FFB27A,var(--or))}
@keyframes grow{from{width:0}}

/* Píldoras de verificación */
.pill{display:inline-block;padding:.25rem .8rem;border-radius:99px;font-size:.8rem;font-weight:600}
.ok{background:rgba(30,160,100,.2);color:#4ADE80;border:1px solid #4ADE80}
.no{background:rgba(230,60,50,.2);color:#F87171;border:1px solid #F87171}
.chk{display:flex;justify-content:space-between;align-items:center;gap:1rem;padding:.8rem 0;border-bottom:1px solid var(--bd)}
.chk small{color:var(--mu);display:block; font-size: 0.85rem; margin-top: 2px}

/* Gráficos SVG (Sensibilidad y Mortalidad) */
svg.ch{width:100%;height:auto;overflow:visible}
.ch .ln{fill:none;stroke:var(--ac);stroke-width:3;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;animation:draw 1.6s ease-out both}
@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
.ch .ar{fill:url(#g);animation:fi 1.6s ease both}
.ch .mk{fill:var(--or);stroke:var(--bg);stroke-width:3;animation:fi 1s 1.1s both}
.ch text{fill:var(--tx);font-size:13px;font-weight:600}
@keyframes fi{from{opacity:0}}

/* Botones principales */
button[data-testid=stBaseButton-primary]{background:linear-gradient(135deg,#00E5FF,#0055FF)!important;color:#FFF!important;border:0!important;border-radius:14px!important;font-weight:700!important;font-size:1.05rem!important;min-height:3rem;box-shadow:0 10px 20px -10px rgba(0,229,255,.5);transition:transform .35s SPRING}
button[data-testid=stBaseButton-primary]:hover{transform:translateY(-2px);box-shadow:0 15px 25px -10px rgba(0,229,255,.7)}
button[data-testid=stBaseButton-secondary]{background:rgba(255,255,255,.05)!important;color:var(--tx)!important;border:1px solid var(--bd)!important;border-radius:14px!important;font-weight:600!important}
</style>""".replace("SPRING", SP).replace("ROLL", ROLL)

st.markdown(CSS, unsafe_allow_html=True)

# ───────────────────────── FONDO ANIMADO GLOBAL ─────────────────────────
st.markdown('<div class="bg-blobs"><div class="blob blob1"></div><div class="blob blob2"></div></div>', unsafe_allow_html=True)

# ───────────────────────── SCRIPT DE REACTIVIDAD Y ANTI-TRADUCCIÓN ─────────────────────────
components.html("""
<script>
const d = window.parent.document;
d.documentElement.lang = 'es';
d.documentElement.setAttribute('translate', 'no');
d.documentElement.classList.add('notranslate');
d.body.classList.add('notranslate');

// Forzar metadatos de no traducción
let meta = d.createElement('meta');
meta.name = "google";
meta.content = "notranslate";
d.head.appendChild(meta);

d.addEventListener('mousemove', (e) => {
    const x = e.clientX / window.innerWidth;
    const y = e.clientY / window.innerHeight;
    d.documentElement.style.setProperty('--mx', (x * 100) + '%');
    d.documentElement.style.setProperty('--my', (y * 100) + '%');
    const logo = d.querySelector('.svg-logo');
    if (logo) { logo.style.transform = `translate(${x * 20 - 10}px, ${y * 20 - 10}px)`; }
});
</script>
""", height=0)

# ───────────────────────── RUTAS Y BASE DE DATOS (JSON) ─────────────────────────
DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILE = os.path.join(DIR, "usuarios.json")
HIST_FILE = os.path.join(DIR, "historial_cotizaciones.json")

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def cargar_json(ruta, defecto):
    if not os.path.exists(ruta): return defecto
    try:
        with open(ruta, "r", encoding="utf-8") as f: return json.load(f)
    except: return defecto

def guardar_json(ruta, data):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ───────────────────────── NÚCLEO DE CÁLCULO (ACTUARIAL) ─────────────────────────
ORIGEN = {"CSO 41": "Primera tabla estándar de la NAIC (experiencia 1930–40). Mortalidad alta, primas mayores.",
          "CSO 58": "Experiencia 1950–54. Tabla compuesta (sin distinción de sexo).",
          "GAM-71": "Tabla de rentas de grupo: menor mortalidad; contraste, no tarificación por defecto.",
          "CSO 80": "Experiencia 1970–75. Primera con tasas por sexo.",
          "CET 58": "Tabla de seguro prorrogado (no forfeiture). Base comparativa."}

@st.cache_data
def tabla(nombre):
    return cargar_tabla("Tablas.xlsx", nombre)

def cotizar(tab, x, S, i, mod, n, fp, h, m, a, b, g, u, f):
    ea, q, l, d = tabla(tab)
    e0 = int(ea[0])
    D, C, N, M = calcular_conmutacion(ea, l, d, i)
    vpa = calcular_seguro(x, n, mod, 1.0, D, C, M, e0)
    tot = calcular_seguro(x, n, mod, S, D, C, M, e0)
    dd = 1.0 if fp == "Prima Única" else calcular_anualidad_primas(x, n, fp, h, m, mod, D, N, e0)
    pn = tot / dd
    pc = calcular_prima_comercial(pn, a, b, g, u, f)
    return dict(vpa=vpa, tot=tot, dd=dd, pn=pn, pc=pc, D=D, C=C, N=N, M=M, e0=e0)

@st.cache_data
def pc_solo(*args):
    try: return float(cotizar(*args)["pc"])
    except: return None

def odo(txt):
    o = ""
    for k, ch in enumerate(txt):
        if ch.isdigit():
            o += f'<span class="dg"><span class="st r{ch}" style="animation-delay:{k*55}ms">' + "".join(f"<i>{j}</i>" for j in range(10)) + "</span></span>"
        else:
            o += f'<span class="sp">{ch}</span>'
    return f'<div class="odo">{o}</div>'

def lineas(xs, ys, mx, fx, fy):
    pts = [(x, y) for x, y in zip(xs, ys) if y is not None]
    if len(pts) < 2: return '<p class="lb">Sin datos suficientes en este rango.</p>'
    xs, ys = zip(*pts)
    W, H, P = 640, 230, 34
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    y1 = y1 if y1 > y0 else y0 + 1
    px = lambda v: P + (v - x0) / ((x1 - x0) or 1) * (W - 2 * P)
    py = lambda v: H - P - (v - y0) / (y1 - y0) * (H - 2 * P)
    d = "M" + " L".join(f"{px(a):.1f},{py(b):.1f}" for a, b in pts)
    ar = d + f" L{px(xs[-1]):.1f},{H-P} L{px(xs[0]):.1f},{H-P}Z"
    k = min(range(len(xs)), key=lambda j: abs(xs[j] - mx))
    return (f'<svg class="ch" viewBox="0 0 {W} {H}"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#00E5FF" stop-opacity=".35"/><stop offset="1" stop-color="#00E5FF" stop-opacity="0"/></linearGradient></defs>'
            f'<path class="ar" d="{ar}"/><path class="ln" pathLength="1" d="{d}"/><circle class="mk" cx="{px(xs[k]):.1f}" cy="{py(ys[k]):.1f}" r="7"/>'
            f'<text x="{P}" y="{H-8}">{fx(xs[0])}</text><text x="{W-P}" y="{H-8}" text-anchor="end">{fx(xs[-1])}</text>'
            f'<text x="{px(xs[k]):.1f}" y="{py(ys[k])-14:.1f}" text-anchor="middle" style="fill:var(--tx);font-weight:500">{fy(ys[k])}</text>'
            f'<text x="{P}" y="14">{fy(y1)}</text><text x="{P}" y="{H-P-6}">{fy(y0)}</text></svg>')

def L(s):
    st.latex(s.replace(",", "{,}"))

def selector(lado, etiqueta, opciones, fmt=str):
    ss.setdefault(etiqueta, opciones[0])
    if hasattr(st, "segmented_control"):
        return lado.segmented_control(etiqueta, opciones, format_func=fmt, key=etiqueta) or opciones[0]
    return lado.radio(etiqueta, opciones, horizontal=True, format_func=fmt, key=etiqueta)


# ───────────────────────── SISTEMA DE AUTENTICACIÓN ─────────────────────────
ss = st.session_state
if "usuario" not in ss:
    ss.usuario = None

if ss.usuario is None:
    st.markdown('<div style="height: 8vh;"></div>', unsafe_allow_html=True)
    col_logo, col_form = st.columns([1.2, 1], gap="large")
    
    with col_logo:
        logo_html = '''<div class="logo-wrapper"><svg class="svg-logo" viewBox="0 0 200 200"><defs>
<linearGradient id="gradLine1" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#00E5FF" /><stop offset="100%" stop-color="#0055FF" /></linearGradient>
<linearGradient id="gradArea" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" stop-color="rgba(0,229,255,0.3)" /><stop offset="100%" stop-color="rgba(0,229,255,0)" /></linearGradient>
<linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="rgba(0,229,255,0.15)" /><stop offset="100%" stop-color="rgba(0,85,255,0.4)" /></linearGradient>
</defs>
<circle cx="100" cy="100" r="95" class="ring-bg"/><circle cx="100" cy="100" r="85" class="ring-spin"/>
<g class="frag f1"><path d="M 30,160 L 170,160 M 30,160 L 30,30" fill="none" stroke="rgba(0,229,255,0.15)" stroke-width="1.5" stroke-dasharray="4 4" class="draw-loop"/><path d="M 30,140 Q 60,60 100,100 T 170,50 L 170,160 L 30,160 Z" fill="url(#gradArea)" opacity="0.6"/><path d="M 30,140 Q 60,60 100,100 T 170,50" fill="none" stroke="url(#gradLine1)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="draw-loop"/><circle cx="100" cy="100" r="4" fill="#FFF"/><circle cx="170" cy="50" r="5" fill="#00E5FF"/></g>
<g class="frag f2"><path d="M 30,160 L 170,160 M 30,160 L 30,30" fill="none" stroke="rgba(0,229,255,0.15)" stroke-width="1.5" stroke-dasharray="4 4" class="draw-loop"/><circle cx="50" cy="120" r="5" fill="#00E5FF" class="dot-anim" style="animation-delay:0s"/><circle cx="80" cy="80" r="6" fill="#0055FF" class="dot-anim" style="animation-delay:0.2s"/><circle cx="110" cy="130" r="4" fill="#00E5FF" class="dot-anim" style="animation-delay:0.4s"/><circle cx="140" cy="60" r="7" fill="#0055FF" class="dot-anim" style="animation-delay:0.6s"/><circle cx="160" cy="100" r="5" fill="#00E5FF" class="dot-anim" style="animation-delay:0.8s"/><circle cx="90" cy="50" r="3" fill="#FFF" opacity="0.8" class="dot-anim" style="animation-delay:1s"/></g>
<g class="frag f3"><path d="M 100,20 L 160,40 Q 160,110 100,180 Q 40,110 40,40 Z" fill="url(#shieldGrad)" stroke="#00E5FF" stroke-width="2.5" stroke-linejoin="round" class="draw-loop"/><path d="M 100,40 L 140,55 Q 140,100 100,150 Q 60,100 60,55 Z" fill="none" stroke="rgba(0,229,255,0.4)" stroke-width="1.5" stroke-linejoin="round" class="draw-loop"/><line x1="100" y1="20" x2="100" y2="180" stroke="#FFF" stroke-opacity="0.5" stroke-width="1.5"/></g>
<g class="frag f4"><g class="heart"><path d="M 100,170 C 100,170 30,115 30,65 C 30,25 75,20 100,55 C 125,20 170,25 170,65 C 170,115 100,170 100,170 Z" fill="rgba(0,229,255,0.08)" stroke="#00E5FF" stroke-width="3" stroke-linejoin="round"/><path d="M 40,100 L 70,100 L 85,60 L 105,140 L 120,100 L 160,100" fill="none" stroke="#FFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="ecg-line" style="filter: drop-shadow(0 0 6px #00E5FF);"/></g></g>
</svg>
<h1 style="text-align:center; margin-top:1rem; font-size:3.5rem; background:-webkit-linear-gradient(45deg, #FFFFFF, #00E5FF); -webkit-background-clip:text; -webkit-text-fill-color:transparent; letter-spacing:-1.5px; font-weight:800; line-height:1.1;">RiskMetrics<br/>Studio</h1>
<p style="text-align:center; color:#94A3B8; font-size:1.15rem; max-width:380px; margin-top:1rem; line-height:1.6; font-weight:300;">Plataforma inteligente para la gestión y tarificación de riesgos de seguros de vida.</p>
</div>'''
        st.markdown(logo_html, unsafe_allow_html=True)
        
    with col_form:
        st.markdown('<div style="height: 5vh;"></div>', unsafe_allow_html=True)
        st.markdown("<h2 style='margin-bottom: 1rem; font-weight: 700; color: #F4F4F9; font-size: 2rem;'>Acceso Seguro</h2>", unsafe_allow_html=True)
        tab_login, tab_reg = st.tabs(["Iniciar Sesión", "Registrarse"])
        
        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Correo electrónico", placeholder="tu@correo.com")
                password = st.text_input("Contraseña", type="password", placeholder="••••••••")
                st.write("")
                btn_login = st.form_submit_button("Entrar a la plataforma", type="primary", use_container_width=True)
                if btn_login:
                    users = cargar_json(USER_FILE, {})
                    if email in users and users[email]["password"] == hash_pw(password):
                        ss.usuario = email
                        ss.nombre = users[email]["nombre"]
                        ss.vista = "cotizador"
                        ss.calc = None
                        ss.err = None
                        st.rerun()
                    else:
                        st.error("Credenciales incorrectas.")
                        
        with tab_reg:
            with st.form("reg_form"):
                nombre = st.text_input("Nombre completo", placeholder="Ej. Ana Pérez")
                email_reg = st.text_input("Correo electrónico", placeholder="tu@correo.com")
                password_reg = st.text_input("Contraseña", type="password", placeholder="Crea una contraseña segura")
                st.write("")
                btn_reg = st.form_submit_button("Crear cuenta nueva", type="primary", use_container_width=True)
                if btn_reg:
                    users = cargar_json(USER_FILE, {})
                    if email_reg in users:
                        st.error("El correo ya está registrado.")
                    elif not nombre or not email_reg or not password_reg:
                        st.warning("Completa todos los campos.")
                    else:
                        users[email_reg] = {"nombre": nombre, "password": hash_pw(password_reg)}
                        guardar_json(USER_FILE, users)
                        st.success("Cuenta creada. Procede a iniciar sesión.")
    st.stop()

# ───────────────────────── ESTADO E HISTORIAL (SOLO LOGUEADOS) ─────────────────────────
FREC = {"Semestral": 2, "Trimestral": 4, "Mensual": 12}
FREC_INV = {v: k for k, v in FREC.items()}
MAX_HIST = 200

def leer_historial_usuario():
    datos_globales = cargar_json(HIST_FILE, {})
    if not isinstance(datos_globales, dict): datos_globales = {}
    return datos_globales.get(ss.usuario, [])

def guardar_historial_usuario():
    datos_globales = cargar_json(HIST_FILE, {})
    if not isinstance(datos_globales, dict): datos_globales = {}
    datos_globales[ss.usuario] = ss.hist
    guardar_json(HIST_FILE, datos_globales)

# Valores por defecto en 0 / mínimos
DEFECTOS = {"k_tabla": list(ORIGEN)[0], "k_edad": 0, "k_suma": 0.0, "k_tasa": 0.00, "k_plazo": 1,
            "k_fp": "Prima Única", "k_h": 1, "k_alfa": 0.0, "k_beta": 0.0, "k_gamma": 0.0,
            "k_util": 0.0, "k_gf": 0.0}

for k, v in DEFECTOS.items():
    ss.setdefault(k, v)

ss.setdefault("vista", "cotizador")
ss.setdefault("calc", None)
ss.setdefault("err", None)

if "hist" not in ss:
    ss.hist = leer_historial_usuario()

def ir(vista):
    ss.vista = vista

def restaurar(eid):
    e = next((x for x in ss.hist if x["id"] == eid), None)
    if e is None: return
    p = e["p"]
    ss.k_tabla, ss.k_edad, ss.k_suma, ss.k_tasa = p["tabla"], int(p["edad"]), float(p["suma"]), float(p["tasa"])
    ss["Modalidad"], ss.k_plazo, ss.k_fp, ss.k_h = p["modalidad"], int(p["plazo"]), p["fp"], int(p["h"])
    ss["Frecuencia"] = FREC_INV.get(int(p["m"]), "Semestral")
    ss.k_alfa, ss.k_beta, ss.k_gamma = float(p["alfa"]), float(p["beta"]), float(p["gamma"])
    ss.k_util, ss.k_gf = float(p["utilidad"]), float(p["gasto_fijo"])
    ss.calc = dict(p)
    ss.err = None
    ss.vista = "cotizador"

def borrar_historial():
    ss.hist = []
    guardar_historial_usuario()

# ───────────────────────── PANEL DE CONTROL (SIDEBAR) ─────────────────────────
sb = st.sidebar
sb.markdown("### Centro de control")
with sb.expander("Asegurado y tabla", expanded=False):
    tabla_op = st.selectbox("Tabla de mortalidad", list(ORIGEN), key="k_tabla")
    st.caption(ORIGEN[tabla_op])
    ea_, *_ = tabla(tabla_op)
    edad_min_t, edad_max = int(ea_[0]), int(ea_[-1])
    ss.k_edad = max(edad_min_t, min(int(ss.k_edad), edad_max))
    edad = st.number_input("Edad del asegurado (x)", min_value=edad_min_t, max_value=edad_max, step=1, key="k_edad")
    suma_asegurada = st.number_input("Suma asegurada ($)", min_value=0.0, step=1000.0, key="k_suma")
    tasa_tecnica = st.slider("Tasa de interés técnica (i)", 0.00, 0.15, step=0.005, format="%.3f", key="k_tasa")
    
with sb.expander("Cobertura", expanded=False):
    modalidad = selector(st, "Modalidad", ["Temporal", "Vida Entera", "Dotal"])
    plazo = 1
    if modalidad in ["Temporal", "Dotal"]:
        plazo = st.slider("Plazo del seguro (n años)", 1, 50, key="k_plazo")
        
with sb.expander("Forma de pago", expanded=False):
    forma_pago = st.selectbox("Forma de pago de prima", ["Prima Única", "Prima Nivelada", "Prima Limitada", "Prima Fraccionada"], key="k_fp")
    h, m = 1, 1
    if forma_pago == "Prima Limitada":
        ss.k_h = max(1, min(int(ss.k_h), plazo))
        h = st.slider("Plazo de pago limitado (h años)", 1, plazo, key="k_h")
    if forma_pago == "Prima Fraccionada":
        fr = selector(st, "Frecuencia", ["Semestral", "Trimestral", "Mensual"])
        m = FREC[fr]
        
with sb.expander("Recargos y gastos", expanded=False):
    alfa = st.slider("Adquisición (α)", 0.0, 0.5, step=0.01, key="k_alfa")
    beta = st.slider("Administración (β)", 0.0, 0.2, step=0.01, key="k_beta")
    gamma = st.slider("Cobranza (γ)", 0.0, 0.2, step=0.01, key="k_gamma")
    utilidad = st.slider("Margen de utilidad (u)", 0.0, 0.3, step=0.01, key="k_util")
    gasto_fijo = st.number_input("Gasto fijo por póliza ($)", min_value=0.0, step=10.0, key="k_gf")

vivo = dict(tabla=tabla_op, edad=int(edad), suma=float(suma_asegurada), tasa=float(tasa_tecnica), modalidad=modalidad,
            plazo=int(plazo), fp=forma_pago, h=int(h), m=int(m), alfa=float(alfa), beta=float(beta),
            gamma=float(gamma), utilidad=float(utilidad), gasto_fijo=float(gasto_fijo))

with sb.container(key="acciones"):
    calcular = st.button("Calcular cotización", type="primary", use_container_width=True, key="btn_calc")
    if ss.vista == "historial":
        st.button("Volver al cotizador", use_container_width=True, key="btn_volver", on_click=ir, args=("cotizador",))
    else:
        st.button(f"Ver historial ({len(ss.hist)})", use_container_width=True, key="btn_hist", on_click=ir, args=("historial",))
    
    st.divider()
    st.caption(f"Sesión: **{ss.nombre}**")
    if st.button("Cerrar Sesión", use_container_width=True, type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ───────────────────────── EJECUCIÓN DEL CÁLCULO ─────────────────────────
if calcular:
    ss.err = None
    if edad <= 0 or suma_asegurada <= 0 or (modalidad != "Vida Entera" and plazo <= 0):
        ss.err = "Asegúrate de ingresar una edad, suma asegurada y plazo mayores a 0."
    elif alfa + beta + gamma + utilidad >= 1:
        ss.err = "α + β + γ + u debe ser menor que 1 para que la prima comercial exista."
    elif modalidad != "Vida Entera" and edad + plazo > edad_max:
        ss.err = f"La edad + plazo ({edad + plazo}) excede la edad terminal de {tabla_op} ({edad_max}). Reduce el plazo."
    else:
        try:
            rr = cotizar(tabla_op, edad, suma_asegurada, tasa_tecnica, modalidad, plazo, forma_pago, h, m, alfa, beta, gamma, utilidad, gasto_fijo)
            ss.calc = dict(vivo)
            ss.vista = "cotizador"
            if not ss.hist or ss.hist[-1]["p"] != vivo:
                ss.hist.append(dict(id=(max([e["id"] for e in ss.hist]) + 1) if ss.hist else 1,
                                    fecha=datetime.now().strftime("%d/%m/%Y %H:%M"),
                                    p=dict(vivo), pn=float(rr["pn"]), pc=float(rr["pc"])))
                ss.hist = ss.hist[-MAX_HIST:]
                guardar_historial_usuario()
            st.toast("Cotización calculada y guardada en tu historial", icon="✅")
        except Exception as e:
            ss.err = f"Se ha producido un error en la ejecución del cálculo: {e}"

# ───────────────────────── ENCABEZADO Y VISTA DE HISTORIAL ─────────────────────────
st.markdown("# Cotizador de seguros de vida")
if ss.err:
    st.error(ss.err)

if ss.vista == "historial":
    st.markdown("## Historial de cálculos")
    if not ss.hist:
        st.markdown('<div class="gl vacio"><b>Aún no hay cálculos</b><span>Configura una póliza y presiona «Calcular cotización»; aparecerá aquí.</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="sub" style="margin:0 0 1rem">{len(ss.hist)} cotizaciones guardadas. Toca una para volver al cotizador con esos datos ya cargados.</div>', unsafe_allow_html=True)
        with st.container(key="hist"):
            for e in reversed(ss.hist):
                p = e["p"]
                plz = f" {p['plazo']} años" if p["modalidad"] != "Vida Entera" else ""
                pago = p["fp"] + (f" ({p['m']} pagos/año)" if p["fp"] == "Prima Fraccionada" else "") + (f" {p['h']} años" if p["fp"] == "Prima Limitada" else "")
                st.button(f"**{p['modalidad']}{plz}** · {pago} · {p['tabla']}  \n"
                          f"Edad {p['edad']} · Suma ${p['suma']:,.0f} · i = {p['tasa']*100:.2f}% · Prima comercial **${e['pc']:,.2f}** · {e['fecha']}",
                          key=f"h_{e['id']}", use_container_width=True, on_click=restaurar, args=(e["id"],))
        st.write("")
        st.button("Borrar historial", key="btn_borrar", on_click=borrar_historial)
    st.stop()

# ───────────────────────── RESULTADOS (DEL ÚLTIMO CÁLCULO) ─────────────────────────
if ss.calc is None:
    st.markdown('<div class="gl vacio"><b>Configura la póliza y presiona «Calcular cotización»</b><span>Los datos se ajustan en el Centro de control, a la izquierda. El resultado aparecerá aquí.</span></div>', unsafe_allow_html=True)
    st.stop()

cal = ss.calc
if cal != vivo:
    st.markdown('<div class="nota">Cambiaste datos en el panel: presiona «Calcular cotización» para actualizar el resultado.</div>', unsafe_allow_html=True)

tabla_op, edad, suma_asegurada, tasa_tecnica = cal["tabla"], cal["edad"], cal["suma"], cal["tasa"]
modalidad, plazo, forma_pago, h, m = cal["modalidad"], cal["plazo"], cal["fp"], cal["h"], cal["m"]
alfa, beta, gamma, utilidad, gasto_fijo = cal["alfa"], cal["beta"], cal["gamma"], cal["utilidad"], cal["gasto_fijo"]
ea_, *_ = tabla(tabla_op)
edad_max = int(ea_[-1])
s_rec = alfa + beta + gamma + utilidad
args = (tabla_op, edad, suma_asegurada, tasa_tecnica, modalidad, plazo, forma_pago, h, m, alfa, beta, gamma, utilidad, gasto_fijo)
r = cotizar(*args)

pn, pc, dd = r["pn"], r["pc"], r["dd"]
rec, fijo = s_rec * pc, gasto_fijo
a1 = 360 * pn / pc
a2 = a1 + 360 * rec / pc
per = {"Prima Única": "pago único", "Prima Nivelada": "por año", "Prima Limitada": f"por año durante {h} años", "Prima Fraccionada": f"por año · {m} pagos de ${pc/m:,.2f}"}[forma_pago]
chips = [tabla_op, modalidad + (f" · {plazo} años" if modalidad != "Vida Entera" else ""), forma_pago, f"x = {edad}", f"i = {tasa_tecnica*100:.2f}%"]
st.markdown('<div class="chips">' + "".join(f'<span class="chip">{c}</span>' for c in chips) + '</div>'
            + f'<div class="hero"><div class="gl"><div class="lb">Prima comercial</div>{odo(f"{pc:,.2f}")}<div class="sub">${"{:,.0f}".format(suma_asegurada)} de suma asegurada · {per}</div></div>'
            + f'<div class="gl"><div class="ringw"><div class="ring-c" style="--a:{a1:.1f}deg;--b:{a2:.1f}deg"></div><div class="lg">'
            + f'<span style="--k:var(--c1)">Prima neta ${pn:,.2f}</span><span style="--k:var(--c2)">Recargos ${rec:,.2f}</span><span style="--k:var(--c3)">Gasto fijo ${fijo:,.2f}</span></div></div></div></div>'
            + f'<div class="stats"><div class="gl"><span class="lb">Valor presente actuarial (A)</span><b>{r["vpa"]:.6f}</b></div>'
            + f'<div class="gl"><span class="lb">Factor de anualidad (ä)</span><b>{dd:.4f}</b></div>'
            + f'<div class="gl"><span class="lb">Sobreprecio comercial</span><b>{(pc/pn-1)*100:.1f}%</b></div></div>', unsafe_allow_html=True)

# ───────────────────────── PESTAÑAS ─────────────────────────
t1, t2, t3, t4, t5 = st.tabs(["Desglose de operaciones", "Comparar tablas", "Sensibilidad", "Verificación", "Mortalidad"])

with t1:
    D, N, M, e0 = r["D"], r["N"], r["M"], r["e0"]
    i0 = edad - e0
    gv = lambda A, k: float(A[k]) if 0 <= k < len(A) else 0.0
    v = 1 / (1 + tasa_tecnica); dr = 1 - v
    Dx, Mx, Nx = gv(D, i0), gv(M, i0), gv(N, i0)
    Dn, Mn, Nn = gv(D, i0 + plazo), gv(M, i0 + plazo), gv(N, i0 + plazo)
    Nh = gv(N, i0 + h)
    nE = Dn / Dx
    A_m = {"Temporal": (Mx - Mn) / Dx, "Vida Entera": Mx / Dx, "Dotal": (Mx - Mn + Dn) / Dx}[modalidad]
    niv = Nx / Dx if modalidad == "Vida Entera" else (Nx - Nn) / Dx
    ad = {"Prima Única": 1.0, "Prima Nivelada": niv, "Prima Limitada": (Nx - Nh) / Dx,
          "Prima Fraccionada": niv - (m - 1) / (2 * m) * (1 if modalidad == "Vida Entera" else 1 - nE)}[forma_pago]
    ok = lambda a, b: '<span class="pill ok">coincide con actuarial.py</span>' if abs(a - b) <= 1e-8 * max(1, abs(b)) else '<span class="pill no">difiere de actuarial.py</span>'
    with st.expander(f"1 · Descuento y conmutación — v = {v:.6f}", expanded=True):
        L(rf"v=\frac{{1}}{{1+i}}={v:.6f}\qquad d=1-v={dr:.6f}")
        L(rf"D_x={Dx:,.4f}\quad N_x={Nx:,.4f}\quad M_x={Mx:,.4f}")
        if modalidad != "Vida Entera":
            L(rf"D_{{x+n}}={Dn:,.4f}\quad N_{{x+n}}={Nn:,.4f}\quad M_{{x+n}}={Mn:,.4f}")
    with st.expander(f"2 · Valor presente actuarial — A = {A_m:.6f}"):
        L({"Temporal": rf"A^1_{{x:n}}=\frac{{M_x-M_{{x+n}}}}{{D_x}}=\frac{{{Mx:,.2f}-{Mn:,.2f}}}{{{Dx:,.2f}}}",
                  "Vida Entera": rf"A_x=\frac{{M_x}}{{D_x}}=\frac{{{Mx:,.2f}}}{{{Dx:,.2f}}}",
                  "Dotal": rf"A_{{x:n}}=\frac{{M_x-M_{{x+n}}+D_{{x+n}}}}{{D_x}}=\frac{{{Mx:,.2f}-{Mn:,.2f}+{Dn:,.2f}}}{{{Dx:,.2f}}}"}[modalidad] + rf"={A_m:.6f}")
        st.markdown(ok(A_m, r["vpa"]), unsafe_allow_html=True)
    with st.expander(f"3 · Anualidad de primas — ä = {ad:.4f}"):
        if forma_pago == "Prima Única":
            L(r"\ddot a=1\quad(\text{pago único al inicio})")
        else:
            L({"Prima Nivelada": r"\ddot a=\frac{N_x-N_{x+n}}{D_x}", "Prima Limitada": rf"\ddot a_{{x:h}}=\frac{{N_x-N_{{x+{h}}}}}{{D_x}}",
                      "Prima Fraccionada": rf"\ddot a^{{({m})}}\approx\ddot a-\frac{{{m}-1}}{{2\cdot {m}}}(1-{{}}_nE_x)"}[forma_pago] + rf"={ad:.6f}")
        st.markdown(ok(ad, dd), unsafe_allow_html=True)
    with st.expander(f"4 · Prima neta — P = ${pn:,.2f}"):
        L(rf"P=\frac{{S\cdot A}}{{\ddot a}}=\frac{{{suma_asegurada:,.0f}\cdot{r['vpa']:.6f}}}{{{dd:.6f}}}=\${pn:,.2f}")
    with st.expander(f"5 · Prima comercial — G = ${pc:,.2f}"):
        L(rf"G=\frac{{P+f}}{{1-(\alpha+\beta+\gamma+u)}}=\frac{{{pn:,.2f}+{gasto_fijo:,.2f}}}{{1-{s_rec:.2f}}}=\${pc:,.2f}")
        st.dataframe(pd.DataFrame({"Componente": ["Prima neta (fondo técnico)", "Adquisición", "Administración", "Cobranza", "Utilidad", "Gasto fijo", "Prima comercial"],
                                   "Monto ($)": [pn, alfa * pc, beta * pc, gamma * pc, utilidad * pc, gasto_fijo, pc]}).style.format({"Monto ($)": "{:,.2f}"}),
                     hide_index=True, use_container_width=True)
    with st.expander("Resumen del contrato"):
        st.download_button("Descargar cotización (CSV)", pd.DataFrame({"Concepto": ["Tabla", "Modalidad", "Plazo", "Forma de pago", "Edad", "Suma asegurada", "Tasa técnica", "VPA unitario", "Anualidad", "Prima neta", "Prima comercial"], "Valor": [tabla_op, modalidad, plazo, forma_pago, edad, suma_asegurada, tasa_tecnica, r["vpa"], dd, pn, pc]}).to_csv(index=False).encode("utf-8-sig"), "cotizacion.csv", "text/csv")
        st.table(pd.DataFrame({"Componente": ["Suma asegurada", "Modalidad", "Forma de pago", "Tabla", "Tasa técnica", "Prima neta", "Prima comercial"],
                               "Valor": [f"${suma_asegurada:,.2f}", modalidad, forma_pago + (f" ({m} pagos/año)" if m > 1 else ""), tabla_op, f"{tasa_tecnica*100:.2f}%", f"${pn:,.2f}", f"${pc:,.2f}"]}))

with t2:
    vals = {t: pc_solo(t, *args[1:]) for t in ORIGEN}
    mx = max([x for x in vals.values() if x] or [1])
    st.markdown('<div class="gl"><div class="lb">Misma póliza, distinta base de mortalidad</div>' + "".join(
        f'<div class="row{" on" if t == tabla_op else ""}"><span>{t}</span><div class="bar"><b style="--w:{(x or 0)/mx*100:.1f}%"></b></div><span>{"$"+format(x, ",.2f") if x else "fuera de rango"}</span></div>' for t, x in vals.items()) + '</div>', unsafe_allow_html=True)

with t3:
    c1, c2 = st.columns(2)
    ed = list(range(max(int(ea_[0]), 18), min(edad_max - (0 if modalidad == "Vida Entera" else plazo), 75) + 1, 2))
    c1.markdown('<div class="gl"><div class="lb">Prima comercial según la edad</div>' + lineas(ed, [pc_solo(tabla_op, e, *args[2:]) for e in ed], edad, lambda v: f"{v:.0f} años", lambda v: f"${v:,.0f}") + '</div>', unsafe_allow_html=True)
    ts = [round(0.01 + 0.005 * k, 3) for k in range(29)]
    c2.markdown('<div class="gl"><div class="lb">Prima comercial según la tasa técnica</div>' + lineas(ts, [pc_solo(tabla_op, edad, suma_asegurada, t, *args[4:]) for t in ts], tasa_tecnica, lambda v: f"{v*100:.1f}%", lambda v: f"${v:,.0f}") + '</div>', unsafe_allow_html=True)

with t4:
    def P(mod, fp, hh=h, mm=m, nn=plazo, **kw):
        return cotizar(tabla_op, edad, 1.0, tasa_tecnica, mod, nn, fp, hh, mm, kw.get("a", 0), kw.get("b", 0), kw.get("g", 0), kw.get("u", 0), kw.get("f", 0))
    pruebas = []
    def prueba(nombre, fn):
        try:
            a, b, desc = fn()
            pruebas.append((nombre, desc, abs(a - b) <= 1e-8 * max(1, abs(b))))
        except Exception as e:
            pruebas.append((nombre, f"no evaluable: {e}", False))
    prueba("Dotal = Temporal + dotación pura", lambda: (P("Dotal", "Prima Única")["vpa"], P("Temporal", "Prima Única")["vpa"] + gv(r["D"], i0 + plazo) / gv(r["D"], i0), "A(dotal) − [A(temporal) + ₙEₓ]"))
    prueba("A = 1 − d·ä (dotal)", lambda: (P("Dotal", "Prima Única")["vpa"], 1 - (1 - 1 / (1 + tasa_tecnica)) * P("Dotal", "Prima Nivelada")["dd"], "identidad entre seguro y anualidad"))
    prueba("Limitada con h = n = Nivelada", lambda: (P(modalidad, "Prima Limitada", hh=plazo)["pn"], P(modalidad, "Prima Nivelada")["pn"], "prima limitada en el caso extremo h = n"))
    prueba("Fraccionada > Nivelada (m = 2)", lambda: (max(P(modalidad, "Prima Fraccionada", mm=2)["pn"], P(modalidad, "Prima Nivelada")["pn"]) , P(modalidad, "Prima Fraccionada", mm=2)["pn"], "la prima anual fraccionada supera a la nivelada"))
    prueba("Recargos nulos: comercial = neta", lambda: (P(modalidad, forma_pago)["pc"], P(modalidad, forma_pago)["pn"], "con α = β = γ = u = f = 0"))
    prueba("Comercial > neta (parámetros actuales)", lambda: (max(pc, pn), pc, "G ≥ P con los recargos actuales"))
    st.markdown('<div class="gl">' + "".join(f'<div class="chk"><div>{n}<small>{d}</small></div><span class="pill {"ok" if o else "no"}">{"aprobada" if o else "revisar"}</span></div>' for n, d, o in pruebas) + '</div>', unsafe_allow_html=True)
    st.caption("Tolerancia relativa 10⁻⁸, conforme al diseño metodológico (fase 3).")

with t5:
    ea, q, l, d_ = tabla(tabla_op)
    st.markdown('<div class="gl"><div class="lb">Probabilidad anual de fallecimiento qₓ — ' + tabla_op + '</div>' + lineas([int(a) for a in ea], [float(x) for x in q], edad, lambda v: f"{v:.0f}", lambda v: f"{v:.4f}") + f'<div class="sub">{ORIGEN[tabla_op]} Edad terminal: {edad_max}, q = {float(q[-1]):.4f}.</div></div>', unsafe_allow_html=True)