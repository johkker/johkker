"""Generates the animated SVG plates in ../assets. Run: python3 _build/build.py

Everything (fonts, images) is embedded as data URIs because GitHub renders
README SVGs as <img>, which can't load external resources.
"""
import base64, math
from pathlib import Path

HERE = Path(__file__).parent
SRC, OUT = HERE / "src", HERE.parent / "assets"

BG, SURF, INK, MUTED, ACC = "#08111b", "#122235", "#eff4f7", "#adbdce", "#b9ddfa"
RULE, TICK = "#a2caea", "#b9ddfa"


def b64(name, mime):
    return f"data:{mime};base64," + base64.b64encode((SRC / name).read_bytes()).decode()


FONTS = (
    "@font-face{font-family:B;src:url(%s)}@font-face{font-family:H;src:url(%s)}@font-face{font-family:M;src:url(%s)}"
    % (b64("bricolage-grotesque.woff2", "font/woff2"), b64("hanken-grotesk.woff2", "font/woff2"), b64("jetbrains-mono.woff2", "font/woff2"))
)
BASE_CSS = f"""
.b{{font-family:B,sans-serif;font-weight:700}} .h{{font-family:H,sans-serif}} .m{{font-family:M,monospace}}
.ink{{fill:{INK}}} .mu{{fill:{MUTED}}} .ac{{fill:{ACC}}}
.ln{{stroke:{ACC};stroke-width:1;fill:none}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w, h, body, css="", title=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<style>{FONTS}{BASE_CSS}{css}</style>
<defs>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{RULE}" stroke-opacity=".12"/></pattern>
<radialGradient id="vig" cx="62%" cy="50%" r="75%"><stop offset="0" stop-color="{BG}" stop-opacity="0"/><stop offset="1" stop-color="{BG}" stop-opacity=".95"/></radialGradient>
</defs>
<rect width="{w}" height="{h}" fill="{BG}"/><rect width="{w}" height="{h}" fill="url(#grid)"/><rect width="{w}" height="{h}" fill="url(#vig)"/>
{ticks(w, h)}
{body}
</svg>"""


def ticks(w, h, m=24, s=18):
    p = f"M{m} {m+s}V{m}H{m+s} M{w-m-s} {m}H{w-m}V{m+s} M{m} {h-m-s}V{h-m}H{m+s} M{w-m-s} {h-m}H{w-m}V{h-m-s}"
    return f'<path d="{p}" stroke="{TICK}" stroke-opacity=".6" fill="none"/>'


def header(fig, title, right="johkker · engineering atlas", w=1280):
    return (
        f'<text x="72" y="70" class="m" font-size="13" letter-spacing="1.2"><tspan class="ac">FIG. {fig}</tspan><tspan class="mu"> — {esc(title)}</tspan></text>'
        f'<text x="{w-72}" y="70" class="m mu" font-size="13" letter-spacing="1.2" text-anchor="end" opacity=".6">{esc(right)}</text>'
        f'<line x1="72" x2="{w-72}" y1="88" y2="88" stroke="{RULE}" stroke-opacity=".18"/>'
    )


