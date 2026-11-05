"""Shared look and feel: page CSS, chart template, and reusable HTML pieces."""
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
.insight {font-family: 'Inter', sans-serif; background: linear-gradient(90deg, rgba(34,211,238,0.09), rgba(34,211,238,0.02)); border: 1px solid rgba(34,211,238,0.18); border-left: 3px solid #22D3EE; border-radius: 12px; padding: 12px 16px; color: #CBD5E1; font-size: 0.9rem; line-height: 1.55; margin: 6px 0 4px;}
.insight b {color: #F8FAFC;}
.insight-tag {display: block; color: #22D3EE; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 4px;}
[class*="st-key-card"] {background: linear-gradient(145deg, rgba(20,30,52,0.88), rgba(12,19,35,0.88)); border-radius: 18px !important; border: 1px solid rgba(148,163,184,0.14) !important; box-shadow: 0 16px 38px rgba(0,0,0,0.42), inset 0 1px 0 rgba(255,255,255,0.05); padding: 6px 4px;}
section[data-testid="stSidebar"] {border-right: 1px solid rgba(148,163,184,0.12);}
</style>
"""


def apply_style():
    """Load the page CSS and set the default chart style. Call once at the top of every page."""
    st.markdown(CSS, unsafe_allow_html=True)
    pio.templates["voi"] = go.layout.Template(
        layout=dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, -apple-system, Segoe UI, sans-serif", color="#CBD5E1", size=13),
            colorway=[ACCENT, ACCENT_2, WARN, DANGER, "#34D399"],
            xaxis=dict(gridcolor=GRID, zeroline=False, linecolor=GRID, showgrid=False),
            yaxis=dict(gridcolor=GRID, zeroline=False, linecolor=GRID),
            margin=dict(l=10, r=10, t=20, b=10),
            hoverlabel=dict(bgcolor="#111A2E", bordercolor=ACCENT, font=dict(color="#F1F5F9")),
        )
    )
    pio.templates.default = "voi"


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