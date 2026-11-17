#!/usr/bin/env python3
"""
generate_scaling_roadmap_pdf.py

Generates a clean, executive-level PDF report summarizing:
1. Publishing on Vercel & Supabase PostgreSQL Cloud Architecture
2. Relational Database Schema & Row-Level Security
3. Step-by-Step Execution Roadmap to Scale Up ETF Optima
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages

def create_scaling_pdf(output_path="docs/ETF_Optima_Scaling_Architecture_Roadmap.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with PdfPages(output_path) as pdf:
        # =====================================================================
        # PAGE 1: System Overview & Vercel Publishing Architecture
        # =====================================================================
        fig1, ax1 = plt.subplots(figsize=(11, 8.5))
        ax1.set_xlim(0, 100)
        ax1.set_ylim(0, 100)
        ax1.axis('off')
        
        # Header Bar
        header_box = mpatches.FancyBboxPatch((4, 88), 92, 9, boxstyle="round,pad=0.5",
                                             facecolor='#0F172A', edgecolor='none')
        ax1.add_patch(header_box)
        ax1.text(50, 93.5, "ETF Optima — Scaling Architecture & Cloud Roadmap",
                 ha='center', va='center', fontsize=18, fontweight='bold', color='#38BDF8')
        ax1.text(50, 90, "Vercel Serverless + Supabase PostgreSQL Cloud Deployment",
                 ha='center', va='center', fontsize=11, color='#94A3B8')

        # Section 1: Where will it publish on Vercel?
        ax1.text(5, 84, "1. Where and How It Publishes on Vercel", fontsize=13, fontweight='bold', color='#0F172A')
        
        info_text = (
            "• Web Dashboard & API: Deployed directly to Vercel (https://web-six-zeta-72.vercel.app).\n"
            "• Zero Server Maintenance: Frontend static assets are distributed via Vercel Global Edge CDN.\n"
            "• Python Serverless Functions: Compute endpoints (/api/generate, /api/excel, /api/optimize) run on-demand.\n"
            "• Database Connection: Connects to Supabase Cloud PostgreSQL via connection pooling (PgBouncer) over HTTPS/TCP."
        )
        ax1.text(6, 75, info_text, fontsize=9.5, color='#334155', linespacing=1.6)

        # Architecture Flow Diagram
        ax1.text(5, 68, "2. End-to-End Scaled Cloud Data Flow", fontsize=13, fontweight='bold', color='#0F172A')
        
        # Draw Box helper
        def draw_card(ax, x, y, w, h, title, subtitle, bg='#1E293B', border='#38BDF8'):
            box = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3",
                                          facecolor=bg, edgecolor=border, lw=1.5)
            ax.add_patch(box)
            ax.text(x + w/2, y + h*0.65, title, ha='center', va='center',
                    fontsize=10.5, fontweight='bold', color='white')
            ax.text(x + w/2, y + h*0.3, subtitle, ha='center', va='center',
                    fontsize=8, color='#94A3B8')

        # 3 Tier Cards
        draw_card(ax1, 6, 52, 26, 12, "Client Browser UI", "Vite Glassmorphism + Supabase JS", bg='#1E293B', border='#38BDF8')
        draw_card(ax1, 37, 52, 26, 12, "Vercel Serverless", "Python 3.11 + SciPy + Matplotlib", bg='#0F172A', border='#10B981')
        draw_card(ax1, 68, 52, 26, 12, "Cloud PostgreSQL", "Supabase AWS ap-south-1 (Mumbai)", bg='#1E1B4B', border='#8B5CF6')

        # Arrows
        ax1.annotate("", xy=(36, 58), xytext=(33, 58), arrowprops=dict(arrowstyle="->", color="#0284C7", lw=2))
        ax1.text(34.5, 60, "REST / API", ha='center', fontsize=7.5, color='#0284C7', fontweight='bold')

        ax1.annotate("", xy=(67, 58), xytext=(64, 58), arrowprops=dict(arrowstyle="->", color="#10B981", lw=2))
        ax1.text(65.5, 60, "Pooled SQL", ha='center', fontsize=7.5, color='#10B981', fontweight='bold')

        # Section 3: Why PostgreSQL vs Others
        ax1.text(5, 45, "3. Why PostgreSQL Wins (Institutional Quant Standard)", fontsize=13, fontweight='bold', color='#0F172A')
        
        comp_headers = ["Feature", "MongoDB (NoSQL)", "MySQL / MariaDB", "PostgreSQL (Chosen)"]
        comp_rows = [
            ["Financial Data Modeling", "Loose JSON docs, no joins", "Basic relational tables", "Advanced Relational (Industry Standard)"],
            ["Row-Level Security (RLS)", "None (App code only)", "None (App code only)", "Native Engine-Level Multi-Tenant RLS"],
            ["Math & Simulation Storage", "Raw BSON blobs", "Unparsed text strings", "True Binary JSONB + Window Functions"],
            ["Serverless Compatibility", "Requires persistent sockets", "Connection exhaustion crashes", "Stateless HTTP & PgBouncer pooling"]
        ]
        
        table = ax1.table(cellText=comp_rows, colLabels=comp_headers, loc='center',
                          bbox=[0.05, 0.16, 0.9, 0.24])
        table.auto_set_font_size(False)
        table.set_fontsize(8.5)
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_facecolor('#0F172A')
                cell.set_text_props(color='white', fontweight='bold')
            elif col == 3:
                cell.set_facecolor('#ECFDF5')
                cell.set_text_props(color='#065F46', fontweight='bold')
            else:
                cell.set_facecolor('#F8FAFC')
            cell.set_edgecolor('#CBD5E1')

        # Footer
        ax1.text(50, 6, "ETF Optima Architectural Documentation • Page 1 of 2",
                 ha='center', fontsize=8.5, color='#64748B')
        pdf.savefig(fig1, bbox_inches='tight')
        plt.close(fig1)

        # =====================================================================
        # PAGE 2: Schema Blueprint & Step-by-Step Scaling Roadmap
        # =====================================================================
        fig2, ax2 = plt.subplots(figsize=(11, 8.5))
        ax2.set_xlim(0, 100)
        ax2.set_ylim(0, 100)
        ax2.axis('off')

        # Header Bar
        header_box2 = mpatches.FancyBboxPatch((4, 88), 92, 9, boxstyle="round,pad=0.5",
                                              facecolor='#0F172A', edgecolor='none')
        ax2.add_patch(header_box2)
        ax2.text(50, 93.5, "PostgreSQL Schema & Step-by-Step Execution Roadmap",
                 ha='center', va='center', fontsize=18, fontweight='bold', color='#38BDF8')
        ax2.text(50, 90, "Production Execution Steps from Guest Sandbox to Cloud Storage",
                 ha='center', va='center', fontsize=11, color='#94A3B8')

        # Section 4: Relational Schema Structure
        ax2.text(5, 84, "4. Production Database Schema (PostgreSQL DDL)", fontsize=13, fontweight='bold', color='#0F172A')

        schema_text = (
            "• profiles: Links to auth.users (id, email, full_name, created_at).\n"
            "• etf_universe: Catalog of 15+ ETFs (ticker, name, asset_class, expense_ratio, is_active).\n"
            "• portfolios: User-saved models (id, user_id, name, strategy, investment_amount).\n"
            "• portfolio_holdings: Assets per portfolio (portfolio_id, ticker, weight numeric(5,4)).\n"
            "   → Enforces: CONSTRAINT check_weight CHECK (weight >= 0.0 AND weight <= 1.0).\n"
            "• backtest_runs: Optimization logs (portfolio_id, expected_return, volatility, sharpe, cvar_95, metrics_meta JSONB)."
        )
        ax2.text(6, 73, schema_text, fontsize=9, color='#334155', linespacing=1.5)

        # Section 5: The 4-Phase Scale-Up Roadmap
        ax2.text(5, 64, "5. The 4-Phase Scale-Up Implementation Roadmap", fontsize=13, fontweight='bold', color='#0F172A')

        def draw_phase(ax, x, y, w, h, phase_num, title, items, color_border):
            box = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3",
                                          facecolor='#F8FAFC', edgecolor=color_border, lw=1.8)
            ax.add_patch(box)
            ax.text(x + 2, y + h - 3, f"Phase {phase_num}: {title}", fontsize=10, fontweight='bold', color='#0F172A')
            lines = "\n".join([f"• {item}" for item in items])
            ax.text(x + 2, y + 2, lines, fontsize=8, color='#475569', linespacing=1.4)

        draw_phase(ax2, 5, 43, 43, 18, "1", "Cloud Database Provisioning",
                   ["Create free Supabase project (Mumbai region)",
                    "Run DDL schema script (tables & foreign keys)",
                    "Activate Row-Level Security (RLS) policies",
                    "Populate 15+ Indian & Global ETF catalog"],
                   '#38BDF8')

        draw_phase(ax2, 52, 43, 43, 18, "2", "Frontend Auth & Universe Builder",
                   ["Add glassmorphism Auth modal (Google + Email)",
                    "Connect @supabase/supabase-js in web/main.js",
                    "Build dynamic ETF selector & weight sliders",
                    "Preserve Guest Mode (test without signup)"],
                   '#10B981')

        draw_phase(ax2, 5, 21, 43, 18, "3", "Serverless API & MPT Engine Upgrade",
                   ["Upgrade /api/generate & /api/excel for dynamic tickers",
                    "Connect Python serverless to Supabase via pooled URL",
                    "Execute SciPy SLSQP optimization for custom baskets",
                    "Log backtest metrics & simulation to PostgreSQL"],
                   '#8B5CF6')

        draw_phase(ax2, 52, 21, 43, 18, "4", "Vercel Production Deployment & CI/CD",
                   ["Set Vercel environment variables (SUPABASE_URL, ANON_KEY)",
                    "Verify sub-second response times across Mumbai region",
                    "Run automated Pytest unit tests in GitHub Actions",
                    "Update live README with database architecture badges"],
                   '#F59E0B')

        # Callout Box
        callout = mpatches.FancyBboxPatch((5, 9), 90, 8, boxstyle="round,pad=0.3",
                                          facecolor='#ECFDF5', edgecolor='#10B981', lw=1.5)
        ax2.add_patch(callout)
        ax2.text(50, 14, "Key Recruiter Advantage: Guest Sandbox + Cloud PostgreSQL Persistence",
                 ha='center', fontsize=10.5, fontweight='bold', color='#065F46')
        ax2.text(50, 11, "Recruiters test instantly in 5 seconds. Cloud saves prove enterprise SQL and quantitative data engineering.",
                 ha='center', fontsize=8.5, color='#047857')

        # Footer
        ax2.text(50, 4, "ETF Optima Architectural Documentation • Page 2 of 2",
                 ha='center', fontsize=8.5, color='#64748B')
        pdf.savefig(fig2, bbox_inches='tight')
        plt.close(fig2)

    print(f"Successfully generated: {output_path}")

if __name__ == "__main__":
    create_scaling_pdf()