# ---------------------------------------------------------------- FIG 01 hero
def hero():
    W, H = 1280, 500
    s = 0.78  # core.webp is 440x563, shown at 343x439
    x0, y0 = 690, 34
    iw, ih = 440 * s, 563 * s
    img = b64("core.webp", "image/webp")
    # vertical bands of the render: left panels | core | right panels (source px)
    bands = [(0, 153), (153, 297), (297, 440)]
    layers = f'<defs><image id="core" href="{img}" x="{x0}" y="{y0}" width="{iw}" height="{ih}"/></defs>'
    for i, (a, b) in enumerate(bands):
        cls = ["pl", "", "pr"][i]
        layers += (
            f'<clipPath id="c{i}"><rect x="{x0 + a*s}" y="{y0}" width="{(b-a)*s}" height="{ih}"/></clipPath>'
            f'<g class="{cls}"><use href="#core" clip-path="url(#c{i})"/></g>'
        )
    # leader lines: (point on the fixed core, label row y, text)
    labels = [((840, 66), 112, "Interface"), ((838, 250), 190, "Core: data &amp; domain"),
              ((900, 330), 268, "Services &amp; APIs"), ((842, 440), 346, "Runs in production")]
    leaders = ""
    for n, ((px, py), ly, t) in enumerate(labels, 1):
        d = f"M{px} {py}L1010 {ly}H1052"
        leaders += (
            f'<path d="{d}" class="ln"/><path d="{d}" class="ln flow" style="animation-delay:{n*0.4}s"/>'
            f'<circle cx="{px}" cy="{py}" r="3.2" class="ac pulse" style="animation-delay:{n*0.4}s"/>'
            f'<text x="1060" y="{ly+5}" class="m ink" font-size="14"><tspan class="ac">{n}</tspan>  {t}</text>'
        )
    phrases = ["legacy platforms → cloud-native", "MVPs, from scope to production", "AI-assisted engineering, in practice"]
    rot = "".join(
        f'<text x="72" y="404" class="m ink rot" font-size="15" style="animation-delay:{i*4}s"><tspan class="ac">$ now</tspan>  {esc(p)}<tspan class="cur ac">▌</tspan></text>'
        for i, p in enumerate(phrases)
    )
    css = """
.pl{animation:pl 7s cubic-bezier(.6,0,.2,1) infinite}.pr{animation:pr 7s cubic-bezier(.6,0,.2,1) infinite}
@keyframes pl{0%,18%{transform:translateX(0)}42%,62%{transform:translateX(30px)}86%,100%{transform:translateX(0)}}
@keyframes pr{0%,18%{transform:translateX(0)}42%,62%{transform:translateX(-30px)}86%,100%{transform:translateX(0)}}
.glow{animation:glow 3.5s ease-in-out infinite;transform-origin:862px 250px}
@keyframes glow{0%,100%{opacity:.25}50%{opacity:.6}}
.scan{animation:scan 5s linear infinite}@keyframes scan{0%{transform:translateY(0);opacity:0}10%{opacity:.9}90%{opacity:.9}100%{transform:translateY(430px);opacity:0}}
.flow{stroke-width:2;stroke-dasharray:6 400;animation:flow 3s linear infinite;opacity:.9}@keyframes flow{from{stroke-dashoffset:406}to{stroke-dashoffset:0}}
.pulse{animation:pulse 1.6s ease-in-out infinite;transform-box:fill-box;transform-origin:center}@keyframes pulse{50%{transform:scale(1.7);opacity:.5}}
.rot{opacity:0;animation:rot 12s infinite}@keyframes rot{0%{opacity:0}3%,30%{opacity:1}33%,100%{opacity:0}}
.cur{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}
"""
    body = f"""
<text x="72" y="96" class="m " font-size="13" letter-spacing="1.3"><tspan class="ac">FIG. 01</tspan><tspan class="mu">  —  SOFTWARE ENGINEER · ARCHITECT · TECH LEAD</tspan></text>
<text x="72" y="160" class="b ink" font-size="30">Johnny Gregorio<tspan class="ac">.</tspan></text>
<text x="70" y="250" class="b ink" font-size="70" letter-spacing="-1.8">Backend depth.</text>
<text x="70" y="324" class="b ac" font-size="70" letter-spacing="-1.8">Full-stack delivery.</text>
{rot}
<text x="72" y="446" class="m mu" font-size="13.5" letter-spacing="1">STACK <tspan class="ink">TypeScript · Node · React</tspan>     BASED <tspan class="ink">Curitiba, BR · Remote</tspan>     SPEAKS <tspan class="ink">EN · PT</tspan></text>
<ellipse class="glow" cx="862" cy="250" rx="70" ry="190" fill="{ACC}" filter="url(#blur)"/>
<filter id="blur"><feGaussianBlur stdDeviation="30"/></filter>
{layers}
<rect class="scan" x="{x0-10}" y="{y0}" width="{iw+20}" height="1.5" fill="{ACC}" opacity=".0"/>
{leaders}
"""
    return svg(W, H, body, css, "Johnny Gregorio — Backend depth. Full-stack delivery.")


