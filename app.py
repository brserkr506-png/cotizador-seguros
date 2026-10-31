import streamlit as st
import pandas as pd
import numpy as np
from actuarial import cargar_tabla, calcular_conmutacion, calcular_seguro, calcular_anualidad_primas, calcular_prima_comercial

st.set_page_config(page_title="Cotizador Actuarial", page_icon="◐", layout="wide", initial_sidebar_state="expanded")

# ───────────────────────── Estilo HyperOS 4 ─────────────────────────
SP = "cubic-bezier(.22,1.25,.36,1)"  # resorte con ligero rebote
ROLL = "".join(f"@keyframes roll{d}{{from{{transform:translateY(0)}}to{{transform:translateY(-{d}em)}}}}.r{d}{{animation-name:roll{d}}}" for d in range(10))
CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;300;400;500;600&display=swap');
@property --a{syntax:'<angle>';inherits:false;initial-value:0deg}
@property --b{syntax:'<angle>';inherits:false;initial-value:0deg}
:root{--sp:SPRING;--bg:#EEF1F7;--tx:#14171F;--mu:#6B7280;--gl:rgba(255,255,255,.62);--bd:rgba(255,255,255,.8);--ac:#3478F6;--or:#FF6A00;--c1:#3478F6;--c2:#FF9F43;--c3:#B5BCCB;--sh:0 18px 50px -22px rgba(40,60,110,.35);--inp:rgba(255,255,255,.55)}
@media(prefers-color-scheme:dark){:root{--bg:#0B0D13;--tx:#F2F4F8;--mu:#99A1B3;--gl:rgba(34,38,52,.58);--bd:rgba(255,255,255,.08);--sh:0 18px 50px -22px rgba(0,0,0,.8);--inp:rgba(255,255,255,.07)}}
html,body,.stApp,.stApp p,.stApp label,.stApp input,.stApp button,.stApp li,.stApp td,.stApp th,.stApp summary,.stApp h1,.stApp h2,.stApp h3{font-family:'MiSans','Inter','HarmonyOS Sans',system-ui,sans-serif}
[data-testid=stIconMaterial],.material-symbols-rounded{font-family:'Material Symbols Rounded'!important}
.stApp{background:var(--bg);color:var(--tx)}
.stApp::before,.stApp::after{content:"";position:fixed;z-index:0;width:56vmax;height:56vmax;filter:blur(90px);opacity:.55;pointer-events:none;animation:morph 22s ease-in-out infinite alternate}
.stApp::before{top:-22vmax;left:-14vmax;background:#7FB2FF}
.stApp::after{bottom:-26vmax;right:-14vmax;background:#FFB27A;animation-duration:28s;animation-direction:alternate-reverse}
@keyframes morph{0%{border-radius:42% 58% 63% 37%/41% 44% 56% 59%;transform:translate(0,0) rotate(0)}50%{border-radius:65% 35% 40% 60%/55% 62% 38% 45%;transform:translate(6vmax,4vmax) rotate(40deg)}100%{border-radius:38% 62% 55% 45%/60% 40% 60% 40%;transform:translate(-3vmax,8vmax) rotate(80deg)}}
header[data-testid=stHeader]{background:transparent}
.block-container{position:relative;z-index:1;padding-top:2.2rem;max-width:1180px}
[data-testid=stSidebar]{background:var(--gl);backdrop-filter:blur(36px) saturate(1.6);border-right:1px solid var(--bd);border-radius:0 34px 34px 0}
[data-testid=stSidebar] [data-testid=stExpander] details{background:rgba(255,255,255,.18)}
h1,h2,h3{font-weight:300!important;letter-spacing:-.02em}
[data-testid=stExpander] details{border:1px solid var(--bd)!important;border-radius:26px!important;background:var(--gl);backdrop-filter:blur(24px);box-shadow:var(--sh);overflow:hidden;interpolate-size:allow-keywords;transition:transform .5s var(--sp)}
[data-testid=stExpander] details::details-content{block-size:0;opacity:0;overflow:clip;transition:block-size .55s var(--sp),opacity .4s ease,content-visibility .55s allow-discrete}
[data-testid=stExpander] details[open]::details-content{block-size:auto;opacity:1}
[data-testid=stExpander] summary{font-weight:500;padding:.9rem 1.2rem}
[data-testid=stExpander] summary:hover{background:rgba(120,140,200,.10)}
[data-testid=stNumberInput] input,[data-testid=stNumberInput] button{background:transparent!important;color:var(--tx)!important}
[data-baseweb=select]>div,[data-testid=stNumberInputContainer]{border-radius:18px!important;background:var(--inp)!important;color:var(--tx)!important;border:1px solid var(--bd)!important;transition:box-shadow .35s var(--sp),transform .35s var(--sp)}
[data-baseweb=select]>div:hover,[data-testid=stNumberInputContainer]:focus-within{box-shadow:0 0 0 3px rgba(52,120,246,.28);transform:scale(1.01)}
[data-baseweb=popover] ul,[data-baseweb=menu]{border-radius:22px!important;backdrop-filter:blur(30px);background:var(--gl)!important;border:1px solid var(--bd);box-shadow:var(--sh);animation:pop .45s var(--sp) both;transform-origin:top}
@keyframes pop{from{opacity:0;transform:scale(.9) translateY(-10px)}}
[data-baseweb=menu] li{border-radius:14px;margin:2px 6px;transition:background .2s}
[data-testid=stSlider] [role=slider]{background:#fff!important;box-shadow:0 4px 14px rgba(0,0,0,.25)!important;width:26px;height:26px;transition:transform .35s var(--sp)}
[data-testid=stSlider] [role=slider]:active{transform:scale(1.25)}
[data-testid=stSegmentedControl] button,[data-baseweb=button-group] button{border-radius:999px!important;transition:all .45s var(--sp)}
[data-testid=stTabs] [role=tablist]{gap:6px;background:var(--gl);padding:6px;border-radius:999px;border:1px solid var(--bd);backdrop-filter:blur(20px);width:fit-content;max-width:100%;overflow-x:auto}
[data-testid=stTabs] [role=tab]{border-radius:999px;padding:.5rem 1.1rem;transition:all .45s var(--sp)}
[data-testid=stTabs] [aria-selected=true]{background:var(--ac);color:#fff}
[data-testid=stTabs] [data-baseweb=tab-highlight],[data-testid=stTabs] [data-baseweb=tab-border]{display:none}
.gl{background:var(--gl);backdrop-filter:blur(28px) saturate(1.5);border:1px solid var(--bd);border-radius:34px;box-shadow:var(--sh);padding:1.6rem 1.8rem;transition:transform .5s var(--sp)}
.gl:hover{transform:translateY(-3px) scale(1.004)}
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:.2rem 0 1.2rem}
.chip{padding:.38rem .95rem;border-radius:999px;background:var(--gl);border:1px solid var(--bd);font-size:.82rem;color:var(--mu);backdrop-filter:blur(16px)}
.hero{display:grid;grid-template-columns:1.5fr 1fr;gap:1.5rem;align-items:center;margin-bottom:1rem}
@media(max-width:760px){.hero{grid-template-columns:1fr}}
.lb{color:var(--mu);font-size:.9rem}
.sub{color:var(--mu);margin-top:.7rem;font-size:.95rem}
.odo{display:flex;align-items:flex-end;font-size:clamp(46px,7.5vw,96px);font-weight:200;letter-spacing:-.04em;line-height:1;font-variant-numeric:tabular-nums;color:var(--tx);margin-top:.3rem}
.odo .dg{display:inline-block;height:1em;overflow:hidden}
.odo .st{display:flex;flex-direction:column;animation-duration:1.15s;animation-timing-function:SPRING;animation-fill-mode:both}
.odo i{display:block;height:1em;font-style:normal}
.odo .sp{display:inline-block;height:1em}
ROLL
.ringw{display:flex;gap:1.3rem;align-items:center;justify-content:center;flex-wrap:wrap}
.ring{width:150px;height:150px;border-radius:50%;background:conic-gradient(var(--c1) 0 var(--a),var(--c2) var(--a) var(--b),var(--c3) var(--b) 360deg);-webkit-mask:radial-gradient(circle,transparent 57%,#000 58%);mask:radial-gradient(circle,transparent 57%,#000 58%);animation:sweep 1.4s SPRING both}
@keyframes sweep{from{--a:0deg;--b:0deg;transform:rotate(-90deg) scale(.8)}to{transform:rotate(0) scale(1)}}
.lg{display:flex;flex-direction:column;gap:.5rem;font-size:.88rem}
.lg span::before{content:"";display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:8px;background:var(--k)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin-bottom:1.4rem}
@media(max-width:760px){.stats{grid-template-columns:1fr}}
.stats .gl{padding:1.1rem 1.4rem;border-radius:28px}
.stats b{display:block;font-size:1.65rem;font-weight:300;margin-top:.2rem}
.row{display:grid;grid-template-columns:150px 1fr 110px;gap:.9rem;align-items:center;margin:.7rem 0;font-size:.92rem}
.bar{height:18px;border-radius:99px;background:rgba(130,140,170,.18);overflow:hidden}
.bar b{display:block;height:100%;width:var(--w);border-radius:99px;background:linear-gradient(90deg,#7FB2FF,var(--ac));animation:grow 1.1s SPRING both}
.row.on .bar b{background:linear-gradient(90deg,#FFB27A,var(--or))}
@keyframes grow{from{width:0}}
.pill{display:inline-block;padding:.25rem .8rem;border-radius:99px;font-size:.8rem;font-weight:500}
.ok{background:rgba(48,190,120,.18);color:#1C9A5E}.no{background:rgba(240,80,70,.18);color:#D63C32}
.chk{display:flex;justify-content:space-between;align-items:center;gap:1rem;padding:.8rem 0;border-bottom:1px solid var(--bd)}
.chk small{color:var(--mu);display:block}
svg.ch{width:100%;height:auto;overflow:visible}
.ch .ln{fill:none;stroke:var(--ac);stroke-width:3;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;animation:draw 1.6s ease-out both}
@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
.ch .ar{fill:url(#g);animation:fi 1.6s ease both}.ch .mk{fill:var(--or);stroke:#fff;stroke-width:3;animation:fi 1s 1.1s both}
.ch text{fill:var(--mu);font-size:11px}
@keyframes fi{from{opacity:0}}

[data-testid=stAppViewContainer],[data-testid=stMain],[data-testid=stMainBlockContainer],section.main{border:none!important;outline:none!important;box-shadow:none!important;background:transparent!important}
[data-testid=stAppDeployButton],[data-testid=stToolbar] [data-testid=stAppDeployButton]{display:none}
[data-testid=stElementContainer]:has(iframe[height="0"]){display:none}
iframe{border:0}
[data-testid=stSliderThumbValue]{color:var(--ac)!important;font-weight:500}
[data-testid=stTabs] [data-baseweb=tab-highlight],[data-testid=stTabs] [data-baseweb=tab-border]{display:none!important;height:0!important}
[data-testid=stTabs] [role=tablist]>div:not([role=tab]){display:none!important}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>""".replace("SPRING", SP).replace("ROLL", ROLL)
st.markdown(CSS, unsafe_allow_html=True)

# ───────────────────────── Núcleo de cálculo (usa actuarial.py) ─────────────────────────
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
    try:
        return float(cotizar(*args)["pc"])
    except Exception:
        return None

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
    if len(pts) < 2:
        return '<p class="lb">Sin datos suficientes en este rango.</p>'
    xs, ys = zip(*pts)
    W, H, P = 640, 230, 34
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    y1 = y1 if y1 > y0 else y0 + 1
    px = lambda v: P + (v - x0) / ((x1 - x0) or 1) * (W - 2 * P)
    py = lambda v: H - P - (v - y0) / (y1 - y0) * (H - 2 * P)
    d = "M" + " L".join(f"{px(a):.1f},{py(b):.1f}" for a, b in pts)
    ar = d + f" L{px(xs[-1]):.1f},{H-P} L{px(xs[0]):.1f},{H-P}Z"
    k = min(range(len(xs)), key=lambda j: abs(xs[j] - mx))
    return (f'<svg class="ch" viewBox="0 0 {W} {H}"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3478F6" stop-opacity=".35"/><stop offset="1" stop-color="#3478F6" stop-opacity="0"/></linearGradient></defs>'
            f'<path class="ar" d="{ar}"/><path class="ln" pathLength="1" d="{d}"/><circle class="mk" cx="{px(xs[k]):.1f}" cy="{py(ys[k]):.1f}" r="7"/>'
            f'<text x="{P}" y="{H-8}">{fx(xs[0])}</text><text x="{W-P}" y="{H-8}" text-anchor="end">{fx(xs[-1])}</text>'
            f'<text x="{px(xs[k]):.1f}" y="{py(ys[k])-14:.1f}" text-anchor="middle" style="fill:var(--tx);font-weight:500">{fy(ys[k])}</text>'
            f'<text x="{P}" y="14">{fy(y1)}</text><text x="{P}" y="{H-P-6}">{fy(y0)}</text></svg>')

def L(s):
    st.latex(s.replace(",", "{,}"))

def selector(lado, etiqueta, opciones, defecto=None, fmt=str):
    if hasattr(st, "segmented_control"):
        return lado.segmented_control(etiqueta, opciones, default=defecto or opciones[0], format_func=fmt, key=etiqueta) or (defecto or opciones[0])
    return lado.radio(etiqueta, opciones, horizontal=True, format_func=fmt)

import streamlit.components.v1 as components
components.html("<script>const d=window.parent.document;d.documentElement.lang='es';d.documentElement.setAttribute('translate','no');d.body.classList.add('notranslate');</script>", height=0)

# ───────────────────────── Panel de control (sidebar) ─────────────────────────
sb = st.sidebar
sb.markdown("### Centro de control")
with sb.expander("Asegurado y tabla", expanded=True):
    tabla_op = st.selectbox("Tabla de mortalidad", list(ORIGEN))
    st.caption(ORIGEN[tabla_op])
    ea_, *_ = tabla(tabla_op)
    edad_max = int(ea_[-1])
    edad = st.number_input("Edad del asegurado (x)", min_value=int(ea_[0]), max_value=edad_max, value=min(30, edad_max), step=1)
    suma_asegurada = st.number_input("Suma asegurada ($)", min_value=1000.0, value=100000.0, step=5000.0)
    tasa_tecnica = st.slider("Tasa de interés técnica (i)", 0.01, 0.15, 0.04, 0.005, format="%.3f")
with sb.expander("Cobertura", expanded=True):
    modalidad = selector(st, "Modalidad", ["Temporal", "Vida Entera", "Dotal"])
    plazo = 10
    if modalidad in ["Temporal", "Dotal"]:
        plazo = st.slider("Plazo del seguro (n años)", 1, 50, 20)
with sb.expander("Forma de pago", expanded=True):
    forma_pago = st.selectbox("Forma de pago de prima", ["Prima Única", "Prima Nivelada", "Prima Limitada", "Prima Fraccionada"], index=1)
    h, m = 10, 1
    if forma_pago == "Prima Limitada":
        h = st.slider("Plazo de pago limitado (h años)", 1, plazo, min(5, plazo))
    if forma_pago == "Prima Fraccionada":
        fr = selector(st, "Frecuencia", ["Semestral", "Trimestral", "Mensual"])
        m = {"Semestral": 2, "Trimestral": 4, "Mensual": 12}[fr]
with sb.expander("Recargos y gastos"):
    alfa = st.slider("Adquisición (α)", 0.0, 0.5, 0.10, 0.01)
    beta = st.slider("Administración (β)", 0.0, 0.2, 0.03, 0.01)
    gamma = st.slider("Cobranza (γ)", 0.0, 0.2, 0.02, 0.01)
    utilidad = st.slider("Margen de utilidad (u)", 0.0, 0.3, 0.05, 0.01)
    gasto_fijo = st.number_input("Gasto fijo por póliza ($)", min_value=0.0, value=50.0, step=10.0)

# ───────────────────────── Validaciones y cálculo ─────────────────────────
st.markdown("# Cotizador de seguros de vida")
s_rec = alfa + beta + gamma + utilidad
if s_rec >= 1:
    st.error("α + β + γ + u debe ser menor que 1 para que la prima comercial exista.")
    st.stop()
if modalidad != "Vida Entera" and edad + plazo > edad_max:
    st.warning(f"La edad + plazo ({edad + plazo}) excede la edad terminal de {tabla_op} ({edad_max}). Reduce el plazo.")
    st.stop()
args = (tabla_op, edad, suma_asegurada, tasa_tecnica, modalidad, plazo, forma_pago, h, m, alfa, beta, gamma, utilidad, gasto_fijo)
try:
    r = cotizar(*args)
except Exception as e:
    st.error(f"Se ha producido un error en la ejecución del cálculo: {e}")
    st.stop()

pn, pc, dd = r["pn"], r["pc"], r["dd"]
rec, fijo = s_rec * pc, gasto_fijo
a1 = 360 * pn / pc
a2 = a1 + 360 * rec / pc
per = {"Prima Única": "pago único", "Prima Nivelada": "por año", "Prima Limitada": f"por año durante {h} años", "Prima Fraccionada": f"por año · {m} pagos de ${pc/m:,.2f}"}[forma_pago]
chips = [tabla_op, modalidad + (f" · {plazo} años" if modalidad != "Vida Entera" else ""), forma_pago, f"x = {edad}", f"i = {tasa_tecnica*100:.2f}%"]
st.markdown('<div class="chips">' + "".join(f'<span class="chip">{c}</span>' for c in chips) + '</div>'
            + f'<div class="hero"><div class="gl"><div class="lb">Prima comercial</div>{odo(f"{pc:,.2f}")}<div class="sub">${"{:,.0f}".format(suma_asegurada)} de suma asegurada · {per}</div></div>'
            + f'<div class="gl"><div class="ringw"><div class="ring" style="--a:{a1:.1f}deg;--b:{a2:.1f}deg"></div><div class="lg">'
            + f'<span style="--k:var(--c1)">Prima neta ${pn:,.2f}</span><span style="--k:var(--c2)">Recargos ${rec:,.2f}</span><span style="--k:var(--c3)">Gasto fijo ${fijo:,.2f}</span></div></div></div></div>'
            + f'<div class="stats"><div class="gl"><span class="lb">Valor presente actuarial (A)</span><b>{r["vpa"]:.6f}</b></div>'
            + f'<div class="gl"><span class="lb">Factor de anualidad (ä)</span><b>{dd:.4f}</b></div>'
            + f'<div class="gl"><span class="lb">Sobreprecio comercial</span><b>{(pc/pn-1)*100:.1f}%</b></div></div>', unsafe_allow_html=True)

# ───────────────────────── Pestañas ─────────────────────────
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