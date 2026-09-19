#!/usr/bin/env python3
"""Jseongwon 프로필 히어로 SVG 생성기.

데이터(NODES / ACTIVE / FLOW)만 고치고 다시 실행하면 assets/hero.svg 가 갱신된다.
    python3 assets/build_hero.py
"""
import datetime
import math

W, H = 1200, 836

# ── 팔레트 ────────────────────────────────────────────────────────────────
BG        = "#05060a"
PANEL     = "#0a0c14"
LINE      = "#1c2035"
DIM       = "#4e5570"
TEXT      = "#c9cede"
WHITE     = "#ffffff"
ACCENT    = "#fbbf24"
CORE      = "#a855f7"

LANG = {
    "Go":         "#22d3ee",
    "TypeScript": "#60a5fa",
    "Python":     "#fbbf24",
    "Dart":       "#2dd4bf",
    "Rust":       "#fb923c",
    "C#":         "#ec4899",
    "Shell":      "#34d399",
}

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

# ── 데이터 ────────────────────────────────────────────────────────────────
# (번호, 짧은 라벨, 표시용 코드명, 언어, 각도°, 반지름)  각도 0°=오른쪽, 반시계 +
# 제품 브랜드는 alpha / bravo 로 가려 둔다. 실제 매핑은 이 파일에 기록하지 않는다.
NODES = [
    ("01", "CHAIN",     "alpha-chain",              "Go",          168, 210),
    ("02", "PLACE·API", "place-alpha-platform",     "Go",          142, 205),
    ("03", "PLACE·WEB", "place-alpha-front",        "TypeScript",  113, 195),
    ("04", "WALLET",    "wallet-alpha-front",       "TypeScript",   80, 190),
    ("05", "LOOP",      "alpha-loop",               "Dart",         48, 200),
    ("06", "MSG·API",   "messenger-platform",       "Go",           16, 215),
    ("07", "MSG·WEB",   "messenger-front",          "TypeScript",  -15, 205),
    ("08", "DRAFT·API", "draft-bravo-platform",     "Go",          -45, 195),
    ("09", "DRAFT·ML",  "draft-bravo-model",        "Python",      -76, 192),
    ("10", "DRAFT·WEB", "draft-bravo-front",        "TypeScript", -108, 185),
    ("11", "MKT·API",   "marketing-bravo-platform", "Go",         -140, 200),
    ("12", "K3S",       "k3s-migration",            "Shell",      -170, 215),
    ("13", "VEILGATE",  "VeilGate",                 "Rust",        133, 132),
    ("14", "SOCIAL",    "social-automation",        "Go",           25, 138),
    ("15", "TAMERLOOP", "TamerLoop",                "C#",          -90, 118),
]

# 노드 사이 보조 연결선 (같은 제품군 묶기)
EDGES = [("02", "03"), ("03", "04"), ("06", "07"), ("08", "09"), ("08", "10"), ("11", "10")]

ACTIVE = {
    "tag":   "INFRA · LIVE",
    "name":  "PRODUCTION CLUSTER",
    "meta":  [("CLOUD", "OCI FREE TIER · OKE"),
              ("NODES", "ARM A1 · 4 OCPU · 24GB"),
              ("EDGE",  "TRAEFIK v3 · LET'S ENCRYPT")],
    "bars":  [("CLUSTER", 1.00, "ACTIVE",  "#34d399"),
              ("INGRESS", 1.00, "TRAEFIK", "#34d399"),
              ("TLS",     1.00, "LE PROD", "#34d399"),
              ("SERVICE", 0.45, "DEPLOY",  "#fbbf24")],
    "pill":  "SHIPPING SERVICES",
    "cost":  "0 USD / MONTH",
}

FLOW = [("SPEC",    "ISSUE · PR"),
        ("ARCH",    "CLEAN + HEX"),
        ("BUILD",   "GO · NEXT"),
        ("TEST",    "CI GATE"),
        ("IMAGE",   "OCIR · ARM64"),
        ("DEPLOY",  "K8S · HELM"),
        ("OBSERVE", "INGRESS · TLS")]
FLOW_COLORS = ["#22d3ee", "#60a5fa", "#a855f7", "#ec4899", "#fbbf24", "#34d399", "#2dd4bf"]

CX, CY = 400, 360          # 노드 그래프 중심
RY = 0.62                  # 세로 눌림 비율

# ── 헬퍼 ──────────────────────────────────────────────────────────────────
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "&apos;")

def txt(x, y, s, size=9, fill=DIM, weight="400", anchor="start", ls="0.12em", op=None):
    o = f' opacity="{op}"' if op is not None else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}" letter-spacing="{ls}"{o}>{esc(s)}</text>')

def panel(x, y, w, h):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{PANEL}" '
            f'stroke="{LINE}" stroke-width="1"/>')