# ---------------------------------------------------------------- FIG 02 now
def now():
    W, H = 1280, 600

    def box(x, y, w, h, k, t, sub="", dash=False, cls=""):
        d = ' stroke-dasharray="4 4"' if dash else ""
        s = f'<text x="{x+14}" y="{y+56 if not sub else y+54}" class="h mu" font-size="13.5">{esc(sub)}</text>' if sub else ""
        return (f'<g class="{cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{SURF}" fill-opacity=".55" stroke="{ACC}" stroke-opacity=".45"{d}/>'
                f'<text x="{x+14}" y="{y+22}" class="m ac" font-size="11" letter-spacing="1.2">{esc(k)}</text>'
                f'<text x="{x+14}" y="{y+40}" class="h ink" font-size="15.5">{esc(t)}</text>{s}</g>')

    nodes = [
        box(72, 250, 150, 74, "CLIENTS", "web · mobile", "partners · APIs"),
        box(282, 180, 170, 74, "EDGE", "Ingress · K8s", "TLS · routing"),
        box(282, 300, 170, 74, "BFF", "JWT · throttling", "API gateway"),
        box(282, 120 - 10, 170, 50, "IDENTITY", "OIDC · MFA"),
        box(512, 130, 200, 74, "CONTEXT · A", "bounded context", "DDD"),
        box(512, 230, 200, 74, "CONTEXT · B", "bounded context", "DDD"),
        box(512, 330, 200, 74, "CONTEXT · C", "bounded context", "DDD"),
        box(512, 446, 200, 74, "LEGACY", "monolith", "strangled, route by route", dash=True, cls="legacy"),
        box(970, 130, 210, 60, "STORE", "PostgreSQL"),
        box(970, 210, 210, 60, "STORE", "Cassandra"),
        box(970, 290, 210, 60, "CACHE", "Redis"),
        box(970, 400, 210, 74, "OPS", "Grafana · Prometheus", "Vault · CI/CD"),
    ]
    # event bus
    bus = (f'<rect x="772" y="130" width="130" height="274" fill="{SURF}" fill-opacity=".55" stroke="{ACC}" stroke-opacity=".45"/>'
           f'<text x="786" y="152" class="m ac" font-size="11" letter-spacing="1.2">EVENT BUS</text>'
           f'<text x="786" y="171" class="h ink" font-size="15.5">RabbitMQ</text>'
           + "".join(f'<rect x="790" y="{196+i*34}" width="94" height="22" fill="none" stroke="{ACC}" stroke-opacity=".25"/>'
                     f'<rect x="790" y="{196+i*34}" width="94" height="22" fill="{ACC}" class="q" style="animation-delay:{i*0.4}s"/>' for i in range(6)))
    wires = [
        "M222 287H252V217H282", "M222 287H252V337H282", "M367 254V300", "M367 180V160",
        "M452 337H482V167H512", "M452 337H512", "M452 337H482V367H512",
        "M712 167H772", "M712 267H772", "M712 367H772",
        "M902 200H936V160H970", "M902 240H970", "M902 300H936V320H970",
        "M612 446V404",
    ]
    wire_svg = "".join(f'<path d="{d}" stroke="{ACC}" stroke-opacity=".35" fill="none"/>' for d in wires)
    flows = [
        ("M222 287H252V337H282 M452 337H482V167H512 M712 167H772 M902 200H936V160H970", 0),
        ("M222 287H252V337H282 M452 337H512 M712 267H772 M902 240H970", 1.1),
        ("M222 287H252V337H282 M452 337H482V367H512 M712 367H772 M902 300H936V320H970", 2.2),
        ("M612 446V404", 0.5),
    ]
    packets = "".join(
        f'<circle r="3.5" fill="{ACC}" opacity="0"><animateMotion dur="3.3s" begin="{b}s" repeatCount="indefinite" path="{d}"/>'
        f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.9;1" dur="3.3s" begin="{b}s" repeatCount="indefinite"/></circle>'
        for d, b in flows
    )
    ai = (f'<g class="m" font-size="12"><path d="M1180 520H770" class="ln" stroke-dasharray="2 5" opacity=".6"/>'
          f'<text x="770" y="548" class="ac" letter-spacing="1.1">AI-ASSISTED</text>'
          f'<text x="770" y="566" class="mu">Claude Code · custom agents · MCP tooling</text></g>')
    caption = (f'<text x="72" y="566" class="m mu" font-size="12" opacity=".8">fig. 02 — the kind of system I design, build and keep running.</text>'
               f'<text x="72" y="584" class="m mu" font-size="12" opacity=".5">illustrative, not a client diagram.</text>')
    css = """
.q{opacity:0;animation:q 2.4s ease-in-out infinite}@keyframes q{0%,100%{opacity:0}40%,60%{opacity:.35}}
.legacy{animation:leg 6s ease-in-out infinite}@keyframes leg{0%,100%{opacity:.9}50%{opacity:.35}}
"""
    body = header("02", "NOW · SOFTWARE ARCHITECT & TECH LEAD @ ARCHOFFICE") + wire_svg + "".join(nodes) + bus + packets + ai + caption
    return svg(W, H, body, css, "Diagram of the kind of cloud-native system I design: clients, edge, BFF, bounded contexts, event bus, data stores, observability.")


