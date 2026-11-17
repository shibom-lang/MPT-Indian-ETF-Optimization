#!/usr/bin/env python3
"""
build_clean_pdf.py

Builds a clean, publication-grade, multi-page PDF document using ReportLab.
Uses automated document flow so elements NEVER overlap or collide.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Adds clean header rule and page numbers (e.g. Page 1 of 3)"""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "ETF Optima — Scaling Architecture & Database Manual")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer (all pages)
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, footer_text)
        self.drawString(54, 36, "Confidential • Architectural Roadmap for Engineering & Portfolio Review")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, 558, 46)
        self.restoreState()

def build_pdf(output_path="docs/ETF_Optima_Scaling_Architecture_Roadmap.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Clean Styles
    primary_color = colors.HexColor("#0F172A")
    accent_blue = colors.HexColor("#0284C7")
    text_dark = colors.HexColor("#1E293B")
    text_muted = colors.HexColor("#475569")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=accent_blue,
        spaceAfter=14
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=text_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=text_dark,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=text_dark
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white
    )

    story = []

    # Title & Header
    story.append(Paragraph("ETF Optima — Scaling Architecture & Database Manual", title_style))
    story.append(Paragraph("Cloud PostgreSQL, User Accounts & Multi-ETF Quantitative Analytics on Vercel", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceAfter=14))

    # Section 1: Where will it publish on Vercel?
    story.append(Paragraph("1. Where and How It Publishes on Vercel", h1_style))
    story.append(Paragraph(
        "The scaled platform will remain published on your existing live production domain: "
        "<b>https://web-six-zeta-72.vercel.app</b>. The system operates as a modern 3-tier cloud architecture:",
        body_style
    ))
    story.append(Paragraph("• <b>Frontend Layer (Vercel CDN):</b> Static Vite assets (HTML, CSS, JavaScript) deployed across Vercel Global Edge Network for sub-50ms load times worldwide.", bullet_style))
    story.append(Paragraph("• <b>Compute Layer (Vercel Serverless Functions):</b> On-demand Python endpoints (<code>/api/optimize</code>, <code>/api/generate</code>, <code>/api/excel</code>) execute MPT mathematics and stream reports without running 24/7 idle servers.", bullet_style))
    story.append(Paragraph("• <b>Database & Auth Layer (Supabase Cloud PostgreSQL):</b> Managed relational database in the AWS Mumbai region (<code>ap-south-1</code>) connected securely via connection pooling.", bullet_style))
    story.append(Spacer(1, 8))

    # Architecture Table / Box
    arch_data = [
        [
            Paragraph("<b>Client Browser UI</b><br/><font color='#64748B'>Vite + Glassmorphism<br/>Supabase JS SDK (Auth & Sync)</font>", table_cell_style),
            Paragraph("<b>Vercel Serverless API</b><br/><font color='#64748B'>Python 3.11 Runtime<br/>SciPy MPT & Matplotlib</font>", table_cell_style),
            Paragraph("<b>Cloud PostgreSQL</b><br/><font color='#64748B'>Supabase (Mumbai ap-south-1)<br/>Row-Level Security (RLS)</font>", table_cell_style)
        ]
    ]
    t_arch = Table(arch_data, colWidths=[168, 168, 168])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 14))

    # Section 2: Why PostgreSQL
    story.append(Paragraph("2. Database Technology Evaluation: Why PostgreSQL Wins", h1_style))
    story.append(Paragraph(
        "In institutional finance, data consistency and analytical capabilities are paramount. "
        "Here is why PostgreSQL was selected over MongoDB, MySQL, and MariaDB:",
        body_style
    ))

    db_comp_data = [
        [
            Paragraph("Database", table_header_style),
            Paragraph("Data Modeling", table_header_style),
            Paragraph("Multi-Tenant Security", table_header_style),
            Paragraph("Serverless / Vercel Fit", table_header_style),
            Paragraph("Verdict", table_header_style)
        ],
        [
            Paragraph("<b>PostgreSQL</b><br/>(Chosen)", table_cell_style),
            Paragraph("Strict relational SQL, foreign keys, mathematical CHECK constraints, binary JSONB.", table_cell_style),
            Paragraph("<b>Native Row-Level Security (RLS)</b> enforced directly at engine level.", table_cell_style),
            Paragraph("PgBouncer connection pooling and HTTPS REST prevents socket exhaustion.", table_cell_style),
            Paragraph("<font color='#059669'><b>Institutional Standard</b></font>", table_cell_style)
        ],
        [
            Paragraph("<b>MongoDB</b>", table_cell_style),
            Paragraph("Loose JSON documents; lacks cross-table relational integrity.", table_cell_style),
            Paragraph("Application-level checks only; prone to authorization bugs.", table_cell_style),
            Paragraph("Requires persistent connections; heavy for serverless micro-containers.", table_cell_style),
            Paragraph("<font color='#DC2626'><b>Unsuitable for Ledger</b></font>", table_cell_style)
        ],
        [
            Paragraph("<b>MySQL / MariaDB</b>", table_cell_style),
            Paragraph("Basic relational SQL; weak JSON support (stored as unindexed text).", table_cell_style),
            Paragraph("No native Row-Level Security; requires manual WHERE clauses in every query.", table_cell_style),
            Paragraph("Spikes in serverless traffic crash connection limits (max_connections).", table_cell_style),
            Paragraph("<font color='#D97706'><b>Legacy Web CRUD</b></font>", table_cell_style)
        ]
    ]
    t_comp = Table(db_comp_data, colWidths=[70, 120, 115, 115, 84])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 14))

    # Section 3: Relational Schema
    story.append(Paragraph("3. Production Relational Schema (PostgreSQL DDL)", h1_style))
    story.append(Paragraph(
        "The schema strictly models users, assets, portfolios, holdings, and risk-backtesting logs:",
        body_style
    ))

    schema_rows = [
        [
            Paragraph("Table Name", table_header_style),
            Paragraph("Primary Columns & Types", table_header_style),
            Paragraph("Integrity & Constraints", table_header_style)
        ],
        [
            Paragraph("<b>profiles</b>", table_cell_style),
            Paragraph("<code>id (UUID PK)</code>, <code>email (TEXT)</code>, <code>full_name (TEXT)</code>, <code>created_at</code>", table_cell_style),
            Paragraph("References <code>auth.users(id) ON DELETE CASCADE</code>.", table_cell_style)
        ],
        [
            Paragraph("<b>etf_universe</b>", table_cell_style),
            Paragraph("<code>ticker (TEXT PK)</code>, <code>name (TEXT)</code>, <code>asset_class (TEXT)</code>, <code>expense_ratio</code>", table_cell_style),
            Paragraph("Curated master list of 15+ Indian & Global ETFs (all NSE INR-denominated).", table_cell_style)
        ],
        [
            Paragraph("<b>portfolios</b>", table_cell_style),
            Paragraph("<code>id (UUID PK)</code>, <code>user_id (UUID FK)</code>, <code>name (TEXT)</code>, <code>strategy (TEXT)</code>", table_cell_style),
            Paragraph("Protected by Row-Level Security (RLS) so users only see their own portfolios.", table_cell_style)
        ],
        [
            Paragraph("<b>portfolio_holdings</b>", table_cell_style),
            Paragraph("<code>id (UUID PK)</code>, <code>portfolio_id (UUID FK)</code>, <code>ticker (TEXT FK)</code>, <code>weight (NUMERIC)</code>", table_cell_style),
            Paragraph("<b>Mathematical Constraint:</b><br/><code>CHECK (weight >= 0.0 AND weight <= 1.0)</code>", table_cell_style)
        ],
        [
            Paragraph("<b>backtest_runs</b>", table_cell_style),
            Paragraph("<code>id (UUID PK)</code>, <code>portfolio_id (UUID FK)</code>, <code>expected_return</code>, <code>volatility</code>, <code>sharpe_ratio</code>, <code>cvar_95</code>, <code>metrics_meta (JSONB)</code>", table_cell_style),
            Paragraph("Stores analytical run snapshots; JSONB field holds simulation distribution.", table_cell_style)
        ]
    ]
    t_schema = Table(schema_rows, colWidths=[100, 214, 190])
    t_schema.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_schema)
    story.append(Spacer(1, 14))

    # Section 4: Execution Roadmap
    story.append(Paragraph("4. Step-by-Step Scale-Up Execution Roadmap", h1_style))
    
    phases = [
        ("Phase 1: Database & Cloud Provisioning",
         "Create a free Supabase PostgreSQL project in AWS Mumbai (ap-south-1). Run the SQL migration script defining tables, foreign keys, check constraints, and Row-Level Security (RLS) policies. Seed the etf_universe table with 15+ NSE tickers."),
        ("Phase 2: Frontend Auth Modal & Custom ETF Universe Selector",
         "Implement clean glassmorphism Login/Signup modal (1-click Google + Email). Integrate @supabase/supabase-js in web/main.js. Build an interactive multi-ETF picker with allocation sliders, keeping the Guest Sandbox active for zero friction."),
        ("Phase 3: Serverless Python Optimization Upgrade",
         "Create the dedicated POST /api/optimize serverless endpoint. Update /api/generate (PDF) and /api/excel (XLSX) to accept dynamic ticker arrays. Pass payload directly from client to keep serverless functions fast, stateless, and 100% crash-proof."),
        ("Phase 4: Vercel Production Deployment & Verification",
         "Add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to Vercel Project Settings. Trigger automatic Git CI/CD build. Verify live guest optimization and authenticated cloud portfolio saving across mobile and desktop.")
    ]

    for p_title, p_desc in phases:
        story.append(Paragraph(f"<b>{p_title}</b>", body_style))
        story.append(Paragraph(p_desc, bullet_style))
        story.append(Spacer(1, 3))

    story.append(Spacer(1, 8))
    
    # Recruiter Advantage Callout Box
    callout_data = [
        [
            Paragraph(
                "<b>Key Hiring Advantage:</b> Visitors test custom portfolios in 5 seconds without signing up (zero bounce rate). "
                "Recruiters inspecting the codebase see production-grade PostgreSQL schemas, database-level security policies (RLS), "
                "and an institutional quantitative optimization pipeline.",
                ParagraphStyle('Callout', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor("#065F46"))
            )
        ]
    ]
    t_callout = Table(callout_data, colWidths=[504])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#ECFDF5")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#10B981")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(KeepTogether(t_callout))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated clean PDF: {output_path}")

if __name__ == "__main__":
    build_pdf()