def panel_head(x, y, w, label, right=None):
    """패널 좌상단 라벨 + 오른쪽 보조 텍스트 + 구분선."""
    out = [txt(x + 14, y + 19, label, 8, DIM, "500")]
    if right:
        out.append(txt(x + w - 14, y + 19, right, 8, DIM, "400", "end"))
    out.append(f'<line x1="{x}" y1="{y + 30}" x2="{x + w}" y2="{y + 30}" stroke="{LINE}"/>')
    return "".join(out)

def pos(angle_deg, r):
    a = math.radians(angle_deg)
    return CX + r * math.cos(a), CY - r * RY * math.sin(a)

# ── 조립 ──────────────────────────────────────────────────────────────────
P = []
A = P.append

A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
  f'font-family="{MONO}" role="img" aria-label="Jseongwon system field map">')

# defs: 글로우 필터 + 그라디언트 + 애니메이션
A('<defs>')
A('<filter id="glow" x="-80%" y="-80%" width="260%" height="260%">'
  '<feGaussianBlur stdDeviation="4" result="b"/><feMerge>'
  '<feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
A('<filter id="softglow" x="-120%" y="-120%" width="340%" height="340%">'
  '<feGaussianBlur stdDeviation="9"/></filter>')
A(f'<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">'
  f'<stop offset="0%" stop-color="{CORE}" stop-opacity="0.9"/>'
  f'<stop offset="45%" stop-color="#ec4899" stop-opacity="0.5"/>'
  f'<stop offset="100%" stop-color="#22d3ee" stop-opacity="0"/></linearGradient>')
A(f'<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">'
  f'<stop offset="0%" stop-color="#22d3ee" stop-opacity="0"/>'
  f'<stop offset="50%" stop-color="#22d3ee" stop-opacity="0.85"/>'
  f'<stop offset="100%" stop-color="#22d3ee" stop-opacity="0"/></linearGradient>')
A('</defs>')

# SVG 내부 CSS 애니메이션 (GitHub는 <img>로 렌더하므로 CSS 애니메이션은 동작, 스크립트는 불가)
A('<style>'
  '.breathe{animation:br 3.6s ease-in-out infinite}'
  '@keyframes br{0%,100%{opacity:.30}50%{opacity:.85}}'
  '.ring{animation:rg 3.4s ease-out infinite}'
  '@keyframes rg{0%{r:30px;opacity:.55}100%{r:62px;opacity:0}}'
  '.scan{animation:sc 5.5s linear infinite}'
  '@keyframes sc{0%{transform:translateX(-240px)}100%{transform:translateX(1180px)}}'
  '.blink{animation:bk 2s step-end infinite}'
  '@keyframes bk{0%,60%{opacity:1}61%,100%{opacity:.25}}'
  '@media (prefers-reduced-motion:reduce){.breathe,.ring,.scan,.blink{animation:none}}'
  '</style>')

# 바탕 + 외곽 프레임
A(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
A(f'<rect x="8" y="8" width="{W-16}" height="{H-16}" rx="6" fill="none" stroke="{LINE}"/>')

# ── 상단 메타 바 ──────────────────────────────────────────────────────────
A(txt(30, 38, "JSEONGWON / SYSTEM FIELD MAP / BACKEND · PLATFORM", 8, DIM, "500"))
A(txt(W - 30, 38, "137 REPOS · GO + K8S · 2026", 8, DIM, "400", "end"))

# ── 타이틀 블록 ───────────────────────────────────────────────────────────
A(txt(30, 86, "BUILDING PRODUCT PLATFORMS", 25, WHITE, "700", "0.02em"))
A(txt(30, 114, "ON A ZERO-COST CLOUD", 25, ACCENT, "700", "0.02em"))
A(txt(30, 136, "GO · CLEAN + HEXAGONAL · KUBERNETES · TRAEFIK · CERT-MANAGER · OCI FREE TIER",
      8, DIM, "400"))
A(txt(W - 30, 96, "FOCUS", 8, DIM, "400", "end"))
A(txt(W - 30, 114, "ZERO-COST INFRA", 12, TEXT, "500", "end"))

# ── 구분 웨이브 ───────────────────────────────────────────────────────────
A(f'<rect x="30" y="156" width="{W-60}" height="1" fill="url(#rule)"/>')
wave = []
for i in range(0, 1141, 4):
    x = 30 + i
    y = 166 + math.sin(i / 26.0) * 5 * math.exp(-i / 900.0) + math.sin(i / 7.0) * 1.6
    wave.append(f"{x:.0f},{y:.1f}")
A(f'<polyline points="{" ".join(wave)}" fill="none" stroke="{CORE}" stroke-width="1" opacity="0.35"/>')
segs = [(30, 150, "#a855f7"), (190, 90, "#ec4899"), (290, 220, "#60a5fa"),
        (525, 140, "#22d3ee"), (680, 70, "#34d399"), (760, 180, "#fbbf24")]
for sx, sw, sc in segs:
    A(f'<rect x="{sx}" y="176" width="{sw}" height="2" fill="{sc}" opacity="0.5"/>')
A(f'<g class="scan"><rect x="0" y="174" width="240" height="6" fill="url(#sweep)"/></g>')

# ── 좌측: LIVE PROJECT GRAPH ─────────────────────────────────────────────
GX, GY, GW, GH = 28, 196, 744, 340
A(panel(GX, GY, GW, GH))
A(panel_head(GX, GY, GW, "LIVE PROJECT GRAPH", "15 SYSTEMS · 7 LANGUAGES"))

coords = {}
for num, label, full, lang, ang, r in NODES:
    coords[num] = pos(ang, r)

# 중심 → 노드 간선
for i, (num, label, full, lang, ang, r) in enumerate(NODES):
    x, y = coords[num]
    c = LANG[lang]
    A(f'<line x1="{CX}" y1="{CY}" x2="{x:.1f}" y2="{y:.1f}" stroke="{c}" '
      f'stroke-width="0.8" opacity="0.22"/>')

# 제품군 보조 간선
for a_num, b_num in EDGES:
    ax, ay = coords[a_num]
    bx, by = coords[b_num]
    A(f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" '
      f'stroke="{DIM}" stroke-width="0.7" opacity="0.30" stroke-dasharray="2 4"/>')

# 중심 노드
A(f'<circle cx="{CX}" cy="{CY}" r="46" fill="{CORE}" opacity="0.13" filter="url(#softglow)"/>')
A(f'<circle class="ring" cx="{CX}" cy="{CY}" r="30" fill="none" stroke="{CORE}" stroke-width="1"/>')
A(f'<circle cx="{CX}" cy="{CY}" r="30" fill="{BG}" stroke="{CORE}" stroke-width="1.2"/>')
A(txt(CX, CY - 1, "CORE", 10, WHITE, "700", "middle", "0.16em"))
A(txt(CX, CY + 12, "STACK", 7, CORE, "500", "middle", "0.2em"))

# 노드
for idx, (num, label, full, lang, ang, r) in enumerate(NODES):
    x, y = coords[num]
    c = LANG[lang]
    delay = f"{(idx % 6) * 0.6:.1f}s"
    A(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="19" fill="{c}" opacity="0.14" '
      f'filter="url(#softglow)" class="breathe" style="animation-delay:{delay}"/>')
    A(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11" fill="{BG}" stroke="{c}" stroke-width="1.2" '
      f'filter="url(#glow)"/>')
    A(txt(x, y + 3.2, num, 8, c, "600", "middle", "0.04em"))
    # 라벨 박스
    bw = max(46, len(label) * 5.6 + 12)
    by = y + 19
    A(f'<rect x="{x - bw/2:.1f}" y="{by}" width="{bw:.1f}" height="14" rx="2" '
      f'fill="{BG}" stroke="{LINE}"/>')
    A(txt(x, by + 10, label, 7, TEXT, "500", "middle", "0.08em"))

A(txt(GX + 14, GY + GH - 12, "PRIVATE WORKSPACES — PRODUCT NAMES REDACTED AS ALPHA / BRAVO",
      7, DIM, "400", "0.14em"))

# ── 우측: ACTIVE PROJECT ─────────────────────────────────────────────────
AX, AY, AW, AH = 790, 196, 382, 340
A(panel(AX, AY, AW, AH))
A(panel_head(AX, AY, AW, "ACTIVE PROJECT", "01 / 15"))

A(txt(AX + 16, AY + 56, ACTIVE["tag"], 7, "#34d399", "500"))
A(txt(AX + 16, AY + 80, ACTIVE["name"], 18, WHITE, "700", "0.03em"))

my = AY + 104
for k, v in ACTIVE["meta"]:
    A(txt(AX + 16, my, k, 7, DIM, "400"))
    A(txt(AX + AW - 16, my, v, 8, TEXT, "400", "end"))
    my += 17

# 스파크라인
SPX, SPY, SPW, SPH = AX + 16, AY + 160, AW - 32, 46
A(txt(SPX, SPY - 7, "SIGNAL ACTIVITY", 7, DIM, "400"))
A(f'<rect x="{SPX}" y="{SPY}" width="{SPW}" height="{SPH}" rx="3" fill="{BG}" stroke="{LINE}"/>')
pts, dots = [], []
for i in range(0, SPW - 16, 3):
    t = i / float(SPW - 16)
    yv = (math.sin(t * 7.2) * 0.55 + math.sin(t * 17.0) * 0.2 + math.sin(t * 3.1) * 0.25)
    px = SPX + 8 + i
    py = SPY + SPH / 2 - yv * (SPH / 2 - 12)
    pts.append(f"{px:.0f},{py:.1f}")
    if i % 42 == 0:
        dots.append((px, py))
A(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{TEXT}" stroke-width="1.2" opacity="0.8"/>')
for px, py in dots:
    A(f'<circle cx="{px:.0f}" cy="{py:.1f}" r="2" fill="{WHITE}"/>')

# 진행 바
BY = AY + 222
A(txt(AX + 16, BY - 8, "STACK STATUS", 7, DIM, "400"))
BAR_X = AX + 74
BAR_W = AW - 74 - 74
for i, (k, frac, val, col) in enumerate(ACTIVE["bars"]):
    row = BY + i * 17
    A(txt(AX + 16, row + 9, k, 7, DIM, "400"))
    A(f'<rect x="{BAR_X}" y="{row+1}" width="{BAR_W}" height="9" rx="1.5" '
      f'fill="{BG}" stroke="{LINE}"/>')
    A(f'<rect x="{BAR_X+1}" y="{row+2}" width="{(BAR_W-2)*frac:.0f}" height="7" rx="1" '
      f'fill="{col}" opacity="0.85"/>')
    A(txt(AX + AW - 16, row + 9, val, 7, TEXT, "400", "end"))

# 상태 필
PY_ = AY + AH - 42
A(f'<rect x="{AX+16}" y="{PY_}" width="{AW-32}" height="24" rx="3" fill="{BG}" stroke="{LINE}"/>')
A(f'<circle class="blink" cx="{AX+30}" cy="{PY_+12}" r="3.5" fill="#34d399"/>')
A(txt(AX + 42, PY_ + 15, ACTIVE["pill"], 8, TEXT, "500"))
A(txt(AX + AW - 22, PY_ + 15, ACTIVE["cost"], 7, ACCENT, "500", "end"))

# ── 워크플로 ──────────────────────────────────────────────────────────────
FX, FY, FW, FH = 28, 550, 1144, 92
A(panel(FX, FY, FW, FH))
A(panel_head(FX, FY, FW, "THE DELIVERY LOOP", "DESIGN · SHIP · OBSERVE · REPEAT"))

step = (FW - 72 - 95) / (len(FLOW) - 1)
for i, (name, sub) in enumerate(FLOW):
    x = FX + 36 + step * i
    y = FY + 58
    c = FLOW_COLORS[i]
    A(f'<circle cx="{x:.0f}" cy="{y}" r="9" fill="{c}" opacity="0.18" filter="url(#softglow)"/>')
    A(f'<circle cx="{x:.0f}" cy="{y}" r="4.5" fill="{c}"/>')
    A(txt(x + 14, y + 3, name, 8, TEXT, "600"))
    A(txt(x + 14, y + 16, sub, 6.5, DIM, "400"))
    if i < len(FLOW) - 1:
        A(f'<line x1="{x+ (14 + len(name)*5.6) + 8:.0f}" y1="{y}" x2="{x+step-14:.0f}" y2="{y}" '
          f'stroke="{LINE}" stroke-width="1"/>')
        A(f'<path d="M{x+step-14:.0f},{y-3} L{x+step-9:.0f},{y} L{x+step-14:.0f},{y+3}" '
          f'fill="none" stroke="{DIM}" stroke-width="1"/>')

# ── 인덱스 ────────────────────────────────────────────────────────────────
IX, IY, IW, IH = 28, 656, 1144, 152
A(panel(IX, IY, IW, IH))
A(panel_head(IX, IY, IW, "PROJECT INDEX", "PRIVATE · CODENAMED · NOT LINKED"))

col_w = (IW - 40) / 3.0
for i, (num, label, full, lang, ang, r) in enumerate(NODES):
    col, row = i // 5, i % 5
    x = IX + 20 + col * col_w
    y = IY + 54 + row * 17
    A(txt(x, y, num, 7.5, DIM, "400"))
    A(f'<rect x="{x+20}" y="{y-6}" width="6" height="6" rx="1" fill="{LANG[lang]}"/>')
    A(txt(x + 34, y, full, 8, TEXT, "400", "0.03em"))

A(txt(IX + 20, IY + IH - 14,
      "PUBLIC WORK LIVES AT GITHUB.COM/JSEONGWON — 44 OPEN REPOSITORIES",
      7, DIM, "400", "0.14em"))
A(txt(IX + IW - 20, IY + IH - 14,
      f"GENERATED {datetime.date.today().isoformat()}", 7, DIM, "400", "end", "0.14em"))

A('</svg>')

out = "\n".join(P)
path = __file__.rsplit("/", 1)[0] + "/hero.svg"
with open(path, "w") as f:
    f.write(out)
print(f"wrote {path}  ({len(out)} bytes)")