# ---------------------------------------------------------------- specimens
def specimen(letter, name, img, status, live, lines, tags, out):
    W, H = 600, 800
    pulse = '<circle cx="44" cy="0" r="5" class="ac pulse"/>' if live else f'<circle cx="44" cy="0" r="5" fill="none" stroke="{ACC}"/>'
    tag_svg, x = "", 40
    for t in tags:
        w = len(t) * 10.8 + 26
        tag_svg += (f'<rect x="{x}" y="676" width="{w}" height="36" fill="none" stroke="{ACC}" stroke-opacity=".5"/>'
                    f'<text x="{x+13}" y="700" class="m ink" font-size="18">{esc(t)}</text>')
        x += w + 10
    text = "".join(f'<text x="40" y="{540+i*34}" class="h mu" font-size="24">{esc(l)}</text>' for i, l in enumerate(lines))
    body = f"""
<text x="40" y="66" class="m" font-size="18" letter-spacing="2"><tspan class="ac">SPECIMEN {letter}</tspan><tspan class="mu" opacity=".6">  ·  johkker/atlas</tspan></text>
<line x1="40" x2="560" y1="88" y2="88" stroke="{RULE}" stroke-opacity=".25"/>
<clipPath id="shot"><rect x="40" y="112" width="520" height="325"/></clipPath>
<image href="{b64(img, 'image/webp')}" x="40" y="112" width="520" height="325" preserveAspectRatio="xMidYMin slice" clip-path="url(#shot)"/>
<rect x="40" y="112" width="520" height="325" fill="none" stroke="{ACC}" stroke-opacity=".35"/>
<rect x="40" y="112" width="520" height="2" fill="{ACC}" class="scan"/>
<text x="40" y="496" class="b ink" font-size="50" letter-spacing="-1">{esc(name)}</text>
{text}
<g transform="translate(0,634)">{pulse}<text x="62" y="6" class="m ac" font-size="18" letter-spacing="1.6">{esc(status)}</text></g>
{tag_svg}
<text x="560" y="760" class="m mu" font-size="18" text-anchor="end">view case →</text>
"""
    css = """
.pulse{animation:pulse 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(1.6)}}
.scan{opacity:.0;animation:scan 4.5s linear infinite}@keyframes scan{0%{transform:translateY(0);opacity:0}8%{opacity:.8}92%{opacity:.8}100%{transform:translateY(323px);opacity:0}}
"""
    (OUT / out).write_text(svg(W, H, body, css, f"{name}: {' '.join(lines)}"))


