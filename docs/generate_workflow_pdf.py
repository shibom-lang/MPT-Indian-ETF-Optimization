import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import textwrap

def draw_box(ax, x, y, width, height, text, bg_color='#1E293B', text_color='white', fontsize=10):
    box = mpatches.FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02,rounding_size=0.02",
                                  edgecolor='none', facecolor=bg_color, zorder=2)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text, ha='center', va='center',
            color=text_color, fontsize=fontsize, fontweight='bold', zorder=3,
            wrap=True)
    return x + width/2, y

def draw_arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color="#94A3B8", lw=2), zorder=1)

def create_workflow_pdf():
    pdf_path = "Project_Workflow_Architecture.pdf"
    with PdfPages(pdf_path) as pdf:
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis('off')
        
        # Title
        ax.text(50, 95, "ETF Portfolio Robo-Advisor - System Workflow",
                ha='center', va='center', fontsize=20, fontweight='bold', color='#0F172A')
        ax.text(50, 92, "High-Level Technical Architecture & Data Flow",
                ha='center', va='center', fontsize=12, color='#475569')

        # Colors
        c_front = '#3B82F6'  # Blue
        c_api = '#10B981'    # Green
        c_engine = '#8B5CF6' # Purple
        c_data = '#F59E0B'   # Orange
        c_out = '#EF4444'    # Red
        
        # 1. Frontend
        ax.text(20, 85, "1. Frontend UI", fontsize=14, fontweight='bold', ha='center', color=c_front)
        draw_box(ax, 5, 75, 30, 8, "User enters Investment Amount\n& selects Strategy", c_front)
        
        # 2. Vercel API
        ax.text(50, 85, "2. API Gateway (Vercel)", fontsize=14, fontweight='bold', ha='center', color=c_api)
        draw_box(ax, 38, 75, 24, 8, "GET /api/generate (PDF)\nGET /api/excel (XLSX)", c_api)
        
        # 3. Data Fetching
        ax.text(80, 85, "3. Data Layer", fontsize=14, fontweight='bold', ha='center', color=c_data)
        draw_box(ax, 65, 75, 30, 8, "yfinance API\nFetches 5Y Live ETF Data", c_data)
        
        draw_arrow(ax, 35, 79, 38, 79)
        draw_arrow(ax, 62, 79, 65, 79)
        draw_arrow(ax, 65, 77, 62, 77)

        # 4. Quant Engine
        ax.text(50, 65, "4. Quant Engine (SciPy)", fontsize=14, fontweight='bold', ha='center', color=c_engine)
        draw_box(ax, 20, 52, 60, 10, 
                 "Covariance Matrix & Log Returns Calculation\n"
                 "⬇\n"
                 "SciPy SLSQP Optimization (Maximize Sharpe / Min Volatility)\n"
                 "⬇\n"
                 "Apply constraints: Sum=100%, Max Weight=45%", c_engine, fontsize=11)
        
        draw_arrow(ax, 50, 75, 50, 62)

        # 5. Report Generators
        ax.text(50, 45, "5. Output Generators", fontsize=14, fontweight='bold', ha='center', color=c_out)
        
        draw_box(ax, 15, 32, 30, 10, "Matplotlib Engine\nDraws: Efficient Frontier,\nHeatmap, Underwater Chart", '#334155')
        draw_box(ax, 55, 32, 30, 10, "OpenPyxl Engine\nBuilds: Beta Calculator,\n10Y Projections", '#334155')
        
        draw_arrow(ax, 35, 52, 30, 42)
        draw_arrow(ax, 65, 52, 70, 42)
        
        # 6. Final Delivery
        draw_box(ax, 15, 15, 30, 8, "10-Page PDF Report\nStreamed to Client", c_out)
        draw_box(ax, 55, 15, 30, 8, "Excel Financial Model (.xlsx)\nStreamed to Client", c_out)
        
        draw_arrow(ax, 30, 32, 30, 23)
        draw_arrow(ax, 70, 32, 70, 23)

        pdf.savefig(fig)
        plt.close()
        
    print(f"Generated {pdf_path}")

if __name__ == "__main__":
    create_workflow_pdf()
