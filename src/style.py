"""Shared look and feel: page CSS, chart template, tables, and reusable HTML pieces."""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

ACCENT = "#22D3EE"
ACCENT_2 = "#818CF8"
WARN = "#FBBF24"
DANGER = "#F87171"
TEXT = "#E6EDF7"
MUTED = "#8FA3BF"
GRID = "rgba(148, 163, 184, 0.12)"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
.block-container {padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1400px;}
.stApp {background: radial-gradient(1200px 600px at 10% -10%, rgba(34,211,238,0.10), transparent 60%), radial-gradient(900px 500px at 100% 0%, rgba(129,140,248,0.10), transparent 55%), #0B1220;}
.voi-hero {font-family: 'Inter', sans-serif; margin-bottom: 1.4rem;}
.voi-eyebrow {color: #22D3EE; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase;}
.voi-title {font-size: 2.4rem; font-weight: 800; line-height: 1.15; margin: 0.25rem 0 0.35rem; background: linear-gradient(90deg, #F8FAFC 0%, #A5F3FC 60%, #818CF8 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;}
.voi-sub {color: #8FA3BF; font-size: 0.95rem;}
.kpi-card {font-family: 'Inter', sans-serif; background: linear-gradient(145deg, rgba(23,34,58,0.95), rgba(13,21,38,0.95)); border: 1px solid rgba(148,163,184,0.14); border-radius: 18px; padding: 18px 20px 16px; margin-bottom: 14px; box-shadow: 0 14px 34px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.06); transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease; position: relative; overflow: hidden;}
.kpi-card::before {content: ""; position: absolute; left: 0; top: 0; height: 3px; width: 100%; background: linear-gradient(90deg, #22D3EE, #818CF8);}
.kpi-card:hover {transform: translateY(-4px); border-color: rgba(34,211,238,0.45); box-shadow: 0 22px 44px rgba(0,0,0,0.55), 0 0 24px rgba(34,211,238,0.12);}
.kpi-label {color: #8FA3BF; font-size: 0.74rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase;}
.kpi-value {color: #F8FAFC; font-size: 1.95rem; font-weight: 700; margin-top: 6px; letter-spacing: -0.02em;}
.kpi-sub {color: #22D3EE; font-size: 0.8rem; margin-top: 4px;}
.section-title, .chart-title {font-family: 'Inter', sans-serif; color: #F1F5F9; font-weight: 700;}
.section-title {font-size: 1.35rem; margin: 1.6rem 0 0.8rem;}
.chart-title {font-size: 1.02rem; margin: 2px 0 6px;}
.insight {font-family: 'Inter', sans-serif; background: linear-gradient(90deg, rgba(34,211,238,0.09), rgba(34,211,238,0.02)); border: 1px solid rgba(34,211,238,0.18); border-left: 3px solid #22D3EE; border-radius: 12px; padding: 12px 16px; color: #CBD5E1; font-size: 0.9rem; line-height: 1.55; margin: 6px 0 10px;}
.insight b {color: #F8FAFC;}
.insight-tag {display: block; color: #22D3EE; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 4px;}
[class*="st-key-card"] {background: linear-gradient(145deg, rgba(20,30,52,0.88), rgba(12,19,35,0.88)); border-radius: 18px !important; border: 1px solid rgba(148,163,184,0.14) !important; box-shadow: 0 16px 38px rgba(0,0,0,0.42), inset 0 1px 0 rgba(255,255,255,0.05); padding: 6px 4px;}
[data-testid="stDataFrame"] {border: 1px solid rgba(148,163,184,0.18); border-radius: 12px; overflow: hidden; box-shadow: 0 8px 22px rgba(0,0,0,0.30);}
[data-testid="stMarkdownContainer"] table {width: 100%; border-collapse: collapse; font-size: 0.88rem;}
[data-testid="stMarkdownContainer"] th {background: rgba(34,211,238,0.10); color: #F1F5F9; text-align: left; padding: 9px 10px;}
[data-testid="stMarkdownContainer"] td {padding: 8px 10px; border-top: 1px solid rgba(148,163,184,0.14); vertical-align: top; color: #CBD5E1;}
section[data-testid="stSidebar"] {border-right: 1px solid rgba(148,163,184,0.12);}
</style>
"""


def apply_style():
    """Load the page CSS and set the default chart style. Called once in app.py."""
    st.markdown(CSS, unsafe_allow_html=True)
    axis = dict(gridcolor=GRID, zeroline=False, linecolor=GRID, automargin=True,
                title=dict(standoff=12, font=dict(size=12, color=MUTED)),
                tickfont=dict(size=12))
    pio.templates["voi"] = go.layout.Template(
        layout=dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, -apple-system, Segoe UI, sans-serif", color="#CBD5E1", size=13),
            colorway=[ACCENT, ACCENT_2, WARN, DANGER, "#34D399"],
            xaxis=dict(axis, showgrid=False),
            yaxis=axis,
            margin=dict(l=70, r=40, t=50, b=60),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                        bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
            coloraxis=dict(colorbar=dict(
                thickness=12, len=0.85, outlinewidth=0,
                title=dict(side="top", font=dict(size=12, color=MUTED)),
                tickfont=dict(size=11),
            )),
            hoverlabel=dict(bgcolor="#111A2E", bordercolor=ACCENT, font=dict(color="#F1F5F9")),
        ),
        data=dict(bar=[go.Bar(cliponaxis=False)]),
    )
    pio.templates.default = "voi"


def show_table(df, **kwargs):
    """Every table in the app: progress bars for %, R$ for money, stars for reviews."""
    config = {}
    for col in df.columns:
        name = str(col).lower()
        if "%" in name:
            config[col] = st.column_config.ProgressColumn(
                col, min_value=0, max_value=100, format="%.1f%%", width="medium")
        elif "r$" in name:
            config[col] = st.column_config.NumberColumn(col, format="R$ %.2f", width="medium")
        elif "review" in name:
            config[col] = st.column_config.NumberColumn(col, format="%.2f ★", width="small")
        elif str(df[col].dtype).startswith(("int", "Int")):
            config[col] = st.column_config.NumberColumn(col, format="localized", width="small")
        elif str(df[col].dtype).startswith("float"):
            config[col] = st.column_config.NumberColumn(col, format="%.1f", width="small")
        else:
            config[col] = st.column_config.Column(col, width="medium")
    kwargs.setdefault("hide_index", True)
    st.dataframe(df, column_config=config, **kwargs)


def hero(eyebrow, title, subtitle):
    st.markdown(
        f'<div class="voi-hero"><div class="voi-eyebrow">{eyebrow}</div>'
        f'<div class="voi-title">{title}</div><div class="voi-sub">{subtitle}</div></div>',
        unsafe_allow_html=True,
    )


def kpi_card(column, label, value, sub=""):
    column.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def section_title(text):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def chart_title(text):
    st.markdown(f'<div class="chart-title">{text}</div>', unsafe_allow_html=True)


def insight(text):
    st.markdown(
        f'<div class="insight"><span class="insight-tag">What this shows</span>{text}</div>',
        unsafe_allow_html=True,
    )


def sidebar_brand():
    """Brand card shown in the sidebar under the filters."""
    st.sidebar.markdown(
        '<div style="margin-top:18px;padding:14px 16px;border-radius:14px;'
        'background:linear-gradient(145deg,rgba(34,211,238,0.10),rgba(129,140,248,0.08));'
        'border:1px solid rgba(34,211,238,0.22);font-family:Inter,sans-serif;">'
        '<div style="color:#22D3EE;font-size:0.68rem;font-weight:700;letter-spacing:0.14em;">'
        'A VILLEGAS ANALYTICS PROJECT</div>'
        '<div style="color:#F1F5F9;font-size:0.95rem;font-weight:700;margin-top:4px;">'
        'Villegas Operations Intelligence</div>'
        '<div style="color:#8FA3BF;font-size:0.78rem;margin-top:2px;">Built by Juan Villegas</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def page_footer():
    """Brand line at the bottom of every page."""
    st.markdown(
        '<div style="margin-top:2.5rem;padding-top:1rem;'
        'border-top:1px solid rgba(148,163,184,0.15);font-family:Inter,sans-serif;'
        'font-size:0.8rem;color:#8FA3BF;">'
        '<b style="color:#22D3EE;">Villegas Analytics</b> · Villegas Operations Intelligence'
        ' · Built by Juan Villegas</div>',
        unsafe_allow_html=True,
    )