# ---------------------------------------------------------------- FIG 04 periodic table
CATS = {
    "lang": ("#b9ddfa", "languages"), "back": ("#8fe3cf", "backend"), "front": ("#c9b8ff", "frontend & mobile"),
    "data": ("#f3cf8a", "data"), "msg": ("#f4a9c0", "messaging"), "arch": ("#c8e88f", "architecture"),
    "sec": ("#ffb38a", "identity & security"), "ai": ("#7ff0ff", "AI tooling"), "infra": ("#adbdce", "cloud & ops"),
}
ELEMENTS = [  # (row, col, symbol, name, category)
    (0, 0, "Ts", "TypeScript", "lang"), (0, 1, "Js", "JavaScript", "lang"), (0, 10, "Cc", "Claude Code", "ai"), (0, 11, "Mcp", "MCP", "ai"),
    (1, 0, "Py", "Python", "lang"), (1, 1, "Nd", "Node.js", "back"),
    (1, 6, "Dd", "DDD", "arch"), (1, 7, "Ms", "Microservices", "arch"), (1, 8, "Ev", "Event-driven", "arch"), (1, 9, "Bf", "BFF", "arch"), (1, 10, "Adr", "ADRs", "arch"), (1, 11, "Ag", "Agents", "ai"),
    (2, 0, "Cs", "C# / .NET", "lang"), (2, 1, "Ns", "NestJS", "back"), (2, 2, "Ex", "Express", "back"), (2, 3, "Fy", "Fastify", "back"),
    (2, 4, "Re", "React", "front"), (2, 5, "Nx", "Next.js", "front"), (2, 6, "Rn", "React Native", "front"), (2, 7, "As", "Astro", "front"), (2, 8, "Vu", "Vue", "front"),
    (2, 9, "Oa", "OAuth / OIDC", "sec"), (2, 10, "Kc", "Keycloak", "sec"), (2, 11, "Mf", "MFA", "sec"),
    (3, 0, "Pg", "PostgreSQL", "data"), (3, 1, "Ca", "Cassandra", "data"), (3, 2, "Rd", "Redis", "data"), (3, 3, "Mg", "MongoDB", "data"), (3, 4, "Dz", "Drizzle", "data"), (3, 5, "To", "TypeORM", "data"),
    (3, 6, "Rq", "RabbitMQ", "msg"), (3, 7, "Sqs", "AWS SQS", "msg"), (3, 8, "Af", "Airflow", "msg"), (3, 9, "Ws", "WebSocket", "msg"),
    (3, 10, "Pci", "PCI-DSS", "sec"), (3, 11, "Az", "Entra ID", "sec"),
    (5, 2, "Dk", "Docker", "infra"), (5, 3, "K8s", "Kubernetes", "infra"), (5, 4, "Ak", "Azure AKS", "infra"), (5, 5, "Do", "DigitalOcean", "infra"),
    (5, 6, "Gf", "Grafana", "infra"), (5, 7, "Pr", "Prometheus", "infra"), (5, 8, "Vt", "Vault", "infra"), (5, 9, "Ng", "NGINX", "infra"), (5, 10, "Ci", "CI/CD", "infra"),
]


