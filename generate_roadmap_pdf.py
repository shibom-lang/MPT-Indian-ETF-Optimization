#!/usr/bin/env python3
"""
generate_roadmap_pdf.py — Generates a high-impact, visual vector PDF roadmap
for Indian ETF Quant Engine v2.0 without third-party dependencies.
Produces:
  1. output/ETF_Quant_v2_Roadmap.pdf (Vector PDF, 2 landscape pages)
  2. output/roadmap.html (Interactive visual companion)
"""

import os
import pathlib
import datetime

OUTPUT_DIR = pathlib.Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
PDF_PATH = OUTPUT_DIR / "ETF_Quant_v2_Roadmap.pdf"
HTML_PATH = OUTPUT_DIR / "roadmap.html"


class VectorPDF:
    def __init__(self, width=842, height=595):
        self.width = width
        self.height = height
        self.pages = []
        self.current_stream = []

    def new_page(self):
        if self.current_stream:
            self.pages.append(" ".join(self.current_stream))
            self.current_stream = []

    def _add(self, cmd):
        self.current_stream.append(cmd)

    def set_fill(self, r, g, b):
        self._add(f"{r:.3f} {g:.3f} {b:.3f} rg")

    def set_stroke(self, r, g, b):
        self._add(f"{r:.3f} {g:.3f} {b:.3f} RG")

    def set_line_width(self, w):
        self._add(f"{w:.2f} w")

    def rect(self, x, y, w, h, fill=True, stroke=False):
        self._add(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re")
        if fill and stroke:
            self._add("B")
        elif fill:
            self._add("f")
        elif stroke:
            self._add("S")

    def rounded_rect(self, x, y, w, h, r=6, fill=True, stroke=False):
        # Approximated rounded rectangle using bezier curves
        k = 0.5522847498 * r
        self._add(f"{x+r:.2f} {y:.2f} m")
        self._add(f"{x+w-r:.2f} {y:.2f} l")
        self._add(f"{x+w-r+k:.2f} {y:.2f} {x+w:.2f} {y+k:.2f} {x+w:.2f} {y+r:.2f} c")
        self._add(f"{x+w:.2f} {y+h-r:.2f} l")
        self._add(f"{x+w:.2f} {y+h-r+k:.2f} {x+w-r+k:.2f} {y+h:.2f} {x+w-r:.2f} {y+h:.2f} c")
        self._add(f"{x+r:.2f} {y+h:.2f} l")
        self._add(f"{x+r-k:.2f} {y+h:.2f} {x:.2f} {y+h-r+k:.2f} {x:.2f} {y+h-r:.2f} c")
        self._add(f"{x:.2f} {y+r:.2f} l")
        self._add(f"{x:.2f} {y+r-k:.2f} {x+r-k:.2f} {y:.2f} {x+r:.2f} {y:.2f} c")
        if fill and stroke:
            self._add("B")
        elif fill:
            self._add("f")
        elif stroke:
            self._add("S")

    def line(self, x1, y1, x2, y2):
        self._add(f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def circle(self, cx, cy, r, fill=True, stroke=False):
        k = 0.5522847498 * r
        self._add(f"{cx+r:.2f} {cy:.2f} m")
        self._add(f"{cx+r:.2f} {cy+k:.2f} {cx+k:.2f} {cy+r:.2f} {cx:.2f} {cy+r:.2f} c")
        self._add(f"{cx-k:.2f} {cy+r:.2f} {cx-r:.2f} {cy+k:.2f} {cx-r:.2f} {cy:.2f} c")
        self._add(f"{cx-r:.2f} {cy-k:.2f} {cx-k:.2f} {cy-r:.2f} {cx:.2f} {cy-r:.2f} c")
        self._add(f"{cx+k:.2f} {cy-r:.2f} {cx+r:.2f} {cy-k:.2f} {cx+r:.2f} {cy:.2f} c")
        if fill and stroke:
            self._add("B")
        elif fill:
            self._add("f")
        elif stroke:
            self._add("S")

    def text(self, x, y, text_str, font="F1", size=10, fill_rgb=(1, 1, 1)):
        r, g, b = fill_rgb
        # Escape parenthesis
        clean_text = text_str.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        self._add(f"BT /{font} {size:.2f} Tf {r:.3f} {g:.3f} {b:.3f} rg {x:.2f} {y:.2f} Td ({clean_text}) Tj ET")

    def compile(self) -> bytes:
        if self.current_stream:
            self.pages.append(" ".join(self.current_stream))

        objects = []

        def add_obj(content):
            objects.append(content)
            return len(objects)

        # 1: Catalog
        catalog_id = 1
        # 2: Pages
        pages_id = 2
        # Fonts
        f1_id = 3  # Helvetica
        f2_id = 4  # Helvetica-Bold

        page_ids = []
        stream_ids = []

        # Reserve IDs for pages and streams
        cur_id = 5
        for _ in self.pages:
            page_ids.append(cur_id)
            stream_ids.append(cur_id + 1)
            cur_id += 2

        # Obj 1: Catalog
        obj1 = f"{catalog_id} 0 obj\n<< /Type /Catalog /Pages {pages_id} 0 R >>\nendobj\n"
        # Obj 2: Pages
        kids_str = " ".join([f"{pid} 0 R" for pid in page_ids])
        obj2 = f"{pages_id} 0 obj\n<< /Type /Pages /Kids [{kids_str}] /Count {len(page_ids)} >>\nendobj\n"
        # Obj 3: F1 (Helvetica)
        obj3 = f"{f1_id} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>\nendobj\n"
        # Obj 4: F2 (Helvetica-Bold)
        obj4 = f"{f2_id} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>\nendobj\n"

        all_objs = [obj1, obj2, obj3, obj4]

        for i, page_stream in enumerate(self.pages):
            pid = page_ids[i]
            sid = stream_ids[i]
            stream_bytes = page_stream.encode("latin-1", errors="replace")
            slen = len(stream_bytes)

            p_obj = (
                f"{pid} 0 obj\n"
                f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {self.width} {self.height}] "
                f"/Resources << /Font << /F1 {f1_id} 0 R /F2 {f2_id} 0 R >> >> "
                f"/Contents {sid} 0 R >>\nendobj\n"
            )
            s_obj = (
                f"{sid} 0 obj\n"
                f"<< /Length {slen} >>\nstream\n"
                f"{page_stream}\nendstream\nendobj\n"
            )
            all_objs.append(p_obj)
            all_objs.append(s_obj)

        # Build xref table
        header = "%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"
        body = ""
        xref_offsets = [0]
        cur_offset = len(header)

        for obj in all_objs:
            xref_offsets.append(cur_offset)
            body += obj
            cur_offset += len(obj.encode("latin-1"))

        xref_pos = cur_offset
        xref = f"xref\n0 {len(xref_offsets)}\n0000000000 65535 f \n"
        for off in xref_offsets[1:]:
            xref += f"{off:010d} 00000 n \n"

        trailer = (
            f"trailer\n<< /Size {len(xref_offsets)} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n"
        )

        return (header + body + xref + trailer).encode("latin-1")


def generate_roadmap():
    pdf = VectorPDF(width=842, height=595)

    # ═════════════════════════════════════════════════════════════════════════
    # PAGE 1: STRATEGIC EXECUTION ROADMAP & 4 PHASES
    # ═════════════════════════════════════════════════════════════════════════
    pdf.new_page()

    # Dark background: Navy Slate #0B1120
    pdf.set_fill(0.043, 0.067, 0.125)
    pdf.rect(0, 0, 842, 595, fill=True)

    # Header Card: #1E293B with border #334155
    pdf.set_fill(0.118, 0.161, 0.231)
    pdf.set_stroke(0.200, 0.255, 0.333)
    pdf.set_line_width(1.2)
    pdf.rounded_rect(24, 495, 794, 76, r=8, fill=True, stroke=True)

    # Header Pill Badge: Cyan #0284C7
    pdf.set_fill(0.008, 0.518, 0.780)
    pdf.rounded_rect(36, 545, 185, 18, r=9, fill=True)
    pdf.text(44, 550, "STRATEGIC EXECUTION ROADMAP", font="F2", size=8.5, fill_rgb=(1, 1, 1))

    # Version Pill
    pdf.set_fill(0.063, 0.725, 0.506)  # Emerald
    pdf.rounded_rect(228, 545, 80, 18, r=9, fill=True)
    pdf.text(236, 550, "VERSION 2.0", font="F2", size=8.5, fill_rgb=(1, 1, 1))

    # Title & Subtitle
    pdf.text(36, 522, "Indian ETF Quantitative Engine & Time Series Platform", font="F2", size=18, fill_rgb=(0.95, 0.98, 1))
    pdf.text(36, 504, "From Static Modern Portfolio Theory to Multi-Asset, Rolling Econometrics & Institutional Risk Management", font="F1", size=10, fill_rgb=(0.58, 0.65, 0.75))

    # KPI Bar (4 metrics): Y = 442, H = 42
    kpis = [
        ("UNIVERSE EXPANSION", "8+ Curated ETFs", "Midcap, Nasdaq, Silver, G-Sec", (0.06, 0.72, 0.51)),
        ("TIME SERIES MODELING", "Rolling Sharpe & Vol", "EWMA Volatility Clustering", (0.24, 0.58, 0.98)),
        ("STRESS TESTING", "3 Crisis Windows", "COVID, 2022 Hikes, 2024 Shock", (0.96, 0.62, 0.04)),
        ("ARCHITECTURE", "100% Automated", "Vercel Serverless + PDF Engine", (0.66, 0.38, 0.98)),
    ]
    card_w = 191
    gap = 10
    start_x = 24
    for i, (tag, val, sub, col) in enumerate(kpis):
        x = start_x + i * (card_w + gap)
        pdf.set_fill(0.082, 0.114, 0.173)
        pdf.set_stroke(0.180, 0.235, 0.314)
        pdf.set_line_width(1)
        pdf.rounded_rect(x, 442, card_w, 42, r=6, fill=True, stroke=True)

        # Color Accent Tab
        pdf.set_fill(*col)
        pdf.rounded_rect(x + 2, 444, 4, 38, r=2, fill=True)

        pdf.text(x + 12, 468, tag, font="F2", size=7.5, fill_rgb=(0.58, 0.65, 0.75))
        pdf.text(x + 12, 455, val, font="F2", size=11, fill_rgb=(0.95, 0.98, 1))
        pdf.text(x + 12, 445, sub, font="F1", size=7, fill_rgb=(0.45, 0.52, 0.62))

    # 4 MASTER PHASES (Columns): Y = 110, H = 320
    phases = [
        {
            "num": "01",
            "title": "Multi-Asset Universe",
            "subtitle": "Eliminate Redundancy & Add Alpha",
            "badge": "FOUNDATION",
            "badge_col": (0.06, 0.72, 0.51),
            "items": [
                ("Add MID150BEES", "Captures high-growth Indian midcap alpha beyond large-caps."),
                ("Add MON100 (Nasdaq)", "Global tech exposure + natural USD currency depreciation hedge."),
                ("Add SILVERBEES", "Dual commodity hedge alongside Gold; industrial demand beta."),
                ("Add GSEC10IETF", "10-Yr Sovereign G-Sec; real bond yield vs low-return LiquidBees."),
                ("Split Healing Engine", "Auto-interpolates 1:10 split artifacts across all historical series."),
            ],
            "footer": "Tech: yfinance, pandas, split-healer",
        },
        {
            "num": "02",
            "title": "Time Series Modeling",
            "subtitle": "Dynamic Risk & Regime Shifts",
            "badge": "ECONOMETRICS",
            "badge_col": (0.24, 0.58, 0.98),
            "items": [
                ("Rolling Sharpe & Sortino", "180d & 365d rolling windows reveal regime-dependent decay."),
                ("Rolling Volatility Curve", "Visualizes volatility divergence between equities & gold."),
                ("EWMA Volatility Clustering", "RiskMetrics decay (lambda=0.94) tracks dynamic variance shocks."),
                ("Dynamic Beta Tracking", "Measures shifting correlation of Midcap & Bank vs Nifty 50."),
                ("Correlation Heatmap Matrix", "Pairwise 8x8 matrix exposing low/negative asset linkages."),
            ],
            "footer": "Tech: scipy.stats, numpy, EWMA engine",
        },
        {
            "num": "03",
            "title": "Backtests & Stress Tests",
            "subtitle": "Real-World Performance Proof",
            "badge": "VALIDATION",
            "badge_col": (0.96, 0.62, 0.04),
            "items": [
                ("Walk-Forward Rebalancing", "Quarterly & annual rebalancing vs static buy-and-hold."),
                ("COVID-19 Crash Test", "Stress testing drawdown & recovery during Feb-Apr 2020."),
                ("2022 Inflation Shock", "Performance through RBI/Fed rate hikes & tech correction."),
                ("2024 Election Volatility", "Analyzing multi-asset cushion against political gaps."),
                ("Tail Risk & CVaR (95%)", "Quantifies conditional value at risk during the worst 5% days."),
            ],
            "footer": "Tech: SLSQP, Dirichlet Monte Carlo",
        },
        {
            "num": "04",
            "title": "Web Simulator & Reports",
            "subtitle": "Interactive Tool & PDF Export",
            "badge": "DEPLOYMENT",
            "badge_col": (0.66, 0.38, 0.98),
            "items": [
                ("Custom Preset Baskets", "Toggle Classic 5, All-Weather 7, or Pure Equity Alpha."),
                ("Head-to-Head Compare UI", "Side-by-side radar metrics comparing any two ETFs directly."),
                ("Interactive Stress Simulator", "Sliders to test portfolio survival in a 20% equity crash."),
                ("Institutional 12-Page PDF", "Auto-compiled executive brief with clean print typography."),
                ("25+ Pytest Test Suite", "Full test coverage ensuring zero look-ahead bias."),
            ],
            "footer": "Tech: Vanilla JS, Chart.js, Vercel Serverless",
        },
    ]

    p_w = 191
    p_gap = 10
    for i, p in enumerate(phases):
        px = start_x + i * (p_w + p_gap)
        py = 105
        ph = 325

        # Card Box
        pdf.set_fill(0.071, 0.098, 0.153)
        pdf.set_stroke(0.180, 0.235, 0.314)
        pdf.set_line_width(1)
        pdf.rounded_rect(px, py, p_w, ph, r=7, fill=True, stroke=True)

        # Header area
        pdf.set_fill(0.094, 0.133, 0.200)
        pdf.rounded_rect(px + 1, py + ph - 55, p_w - 2, 54, r=6, fill=True)

        # Phase Number Badge
        pdf.set_fill(*p["badge_col"])
        pdf.rounded_rect(px + 8, py + ph - 26, 24, 18, r=4, fill=True)
        pdf.text(px + 13, py + ph - 22, p["num"], font="F2", size=9, fill_rgb=(1, 1, 1))

        # Pill
        pdf.text(px + 38, py + ph - 22, p["badge"], font="F2", size=7.5, fill_rgb=(0.7, 0.8, 0.9))

        # Title & Subtitle
        pdf.text(px + 8, py + ph - 40, p["title"], font="F2", size=10.5, fill_rgb=(0.95, 0.98, 1))
        pdf.text(px + 8, py + ph - 50, p["subtitle"], font="F1", size=7, fill_rgb=(0.58, 0.65, 0.75))

        # Bullet Items
        iy = py + ph - 70
        for b_title, b_desc in p["items"]:
            # Dot
            pdf.set_fill(*p["badge_col"])
            pdf.circle(px + 12, iy - 2, 2.5, fill=True)

            pdf.text(px + 18, iy, b_title, font="F2", size=8, fill_rgb=(0.90, 0.94, 0.99))
            iy -= 11
            # Split description if needed or print compact
            pdf.text(px + 18, iy, b_desc[:40], font="F1", size=6.5, fill_rgb=(0.55, 0.62, 0.72))
            iy -= 10
            if len(b_desc) > 40:
                pdf.text(px + 18, iy, b_desc[40:80], font="F1", size=6.5, fill_rgb=(0.55, 0.62, 0.72))
                iy -= 12
            else:
                iy -= 2

        # Card Footer
        pdf.set_fill(0.051, 0.071, 0.114)
        pdf.rounded_rect(px + 6, py + 8, p_w - 12, 18, r=4, fill=True)
        pdf.text(px + 10, py + 13, p["footer"], font="F1", size=6.5, fill_rgb=(0.45, 0.52, 0.62))

    # Bottom Timeline Bar: Y = 28, H = 64
    pdf.set_fill(0.118, 0.161, 0.231)
    pdf.set_stroke(0.200, 0.255, 0.333)
    pdf.set_line_width(1)
    pdf.rounded_rect(24, 26, 794, 66, r=8, fill=True, stroke=True)

    pdf.text(36, 72, "EXECUTION TIMELINE & MILESTONES", font="F2", size=9, fill_rgb=(0.06, 0.72, 0.51))
    pdf.text(280, 72, "Estimated Duration: 3-4 Focused Sprints", font="F1", size=8.5, fill_rgb=(0.58, 0.65, 0.75))

    # Milestones Track
    m_steps = [
        ("Sprint 1", "Universe Expansion & Ingestion", "Days 1-3", 100),
        ("Sprint 2", "Time Series & Rolling Engine", "Days 4-7", 295),
        ("Sprint 3", "Backtesting & Stress Tests", "Days 8-11", 490),
        ("Sprint 4", "Web UI Simulator & PDF Suite", "Days 12-14", 685),
    ]
    # Line
    pdf.set_stroke(0.28, 0.35, 0.45)
    pdf.set_line_width(2)
    pdf.line(50, 48, 770, 48)

    for tag, name, span, mx in m_steps:
        pdf.set_fill(0.06, 0.72, 0.51)
        pdf.circle(mx, 48, 5, fill=True)
        pdf.text(mx - 15, 55, tag, font="F2", size=7.5, fill_rgb=(0.95, 0.98, 1))
        pdf.text(mx - 25, 36, name[:24], font="F1", size=6.5, fill_rgb=(0.8, 0.85, 0.92))
        pdf.text(mx - 15, 29, span, font="F1", size=6, fill_rgb=(0.45, 0.52, 0.62))

    # ═════════════════════════════════════════════════════════════════════════
    # PAGE 2: ARCHITECTURE & ETF BASKET BENCHMARK
    # ═════════════════════════════════════════════════════════════════════════
    pdf.new_page()

    # Background
    pdf.set_fill(0.043, 0.067, 0.125)
    pdf.rect(0, 0, 842, 595, fill=True)

    # Header Card
    pdf.set_fill(0.118, 0.161, 0.231)
    pdf.set_stroke(0.200, 0.255, 0.333)
    pdf.set_line_width(1.2)
    pdf.rounded_rect(24, 508, 794, 63, r=8, fill=True, stroke=True)

    pdf.text(36, 546, "ARCHITECTURAL BLUEPRINT & UNIVERSE COMPARISON", font="F2", size=15, fill_rgb=(0.95, 0.98, 1))
    pdf.text(36, 528, "Solving Correlation Redundancy, Cash Drag & Model Fragility with Modern Multi-Asset Quant Engineering", font="F1", size=9.5, fill_rgb=(0.58, 0.65, 0.75))

    # Left Box: Basket Comparison Table (X=24, Y=145, W=460, H=350)
    pdf.set_fill(0.071, 0.098, 0.153)
    pdf.set_stroke(0.180, 0.235, 0.314)
    pdf.set_line_width(1)
    pdf.rounded_rect(24, 145, 465, 350, r=8, fill=True, stroke=True)

    pdf.text(36, 474, "ETF BASKET UPGRADE: v1.0 (CLASSIC) vs v2.0 (ALL-WEATHER)", font="F2", size=10, fill_rgb=(0.06, 0.72, 0.51))
    pdf.text(36, 460, "Strategic shift from bank-heavy equity to true non-correlated multi-asset allocation", font="F1", size=7.5, fill_rgb=(0.55, 0.62, 0.72))

    # Table Header: Y=436
    pdf.set_fill(0.118, 0.161, 0.231)
    pdf.rounded_rect(34, 436, 445, 18, r=4, fill=True)
    pdf.text(40, 442, "TICKER", font="F2", size=7.5, fill_rgb=(0.9, 0.95, 1))
    pdf.text(115, 442, "ASSET CLASS", font="F2", size=7.5, fill_rgb=(0.9, 0.95, 1))
    pdf.text(210, 442, "ROLE IN PORTFOLIO", font="F2", size=7.5, fill_rgb=(0.9, 0.95, 1))
    pdf.text(360, 442, "v1.0 ISSUE / v2.0 BENEFIT", font="F2", size=7.5, fill_rgb=(0.9, 0.95, 1))

    table_rows = [
        ("NIFTYBEES.NS", "Large-Cap Equity", "Core India Growth Anchor", "Baseline market return; high liquidity", (0.38, 0.65, 0.98)),
        ("JUNIORBEES.NS", "Large/Mid Next 50", "Growth & Beta Booster", "Higher CAGR; complements Nifty 50", (0.94, 0.27, 0.27)),
        ("BANKBEES.NS", "Banking Sector", "Financial Sector Alpha", "OVERLAPS: 82% corr with Nifty; 0% weight", (0.96, 0.62, 0.04)),
        ("MID150BEES.NS", "Mid-Cap 150 (NEW)", "Alpha & Factor Premium", "REPLACES BANK: Real midcap diversification", (0.06, 0.72, 0.51)),
        ("MON100.NS", "US Nasdaq 100 (NEW)", "Global Tech + Currency Hedge", "PROTECTS INR: Low correlation to Nifty", (0.66, 0.38, 0.98)),
        ("GOLDBEES.NS", "Precious Metal", "Crisis Ballast & Safe Haven", "Zero correlation to stocks; proven hedge", (0.98, 0.75, 0.14)),
        ("SILVERBEES.NS", "Precious Metal (NEW)", "Industrial Commodity Beta", "High volatility commodity upside kicker", (0.80, 0.85, 0.90)),
        ("GSEC10IETF.NS", "10-Yr Sovereign (NEW)", "Long-Duration Bond Yield", "REPLACES LIQUID: 7.0% yield + capital gain", (0.20, 0.80, 0.70)),
        ("LIQUIDBEES.NS", "Cash Equivalent", "Dry Powder & Rebalance Pool", "Zero vol, but acts as a long-term return drag", (0.65, 0.55, 0.98)),
    ]

    ty = 416
    for t_sym, t_cls, t_role, t_note, t_col in table_rows:
        # Alternating background
        if "NEW" in t_sym or "NEW" in t_note:
            pdf.set_fill(0.08, 0.14, 0.18)
        else:
            pdf.set_fill(0.06, 0.08, 0.13)
        pdf.rounded_rect(34, ty, 445, 17, r=3, fill=True)

        # Dot
        pdf.set_fill(*t_col)
        pdf.circle(38, ty + 8, 2.5, fill=True)

        pdf.text(45, ty + 5, t_sym, font="F2", size=7, fill_rgb=(0.95, 0.98, 1))
        pdf.text(115, ty + 5, t_cls, font="F1", size=6.8, fill_rgb=(0.65, 0.72, 0.82))
        pdf.text(210, ty + 5, t_role, font="F1", size=6.8, fill_rgb=(0.75, 0.82, 0.90))
        pdf.text(360, ty + 5, t_note[:32], font="F2" if "REPLACES" in t_note or "NEW" in t_note else "F1", size=6.5, fill_rgb=(0.1, 0.9, 0.6) if "REPLACES" in t_note else (0.55, 0.62, 0.72))
        ty -= 20

    # Right Box 1: Crisis Stress Test Windows (X=501, Y=330, W=317, H=165)
    pdf.set_fill(0.071, 0.098, 0.153)
    pdf.set_stroke(0.180, 0.235, 0.314)
    pdf.set_line_width(1)
    pdf.rounded_rect(501, 330, 317, 165, r=8, fill=True, stroke=True)

    pdf.text(513, 477, "HISTORICAL CRISIS STRESS SCENARIOS", font="F2", size=10, fill_rgb=(0.96, 0.62, 0.04))
    pdf.text(513, 463, "Quantifying peak-to-trough drawdowns & multi-asset cushioning", font="F1", size=7.5, fill_rgb=(0.55, 0.62, 0.72))

    scenarios = [
        ("COVID-19 LIQUIDITY CRASH", "Feb 20, 2020 - Apr 15, 2020", "Nifty 50: -38.4% | GoldBees: +12.1%", "Validates Gold as an uncorrelated crisis anchor."),
        ("GLOBAL INFLATION & RATE HIKES", "Jan 03, 2022 - Oct 21, 2022", "US Tech: -33.1% | Nifty: -4.2% | USD/INR: +10.2%", "Proves currency depreciation buffers global tech ETF."),
        ("2024 ELECTION & BUDGET SHOCK", "Jun 03, 2024 - Jun 05, 2024", "Nifty 50: -5.9% single-day shock", "Tests rebalanced G-Sec & Gold stability cushion."),
    ]
    sy = 442
    for sc_title, sc_dates, sc_stats, sc_lesson in scenarios:
        pdf.set_fill(0.09, 0.12, 0.18)
        pdf.rounded_rect(511, sy - 20, 297, 33, r=4, fill=True)
        pdf.text(516, sy + 3, sc_title, font="F2", size=7.5, fill_rgb=(0.95, 0.98, 1))
        pdf.text(680, sy + 3, sc_dates, font="F1", size=6, fill_rgb=(0.5, 0.6, 0.7))
        pdf.text(516, sy - 6, sc_stats, font="F2", size=6.8, fill_rgb=(0.96, 0.62, 0.04))
        pdf.text(516, sy - 15, sc_lesson, font="F1", size=6.5, fill_rgb=(0.6, 0.7, 0.8))
        sy -= 42

    # Right Box 2: Time Series Econometric Toolkit (X=501, Y=145, W=317, H=173)
    pdf.set_fill(0.071, 0.098, 0.153)
    pdf.set_stroke(0.180, 0.235, 0.314)
    pdf.set_line_width(1)
    pdf.rounded_rect(501, 145, 317, 173, r=8, fill=True, stroke=True)

    pdf.text(513, 302, "TIME SERIES & RISK ECONOMETRICS", font="F2", size=10, fill_rgb=(0.24, 0.58, 0.98))
    pdf.text(513, 288, "Advanced statistical indicators integrated into the v2.0 engine", font="F1", size=7.5, fill_rgb=(0.55, 0.62, 0.72))

    metrics_list = [
        ("Rolling Sharpe & Sortino (252d)", "Detects risk-adjusted decay and regime change over time."),
        ("EWMA Dynamic Volatility", "Decay lambda=0.94 models volatility clustering (ARCH effect)."),
        ("Walk-Forward Rebalancing", "Tests if quarterly rebalancing generates positive rebalancing alpha."),
        ("Conditional VaR (CVaR 95%)", "Quantifies expected shortfall during the worst 5% tail events."),
        ("Maximum Drawdown Duration", "Measures recovery time in trading days from peak to new high."),
    ]
    my = 270
    for m_label, m_exp in metrics_list:
        pdf.set_fill(0.24, 0.58, 0.98)
        pdf.circle(518, my + 3, 2.5, fill=True)
        pdf.text(525, my + 2, m_label, font="F2", size=7.5, fill_rgb=(0.90, 0.95, 1))
        pdf.text(525, my - 7, m_exp, font="F1", size=6.5, fill_rgb=(0.55, 0.62, 0.72))
        my -= 23

    # Bottom Pipeline Ribbon (X=24, Y=26, W=794, H=105)
    pdf.set_fill(0.118, 0.161, 0.231)
    pdf.set_stroke(0.200, 0.255, 0.333)
    pdf.set_line_width(1)
    pdf.rounded_rect(24, 26, 794, 105, r=8, fill=True, stroke=True)

    pdf.text(36, 114, "END-TO-END QUANT PRODUCTION PIPELINE", font="F2", size=10, fill_rgb=(0.06, 0.72, 0.51))
    pdf.text(36, 101, "Modular, automated, zero-lookahead-bias architecture from NSE ingestion to serverless API", font="F1", size=7.5, fill_rgb=(0.55, 0.62, 0.72))

    pipe_steps = [
        ("1. INGEST & HEAL", "yfinance download\nSplit artifact healer\nTrading calendar align", 36),
        ("2. TIME SERIES ENGINE", "Rolling 252d metrics\nEWMA vol clustering\nDrawdown duration map", 192),
        ("3. MPT OPTIMIZER", "SLSQP constrained solver\nDirichlet 10k Monte Carlo\nMax Sharpe & Min Vol", 348),
        ("4. STRESS & BACKTEST", "Walk-forward rebalance\nCOVID / 2022 / 2024 shock\nCVaR & Tail risk metrics", 504),
        ("5. REST API & REPORT", "Vercel serverless Python\nInteractive Compare UI\nInstitutional 12-page PDF", 660),
    ]

    for p_title, p_lines, p_x in pipe_steps:
        pdf.set_fill(0.08, 0.11, 0.17)
        pdf.set_stroke(0.20, 0.26, 0.35)
        pdf.rounded_rect(p_x, 34, 145, 58, r=5, fill=True, stroke=True)

        pdf.text(p_x + 8, 77, p_title, font="F2", size=7.5, fill_rgb=(0.06, 0.72, 0.51))
        ly = 65
        for line in p_lines.split("\n"):
            pdf.text(p_x + 8, ly, line, font="F1", size=6.5, fill_rgb=(0.65, 0.72, 0.82))
            ly -= 9

    # Write PDF
    pdf_bytes = pdf.compile()
    with open(PDF_PATH, "wb") as f:
        f.write(pdf_bytes)
    print(f"Generated PDF: {PDF_PATH} ({len(pdf_bytes):,} bytes)")


def generate_html_companion():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Indian ETF Quant Engine v2.0 — Strategic Roadmap</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090e17;
      --card-bg: #111827;
      --card-border: #1f2937;
      --text: #f3f4f6;
      --muted: #9ca3af;
      --emerald: #10b981;
      --cyan: #0ea5e9;
      --amber: #f59e0b;
      --purple: #8b5cf6;
      --red: #ef4444;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background-color: var(--bg);
      color: var(--text);
      font-family: 'Plus Jakarta Sans', sans-serif;
      padding: 32px 24px;
      line-height: 1.5;
    }
    .container { max-width: 1200px; margin: 0 auto; }
    .header-card {
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      border: 1px solid #334155;
      border-radius: 16px;
      padding: 28px 32px;
      margin-bottom: 24px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .badges { display: flex; gap: 8px; margin-bottom: 12px; }
    .badge {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }
    .badge-cyan { background: rgba(14, 165, 233, 0.2); color: var(--cyan); border: 1px solid rgba(14, 165, 233, 0.4); }
    .badge-emerald { background: rgba(16, 185, 129, 0.2); color: var(--emerald); border: 1px solid rgba(16, 185, 129, 0.4); }
    h1 { font-size: 28px; font-weight: 800; color: #fff; margin-bottom: 6px; }
    .subtitle { color: var(--muted); font-size: 14px; }
    
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .kpi-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 16px 20px;
      border-left: 4px solid var(--emerald);
    }
    .kpi-card:nth-child(2) { border-left-color: var(--cyan); }
    .kpi-card:nth-child(3) { border-left-color: var(--amber); }
    .kpi-card:nth-child(4) { border-left-color: var(--purple); }
    .kpi-tag { font-size: 11px; font-weight: 600; color: var(--muted); text-transform: uppercase; margin-bottom: 4px; }
    .kpi-val { font-size: 20px; font-weight: 700; color: #fff; }
    .kpi-sub { font-size: 12px; color: #6b7280; margin-top: 2px; }

    .phases-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .phase-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    .phase-head {
      background: #1a2234;
      padding: 16px;
      border-bottom: 1px solid var(--card-border);
    }
    .phase-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    .phase-num {
      background: var(--emerald);
      color: #000;
      font-weight: 800;
      font-size: 12px;
      padding: 2px 8px;
      border-radius: 6px;
    }
    .phase-card:nth-child(2) .phase-num { background: var(--cyan); }
    .phase-card:nth-child(3) .phase-num { background: var(--amber); }
    .phase-card:nth-child(4) .phase-num { background: var(--purple); color: #fff; }
    .phase-pill { font-size: 11px; font-weight: 600; color: var(--muted); }
    .phase-title { font-size: 16px; font-weight: 700; color: #fff; }
    .phase-sub { font-size: 12px; color: var(--muted); }
    .phase-body { padding: 16px; flex-grow: 1; }
    .item-list { list-style: none; display: flex; flex-direction: column; gap: 12px; }
    .item-title { font-size: 13px; font-weight: 600; color: #e5e7eb; }
    .item-desc { font-size: 11px; color: var(--muted); margin-top: 2px; }
    .phase-foot {
      background: #0d131f;
      padding: 10px 16px;
      font-size: 11px;
      color: #6b7280;
      font-family: 'JetBrains Mono', monospace;
      border-top: 1px solid var(--card-border);
    }

    .table-card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 24px;
      margin-bottom: 24px;
    }
    .table-title { font-size: 18px; font-weight: 700; margin-bottom: 4px; color: var(--emerald); }
    .table-sub { font-size: 13px; color: var(--muted); margin-bottom: 16px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th { text-align: left; padding: 10px 12px; background: #1a2234; color: var(--muted); font-weight: 600; font-size: 11px; text-transform: uppercase; }
    td { padding: 12px; border-bottom: 1px solid var(--card-border); }
    tr:hover { background: rgba(255,255,255,0.02); }
    .badge-new { background: rgba(16, 185, 129, 0.15); color: var(--emerald); padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: 700; }
    .code { font-family: 'JetBrains Mono', monospace; font-weight: 600; color: #93c5fd; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header-card">
      <div class="badges">
        <span class="badge badge-cyan">Strategic Execution Roadmap</span>
        <span class="badge badge-emerald">Version 2.0</span>
      </div>
      <h1>Indian ETF Quantitative Engine & Time Series Platform</h1>
      <p class="subtitle">From Static Modern Portfolio Theory to Multi-Asset, Rolling Econometrics & Institutional Risk Management</p>
    </div>

    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-tag">Universe Expansion</div>
        <div class="kpi-val">8+ Curated ETFs</div>
        <div class="kpi-sub">Midcap, Nasdaq, Silver, G-Sec</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-tag">Time Series Modeling</div>
        <div class="kpi-val">Rolling Sharpe & Vol</div>
        <div class="kpi-sub">EWMA Volatility Clustering</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-tag">Stress Testing</div>
        <div class="kpi-val">3 Crisis Windows</div>
        <div class="kpi-sub">COVID, 2022 Hikes, 2024 Shock</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-tag">Architecture</div>
        <div class="kpi-val">100% Automated</div>
        <div class="kpi-sub">Vercel Serverless + PDF Engine</div>
      </div>
    </div>

    <div class="phases-grid">
      <div class="phase-card">
        <div class="phase-head">
          <div class="phase-top">
            <span class="phase-num">01</span>
            <span class="phase-pill">FOUNDATION</span>
          </div>
          <div class="phase-title">Multi-Asset Universe</div>
          <div class="phase-sub">Eliminate Redundancy & Add Alpha</div>
        </div>
        <div class="phase-body">
          <ul class="item-list">
            <li>
              <div class="item-title">Add MID150BEES</div>
              <div class="item-desc">Captures high-growth Indian midcap alpha beyond large-caps.</div>
            </li>
            <li>
              <div class="item-title">Add MON100 (Nasdaq)</div>
              <div class="item-desc">Global tech exposure + natural USD currency depreciation hedge.</div>
            </li>
            <li>
              <div class="item-title">Add SILVERBEES</div>
              <div class="item-desc">Dual commodity hedge alongside Gold; industrial demand beta.</div>
            </li>
            <li>
              <div class="item-title">Add GSEC10IETF</div>
              <div class="item-desc">10-Yr Sovereign G-Sec; real bond yield vs low-return LiquidBees.</div>
            </li>
          </ul>
        </div>
        <div class="phase-foot">Tech: yfinance, pandas, split-healer</div>
      </div>

      <div class="phase-card">
        <div class="phase-head">
          <div class="phase-top">
            <span class="phase-num">02</span>
            <span class="phase-pill">ECONOMETRICS</span>
          </div>
          <div class="phase-title">Time Series Modeling</div>
          <div class="phase-sub">Dynamic Risk & Regime Shifts</div>
        </div>
        <div class="phase-body">
          <ul class="item-list">
            <li>
              <div class="item-title">Rolling Sharpe & Sortino</div>
              <div class="item-desc">180d & 365d rolling windows reveal regime-dependent decay.</div>
            </li>
            <li>
              <div class="item-title">Rolling Volatility Curve</div>
              <div class="item-desc">Visualizes volatility divergence between equities & gold.</div>
            </li>
            <li>
              <div class="item-title">EWMA Volatility Clustering</div>
              <div class="item-desc">RiskMetrics decay (lambda=0.94) tracks dynamic variance shocks.</div>
            </li>
            <li>
              <div class="item-title">Dynamic Beta Tracking</div>
              <div class="item-desc">Measures shifting correlation of Midcap & Bank vs Nifty 50.</div>
            </li>
          </ul>
        </div>
        <div class="phase-foot">Tech: scipy.stats, numpy, EWMA engine</div>
      </div>

      <div class="phase-card">
        <div class="phase-head">
          <div class="phase-top">
            <span class="phase-num">03</span>
            <span class="phase-pill">VALIDATION</span>
          </div>
          <div class="phase-title">Backtests & Stress Tests</div>
          <div class="phase-sub">Real-World Performance Proof</div>
        </div>
        <div class="phase-body">
          <ul class="item-list">
            <li>
              <div class="item-title">Walk-Forward Rebalancing</div>
              <div class="item-desc">Quarterly & annual rebalancing vs static buy-and-hold.</div>
            </li>
            <li>
              <div class="item-title">COVID-19 Crash Test</div>
              <div class="item-desc">Stress testing drawdown & recovery during Feb-Apr 2020.</div>
            </li>
            <li>
              <div class="item-title">2022 Inflation Shock</div>
              <div class="item-desc">Performance through RBI/Fed rate hikes & tech correction.</div>
            </li>
            <li>
              <div class="item-title">Tail Risk & CVaR (95%)</div>
              <div class="item-desc">Quantifies conditional value at risk during the worst 5% days.</div>
            </li>
          </ul>
        </div>
        <div class="phase-foot">Tech: SLSQP, Dirichlet Monte Carlo</div>
      </div>

      <div class="phase-card">
        <div class="phase-head">
          <div class="phase-top">
            <span class="phase-num">04</span>
            <span class="phase-pill">DEPLOYMENT</span>
          </div>
          <div class="phase-title">Web Simulator & Reports</div>
          <div class="phase-sub">Interactive Tool & PDF Export</div>
        </div>
        <div class="phase-body">
          <ul class="item-list">
            <li>
              <div class="item-title">Custom Preset Baskets</div>
              <div class="item-desc">Toggle Classic 5, All-Weather 7, or Pure Equity Alpha.</div>
            </li>
            <li>
              <div class="item-title">Head-to-Head Compare UI</div>
              <div class="item-desc">Side-by-side radar metrics comparing any two ETFs directly.</div>
            </li>
            <li>
              <div class="item-title">Interactive Stress Simulator</div>
              <div class="item-desc">Sliders to test portfolio survival in a 20% equity crash.</div>
            </li>
            <li>
              <div class="item-title">Institutional 12-Page PDF</div>
              <div class="item-desc">Auto-compiled executive brief with clean print typography.</div>
            </li>
          </ul>
        </div>
        <div class="phase-foot">Tech: Vanilla JS, Chart.js, Vercel Serverless</div>
      </div>
    </div>

    <div class="table-card">
      <div class="table-title">ETF Basket Upgrade: v1.0 (Classic) vs v2.0 (All-Weather)</div>
      <div class="table-sub">Strategic shift from bank-heavy equity to true non-correlated multi-asset allocation</div>
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Asset Class</th>
            <th>Role in Portfolio</th>
            <th>v1.0 Issue / v2.0 Benefit</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="code">NIFTYBEES.NS</td>
            <td>Large-Cap Equity</td>
            <td>Core India Growth Anchor</td>
            <td>Baseline market return; high liquidity</td>
          </tr>
          <tr>
            <td class="code">JUNIORBEES.NS</td>
            <td>Large/Mid Next 50</td>
            <td>Growth & Beta Booster</td>
            <td>Higher CAGR; complements Nifty 50</td>
          </tr>
          <tr>
            <td class="code">BANKBEES.NS</td>
            <td>Banking Sector</td>
            <td>Financial Sector Alpha</td>
            <td><span style="color:#ef4444">OVERLAPS: 82% corr with Nifty; 0% weight</span></td>
          </tr>
          <tr>
            <td class="code">MID150BEES.NS <span class="badge-new">NEW</span></td>
            <td>Mid-Cap 150</td>
            <td>Alpha & Factor Premium</td>
            <td><strong style="color:#10b981">REPLACES BANK: Real midcap diversification</strong></td>
          </tr>
          <tr>
            <td class="code">MON100.NS <span class="badge-new">NEW</span></td>
            <td>US Nasdaq 100</td>
            <td>Global Tech + Currency Hedge</td>
            <td><strong style="color:#10b981">PROTECTS INR: Low correlation to Nifty</strong></td>
          </tr>
          <tr>
            <td class="code">GOLDBEES.NS</td>
            <td>Precious Metal</td>
            <td>Crisis Ballast & Safe Haven</td>
            <td>Zero correlation to stocks; proven hedge</td>
          </tr>
          <tr>
            <td class="code">SILVERBEES.NS <span class="badge-new">NEW</span></td>
            <td>Precious Metal</td>
            <td>Industrial Commodity Beta</td>
            <td>High volatility commodity upside kicker</td>
          </tr>
          <tr>
            <td class="code">GSEC10IETF.NS <span class="badge-new">NEW</span></td>
            <td>10-Yr Sovereign Bond</td>
            <td>Long-Duration Bond Yield</td>
            <td><strong style="color:#10b981">REPLACES LIQUID: 7.0% yield + capital gain</strong></td>
          </tr>
          <tr>
            <td class="code">LIQUIDBEES.NS</td>
            <td>Cash Equivalent</td>
            <td>Dry Powder & Rebalance Pool</td>
            <td>Zero vol, but acts as a long-term return drag</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated HTML: {HTML_PATH}")


if __name__ == "__main__":
    generate_roadmap()
    generate_html_companion()