def elements():
    W, H = 1280, 760
    tw, th, g, x0, y0 = 88, 96, 8, 72, 118
    tiles = ""
    for n, (r, c, sym, name, cat) in enumerate(sorted(ELEMENTS), 1):
        col = CATS[cat][0]
        x = x0 + c * (tw + g)
        y = y0 + r * (th + g) - (36 if r == 5 else 0)
        delay = (c * 0.12 + r * 0.05)
        fs = 30 if len(sym) < 3 else 25
        tiles += (
            f'<g><rect x="{x}" y="{y}" width="{tw}" height="{th}" fill="{col}" fill-opacity=".07" stroke="{col}" stroke-opacity=".55"/>'
            f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" fill="{col}" class="wave" style="animation-delay:{delay:.2f}s"/>'
            f'<text x="{x+8}" y="{y+17}" class="m" fill="{col}" font-size="10.5">{n}</text>'
            f'<text x="{x+tw/2}" y="{y+59}" class="b ink" font-size="{fs}" text-anchor="middle">{esc(sym)}</text>'
            f'<text x="{x+tw/2}" y="{y+82}" class="m mu" font-size="{10 if len(name) > 11 else 11.5}" text-anchor="middle">{esc(name)}</text></g>'
        )
    # legend + title in the gap, like the real table
    lx, ly = x0 + 2 * (tw + g) + 6, y0 + 8
    legend = f'<text x="{lx}" y="{ly+22}" class="b ink" font-size="30" letter-spacing="-.5">Periodic table of the stack</text>'
    legend += f'<text x="{lx}" y="{ly+50}" class="h mu" font-size="15">Elements I work with, grouped by family. Backend-heavy, by nature.</text>'
    for i, (k, (col, label)) in enumerate(CATS.items()):
        cx = lx + (i // 5) * 190
        cy = y0 + th + g + 18 + (i % 5) * 18
        legend += f'<rect x="{cx}" y="{cy-10}" width="11" height="11" fill="{col}"/><text x="{cx+20}" y="{cy}" class="m mu" font-size="12">{esc(label)}</text>'
    lanth = f'<text x="{x0}" y="{y0+5*(th+g)-36+54}" class="m mu" font-size="11" letter-spacing="1">CLOUD &amp; OPS</text><text x="{x0}" y="{y0+5*(th+g)-36+70}" class="m mu" font-size="11" opacity=".6">series ⟶</text>'
    css = ".wave{opacity:0;animation:wave 6s ease-in-out infinite}@keyframes wave{0%,100%{opacity:0}12%{opacity:.22}30%{opacity:0}}"
    return svg(W, H, header("04", "PERIODIC TABLE OF THE STACK") + legend + tiles + lanth, css,
               "Periodic table of the stack: " + ", ".join(e[3] for e in ELEMENTS))


# ---------------------------------------------------------------- FIG 05 genome
def genome():
    W, H = 1280, 470
    cy, amp, x0, x1, n = 270, 52, 90, 1190, 56
    dur, period = 5.0, 18  # rungs per helix turn
    bases = ["#b9ddfa", "#8fe3cf", "#f3cf8a", "#f4a9c0"]
    samples = 16
    sin = [math.sin(2 * math.pi * k / samples) for k in range(samples + 1)]
    ya = ";".join(f"{cy + amp*v:.1f}" for v in sin)
    yb = ";".join(f"{cy - amp*v:.1f}" for v in sin)
    ra = ";".join(f"{4.2 + 1.8*math.cos(2*math.pi*k/samples):.2f}" for k in range(samples + 1))
    rb = ";".join(f"{4.2 - 1.8*math.cos(2*math.pi*k/samples):.2f}" for k in range(samples + 1))
    helix = ""
    for i in range(n):
        x = x0 + i * (x1 - x0) / (n - 1)
        b = f"-{(i % period) / period * dur:.3f}s"
        a = f'dur="{dur}s" begin="{b}" repeatCount="indefinite"'
        helix += (
            f'<line x1="{x}" x2="{x}" stroke="{bases[i % 4]}" stroke-opacity=".45" stroke-width="2">'
            f'<animate attributeName="y1" values="{ya}" {a}/><animate attributeName="y2" values="{yb}" {a}/></line>'
            f'<circle cx="{x}" fill="{ACC}"><animate attributeName="cy" values="{ya}" {a}/><animate attributeName="r" values="{ra}" {a}/></circle>'
            f'<circle cx="{x}" fill="{INK}" fill-opacity=".8"><animate attributeName="cy" values="{yb}" {a}/><animate attributeName="r" values="{rb}" {a}/></circle>'
        )
    genes = [  # (start, end, symbol, note, above)
        (0.02, 0.22, "BIOMED", "studying Biomedicine", True),
        (0.25, 0.44, "ARAPE", "runs an independent record label", False),
        (0.47, 0.64, "RHYME", "around Brazil's rap battle scene", True),
        (0.67, 0.83, "FINEART", "fine-arts background", False),
        (0.76, 0.97, "PILOT", "flew a plane before driving a car", True),
    ]
    ann = ""
    for i, (s, e, sym, note, above) in enumerate(genes):
        a, b = x0 + s * (x1 - x0), x0 + e * (x1 - x0)
        y = cy - amp - 26 if above else cy + amp + 26
        t = y - 14 if above else y + 26
        t2 = t - 18 if above else t + 18
        tick = -8 if above else 8
        ann += (
            f'<g class="gene" style="animation-delay:{i*0.9}s"><path d="M{a} {y+tick}V{y}H{b}V{y+tick}" class="ln"/>'
            f'<text x="{a}" y="{t}" class="m ac" font-size="14" font-style="italic" letter-spacing="1">{sym}</text>'
            f'<text x="{a}" y="{t2}" class="h mu" font-size="16.5">{esc(note)}</text></g>'
        )
    css = ".gene{animation:gene 4.5s ease-in-out infinite}@keyframes gene{0%,100%{opacity:.55}20%{opacity:1}}"
    body = header("05", "ANNOTATED GENOME · OFF THE CLOCK") + helix + ann
    return svg(W, H, body, css, "Off the clock: studying Biomedicine, runs an independent record label, around Brazil's rap battle scene, fine-arts background, flew a plane before driving a car.")


# ---------------------------------------------------------------- end card
def endcard():
    W, H = 1280, 300
    body = f"""
<circle cx="190" cy="150" r="74" fill="none" stroke="{ACC}" stroke-opacity=".7"/>
<circle cx="190" cy="150" r="88" fill="none" stroke="{ACC}" stroke-opacity=".25" stroke-dasharray="3 7" class="spin"/>
<text x="190" y="168" class="b ink" font-size="54" text-anchor="middle" letter-spacing="-1">jg<tspan class="ac">.</tspan></text>
<text x="320" y="118" class="m ac" font-size="13" letter-spacing="1.3">END OF ATLAS · STATUS: AVAILABLE<tspan class="cur">▌</tspan></text>
<text x="320" y="166" class="b ink" font-size="38" letter-spacing="-.8">Let’s build the next system together.</text>
<text x="320" y="204" class="h mu" font-size="18">Open to remote contracts, technical consulting and full-time roles.</text>
<text x="320" y="236" class="m mu" font-size="13.5">johnnygregorio.tech  ·  linkedin.com/in/johkker  ·  johkker@gmail.com</text>
"""
    css = """.spin{animation:spin 30s linear infinite;transform-origin:190px 150px}@keyframes spin{to{transform:rotate(360deg)}}
.cur{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"""
    return svg(W, H, body, css, "Open to remote contracts, technical consulting and full-time roles.")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "hero.svg").write_text(hero())
    (OUT / "now.svg").write_text(now())
    specimen("A", "Arapé Records", "arape.webp", "LIVE PLATFORM", True,
             ["My independent record label and the", "internal tools that run it."], ["Next.js", "NestJS", "Postgres"], "specimen-arape.svg")
    specimen("B", "Cumpri", "cumpri.webp", "WEB APP · PWA", True,
             ["Group challenges with a deadline:", "check-ins, streaks and rankings."], ["React", "Fastify", "Drizzle"], "specimen-cumpri.svg")
    specimen("C", "RapTrak", "raptrak.webp", "FUNCTIONAL · UNRELEASED", False,
             ["Find the next rap battle, and build", "the scene around it."], ["React Native", "Express"], "specimen-raptrak.svg")
    (OUT / "elements.svg").write_text(elements())
    (OUT / "genome.svg").write_text(genome())
    (OUT / "endcard.svg").write_text(endcard())
    for f in sorted(OUT.glob("*.svg")):
        print(f.name, f.stat().st_size // 1024, "KB")
