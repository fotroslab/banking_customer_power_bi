#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سامانه هوش تجاری بانک آریا — نمای ۳۶۰ درجه مشتری و تحلیل ریزش
طراحی بومی راست‌چین (RTL) با تایپوگرافی استاندارد فارسی (Vazirmatn FD)،
چیدمان طبیعی داشبورد بانکی و ۵ صفحه تحلیلی تعاملی.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FONTS_DIR = BASE_DIR / "assets" / "fonts"

# پالت رنگ رسمی تم Bank Aria Fa
COLOR_PRIMARY = "#0b6e4f"
COLOR_PRIMARY_DARK = "#074d37"
COLOR_PRIMARY_SOFT = "#eaf4f0"
COLOR_ACCENT = "#d4a017"
COLOR_ACCENT_SOFT = "#fcf6e4"
COLOR_BG = "#f4f7f5"
COLOR_CARD_BG = "#ffffff"
COLOR_TEXT = "#102a20"
COLOR_MUTED = "#526b61"
COLOR_BORDER = "#dce7e1"
COLOR_CHURN = "#c93b2b"
COLOR_SECONDARY = "#2b7a78"

PAGES = [
    "نمای کلی",
    "تحلیل ریزش مشتری",
    "استان‌ها و شعب",
    "سبد محصولات",
    "جستجوی مشتریان",
]

GEO_FA_MAP = {
    "France": "فرانسه",
    "Germany": "آلمان",
    "Spain": "اسپانیا",
}

EN_TO_FA_TRANS = str.maketrans("0123456789,", "۰۱۲۳۴۵۶۷۸۹٬")
RLM = "\u200f"


def to_fa(val: Any) -> str:
    """تبدیل ارقام انگلیسی و جداکننده هزارگان به معادل فارسی."""
    return str(val).translate(EN_TO_FA_TRANS)


def fmt_int_fa(val: int | float) -> str:
    return to_fa(f"{int(round(val)):,}")


def fmt_pct_fa(val: float, decimals: int = 1) -> str:
    return to_fa(f"{val:.{decimals}f}") + "٪"


def fmt_irr_card_fa(val_irr: float) -> tuple[str, str]:
    """برگرداندن (عدد اصلی، واحد) برای نمایش تمیز و متوازن در کارت KPI."""
    abs_val = abs(val_irr)
    if abs_val >= 1e12:
        return to_fa(f"{val_irr / 1e12:,.2f}"), "هزار میلیارد ریال"
    elif abs_val >= 1e9:
        return to_fa(f"{val_irr / 1e9:,.1f}"), "میلیارد ریال"
    elif abs_val >= 1e6:
        return to_fa(f"{val_irr / 1e6:,.1f}"), "میلیون ریال"
    return fmt_int_fa(val_irr), "ریال"


def fmt_irr_inline_fa(val_irr: float) -> str:
    num_str, unit_str = fmt_irr_card_fa(val_irr)
    return f"{num_str} {unit_str}"


def svg_rtl(text: str) -> str:
    """
    تثبیت ترتیب راست‌به‌چپ کلمات و اعداد فارسی در موتور رندر SVG نمودارهای Plotly
    که به دلیل `.js-plotly-plot * { direction: ltr !important; }` در محیط LTR رندر می‌شوند.
    """
    tokens = str(text).split(" ")
    return RLM + (f" {RLM}").join(tokens) + RLM


@st.cache_data(show_spinner=False)
def load_font_base64(filename: str) -> str:
    path = FONTS_DIR / filename
    if path.exists():
        return base64.b64encode(path.read_bytes()).decode("ascii")
    return ""


def inject_rtl_css() -> None:
    reg_b64 = load_font_base64("Vazirmatn-FD-Regular.woff2")
    med_b64 = load_font_base64("Vazirmatn-FD-Medium.woff2")
    semi_b64 = load_font_base64("Vazirmatn-FD-SemiBold.woff2")
    bold_b64 = load_font_base64("Vazirmatn-FD-Bold.woff2")

    font_faces = ""
    for weight, b64 in [
        (400, reg_b64),
        (500, med_b64),
        (600, semi_b64),
        (700, bold_b64),
    ]:
        if b64:
            font_faces += f"""
            @font-face {{
                font-family: 'Vazirmatn FD';
                src: url('data:font/woff2;base64,{b64}') format('woff2');
                font-weight: {weight};
                font-style: normal;
                font-display: block;
            }}
            """

    css = f"""
    <style>
    {font_faces}

    /* تنظیم تایپوگرافی و رنگ زمینه کل برنامه */
    html, body, .stApp, [data-testid="stAppViewContainer"] {{
        background-color: {COLOR_BG} !important;
        color: {COLOR_TEXT} !important;
        font-family: 'Vazirmatn FD', 'Vazirmatn', Tahoma, sans-serif !important;
        line-height: 1.65 !important;
    }}

    /* انتقال سایدبار به سمت راست صفحه برای تجربه کاربری ۱۰۰٪ راست‌چین طبیعی */
    [data-testid="stAppViewContainer"] {{
        flex-direction: row-reverse !important;
    }}

    /* مخفی کردن نوار ابزار پیش‌فرض بالای استریم‌لیت برای ظاهر طبیعی سامانه بانکی */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        height: 1.5rem !important;
    }}
    [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu, footer {{
        display: none !important;
    }}

    /* کانتینر اصلی محتوا — راست‌چین کامل */
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"],
    .main .block-container {{
        direction: rtl !important;
        text-align: right !important;
        padding-top: 1.1rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1460px !important;
    }}

    /* راست‌چین کردن تمامی بلوک‌های متنی، عناوین و ویجت‌ها */
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stMarkdownContainer"] ul,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stCaptionContainer"],
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    label {{
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Vazirmatn FD', 'Vazirmatn', Tahoma, sans-serif !important;
        letter-spacing: 0 !important;
    }}

    /* چیدمان ستون‌های افقی از راست به چپ */
    [data-testid="stHorizontalBlock"] {{
        direction: rtl !important;
    }}

    /* طراحی سایدبار سمت راست به‌سبک پورتال‌های سازمانی بانک */
    section[data-testid="stSidebar"] {{
        background-color: #ffffff !important;
        border-left: 1px solid {COLOR_BORDER} !important;
        border-right: none !important;
        box-shadow: -4px 0 18px rgba(11, 110, 79, 0.04) !important;
        min-width: 290px !important;
        max-width: 310px !important;
    }}

    section[data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"],
    [data-testid="stSidebarUserContent"] {{
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Vazirmatn FD', 'Vazirmatn', Tahoma, sans-serif !important;
    }}

    [data-testid="stSidebarUserContent"] {{
        padding-top: 1.1rem !important;
        padding-right: 1.15rem !important;
        padding-left: 1.15rem !important;
    }}

    /* استایل منوی ناوبری رادیویی در سایدبار راست */
    [data-testid="stRadio"] > label[data-testid="stWidgetLabel"] {{
        display: none !important;
    }}

    [data-testid="stRadio"] div[role="radiogroup"] {{
        direction: rtl !important;
        gap: 0.35rem !important;
        width: 100% !important;
    }}

    [data-testid="stRadio"] div[role="radiogroup"] label {{
        direction: rtl !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        background-color: #f5f9f7 !important;
        border: 1px solid #dce8e2 !important;
        border-radius: 8px !important;
        padding: 0.44rem 0.7rem !important;
        margin: 0 !important;
        width: 100% !important;
        box-sizing: border-box !important;
        transition: all 0.15s ease-in-out !important;
        cursor: pointer !important;
    }}

    [data-testid="stRadio"] div[role="radiogroup"] label:hover {{
        background-color: #e6f2ec !important;
        border-color: {COLOR_PRIMARY} !important;
    }}

    [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {{
        background-color: {COLOR_PRIMARY_SOFT} !important;
        border-color: {COLOR_PRIMARY} !important;
        border-right: 4px solid {COLOR_PRIMARY} !important;
    }}

    [data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {{
        margin-left: 0.5rem !important;
        margin-right: 0 !important;
    }}

    [data-testid="stRadio"] div[role="radiogroup"] label p {{
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: {COLOR_TEXT} !important;
        margin: 0 !important;
    }}

    /* استایل تگ‌های Multiselect به رنگ سبز ملایم سازمانی و بدون هیچ‌گونه بریدگی ارتفاع */
    [data-testid="stMultiSelect"] *,
    [data-baseweb="select"],
    [data-baseweb="select"] * {{
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Vazirmatn FD', 'Vazirmatn', Tahoma, sans-serif !important;
        max-height: none !important;
    }}

    [data-baseweb="select"] > div {{
        background-color: #f8fbf9 !important;
        border-color: #cedfd6 !important;
        border-radius: 8px !important;
        min-height: 36px !important;
        height: auto !important;
        padding-top: 2px !important;
        padding-bottom: 2px !important;
    }}

    span[data-baseweb="tag"] {{
        background-color: {COLOR_PRIMARY_SOFT} !important;
        color: {COLOR_PRIMARY_DARK} !important;
        border: 1px solid #b8dcd0 !important;
        border-radius: 5px !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        height: 22px !important;
        margin: 2px !important;
        padding-right: 5px !important;
        padding-left: 3px !important;
        direction: rtl !important;
    }}

    span[data-baseweb="tag"] span {{
        color: {COLOR_PRIMARY_DARK} !important;
        font-family: 'Vazirmatn FD', Tahoma, sans-serif !important;
    }}

    /* ورودی متن و جستجو راست‌چین */
    [data-baseweb="input"] input {{
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Vazirmatn FD', Tahoma, sans-serif !important;
        font-size: 0.88rem !important;
    }}

    /* الزام حیاتی: محافظت از محورها و مختصات Plotly در محیط RTL */
    .js-plotly-plot, .js-plotly-plot * {{
        direction: ltr !important;
    }}

    /* اتصال یکپارچه هدر فارسی نمودار به بدنه نمودار Plotly */
    div[data-testid="stElementContainer"]:has(.chart-card-header) {{
        margin-bottom: -1rem !important;
    }}

    /* کارت‌های نمودار Plotly */
    [data-testid="stPlotlyChart"] {{
        background: #ffffff;
        border: 1px solid {COLOR_BORDER};
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 0.2rem 0.5rem 0.35rem 0.5rem;
        margin-bottom: 0.65rem;
        box-shadow: 0 2px 8px rgba(16, 42, 32, 0.03);
    }}

    /* هدر فارسی بالای هر نمودار (کاملاً راست‌چین و طبیعی) */
    .chart-card-header {{
        background: #ffffff;
        border: 1px solid {COLOR_BORDER};
        border-bottom: 1px solid #eef4f0;
        border-right: 4px solid {COLOR_PRIMARY};
        border-radius: 12px 12px 0 0;
        padding: 0.75rem 1.05rem 0.6rem 1.05rem;
        margin-bottom: 0;
        direction: rtl !important;
        text-align: right !important;
    }}

    .chart-card-title {{
        color: {COLOR_TEXT};
        font-size: 0.96rem;
        font-weight: 700;
        margin: 0 0 0.15rem 0;
        direction: rtl !important;
        text-align: right !important;
    }}

    .chart-card-sub {{
        color: {COLOR_MUTED};
        font-size: 0.78rem;
        font-weight: 400;
        margin: 0;
        direction: rtl !important;
        text-align: right !important;
    }}

    /* برندینگ سایدبار */
    .sidebar-brand {{
        background: linear-gradient(135deg, {COLOR_PRIMARY} 0%, {COLOR_PRIMARY_DARK} 100%);
        color: #ffffff;
        border-radius: 12px;
        padding: 0.95rem 1rem;
        margin-bottom: 1rem;
        border-bottom: 3px solid {COLOR_ACCENT};
        direction: rtl !important;
        text-align: right !important;
    }}

    .sidebar-brand-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }}

    .sidebar-brand-sub {{
        font-size: 0.76rem;
        color: #d8ede5;
        margin: 0.2rem 0 0 0;
    }}

    .sidebar-section-label {{
        font-size: 0.78rem;
        font-weight: 700;
        color: {COLOR_PRIMARY_DARK};
        margin: 0.85rem 0 0.4rem 0;
        padding-bottom: 0.25rem;
        border-bottom: 1px solid #e3ede8;
        direction: rtl !important;
        text-align: right !important;
    }}

    /* نوار بالایی گزارش (سربرگ طبیعی مدیریتی) */
    .top-masthead {{
        background: #ffffff;
        border: 1px solid {COLOR_BORDER};
        border-right: 5px solid {COLOR_PRIMARY};
        border-radius: 12px;
        padding: 0.9rem 1.3rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        direction: rtl !important;
        text-align: right !important;
        box-shadow: 0 2px 10px rgba(16, 42, 32, 0.03);
    }}

    .masthead-right {{
        direction: rtl !important;
        text-align: right !important;
        flex: 1 1 auto;
    }}

    .masthead-breadcrumb {{
        font-size: 0.75rem;
        color: {COLOR_PRIMARY};
        font-weight: 600;
        margin-bottom: 0.15rem;
    }}

    .masthead-title {{
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: {COLOR_TEXT} !important;
        margin: 0 !important;
        line-height: 1.4 !important;
    }}

    .masthead-desc {{
        font-size: 0.8rem;
        color: {COLOR_MUTED};
        margin: 0.15rem 0 0 0;
    }}

    .masthead-meta {{
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 0.35rem;
        flex-shrink: 0;
        direction: rtl !important;
    }}

    .meta-row {{
        display: flex;
        flex-direction: row;
        gap: 0.45rem;
        direction: rtl !important;
    }}

    .meta-pill {{
        background: #f5f9f7;
        border: 1px solid #d5e4dc;
        border-radius: 7px;
        padding: 0.28rem 0.65rem;
        font-size: 0.74rem;
        color: {COLOR_TEXT};
        white-space: nowrap;
        direction: rtl !important;
        text-align: right !important;
    }}

    .meta-pill b {{
        color: {COLOR_PRIMARY_DARK};
    }}

    /* شبکه ۴ ستونه کارت‌های KPI — ۱۰۰٪ راست‌چین و هم‌ارتفاع */
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.15rem;
        direction: rtl !important;
    }}

    @media (max-width: 1100px) {{
        .kpi-grid {{
            grid-template-columns: repeat(2, 1fr);
        }}
    }}

    .kpi-card {{
        background: {COLOR_CARD_BG};
        border-radius: 12px;
        padding: 1rem 1.15rem;
        border: 1px solid {COLOR_BORDER};
        border-top: 3px solid {COLOR_PRIMARY};
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 126px;
        direction: rtl !important;
        text-align: right !important;
        box-shadow: 0 2px 8px rgba(16, 42, 32, 0.03);
    }}

    .kpi-card.alert {{
        border-top-color: {COLOR_CHURN};
    }}

    .kpi-card.gold {{
        border-top-color: {COLOR_ACCENT};
    }}

    .kpi-card.teal {{
        border-top-color: {COLOR_SECONDARY};
    }}

    .kpi-top {{
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        direction: rtl !important;
    }}

    .kpi-title {{
        color: {COLOR_MUTED};
        font-size: 0.82rem;
        font-weight: 600;
    }}

    .kpi-tag {{
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.12rem 0.5rem;
        border-radius: 6px;
        background: {COLOR_PRIMARY_SOFT};
        color: {COLOR_PRIMARY_DARK};
    }}

    .kpi-tag.alert {{
        background: #fdecea;
        color: {COLOR_CHURN};
    }}

    .kpi-tag.gold {{
        background: {COLOR_ACCENT_SOFT};
        color: #8a6200;
    }}

    .kpi-main {{
        margin: 0.45rem 0 0.35rem 0;
        display: flex;
        flex-direction: row;
        align-items: baseline;
        gap: 0.35rem;
        direction: rtl !important;
    }}

    .kpi-value {{
        color: {COLOR_TEXT};
        font-size: 1.55rem;
        font-weight: 700;
        line-height: 1.2;
    }}

    .kpi-unit {{
        color: {COLOR_MUTED};
        font-size: 0.82rem;
        font-weight: 500;
    }}

    .kpi-sub {{
        color: {COLOR_MUTED};
        font-size: 0.75rem;
        border-top: 1px dashed #e5eee9;
        padding-top: 0.38rem;
        direction: rtl !important;
        text-align: right !important;
    }}

    /* کادر یادداشت روش‌شناختی و صداقت داده */
    .honesty-box {{
        background-color: {COLOR_ACCENT_SOFT};
        border: 1px solid #ead394;
        border-right: 4px solid {COLOR_ACCENT};
        border-radius: 10px;
        padding: 0.75rem 1.05rem;
        margin-bottom: 1rem;
        font-size: 0.82rem;
        color: #3f310d;
        direction: rtl !important;
        text-align: right !important;
        line-height: 1.65;
    }}

    /* کارت‌های بخش و جدول فارسی */
    .section-card {{
        background-color: #ffffff;
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 1rem;
        direction: rtl !important;
        text-align: right !important;
        box-shadow: 0 2px 8px rgba(16, 42, 32, 0.03);
    }}

    .rtl-table-wrap {{
        background: #ffffff;
        border: 1px solid {COLOR_BORDER};
        border-radius: 12px;
        overflow-x: auto;
        margin-bottom: 1rem;
        direction: rtl !important;
        box-shadow: 0 2px 8px rgba(16, 42, 32, 0.03);
    }}

    table.aria-table {{
        width: 100%;
        border-collapse: collapse;
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Vazirmatn FD', Tahoma, sans-serif !important;
        font-size: 0.84rem;
    }}

    table.aria-table thead tr {{
        background-color: #eef5f1;
        border-bottom: 2px solid #cfe0d7;
    }}

    table.aria-table th {{
        color: {COLOR_PRIMARY_DARK};
        font-weight: 700;
        padding: 0.65rem 0.9rem;
        text-align: right !important;
        white-space: nowrap;
    }}

    table.aria-table td {{
        color: {COLOR_TEXT};
        padding: 0.58rem 0.9rem;
        border-bottom: 1px solid #edf3ef;
        text-align: right !important;
        white-space: nowrap;
    }}

    table.aria-table tbody tr:hover {{
        background-color: #f8fbf9;
    }}

    .status-badge {{
        display: inline-block;
        padding: 0.12rem 0.55rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }}

    .status-badge.churn {{
        background: #fdecea;
        color: {COLOR_CHURN};
    }}

    .status-badge.ok {{
        background: {COLOR_PRIMARY_SOFT};
        color: {COLOR_PRIMARY_DARK};
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_chart_header(title: str, subtitle: str) -> None:
    """نمایش عنوان و زیرعنوان نمودار با HTML/CSS کاملاً راست‌چین بالای بوم Plotly."""
    st.markdown(
        f"""
        <div class="chart-card-header">
            <div class="chart-card-title">{title}</div>
            <div class="chart-card-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_rtl_html_table(df: pd.DataFrame) -> None:
    """رندر جدول کاملاً راست‌چین با فونت وزیرمتن و اعداد فارسی."""
    headers = "".join(f"<th>{col}</th>" for col in df.columns)
    rows_html = []
    for _, row in df.iterrows():
        cells = "".join(f"<td>{val}</td>" for val in row)
        rows_html.append(f"<tr>{cells}</tr>")
    body = "".join(rows_html)
    st.markdown(
        f"""
        <div class="rtl-table-wrap">
            <table class="aria-table">
                <thead><tr>{headers}</tr></thead>
                <tbody>{body}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_fig(
    fig: go.Figure,
    height: int = 335,
    margin: dict[str, int] | None = None,
    show_legend: bool = True,
) -> go.Figure:
    """اعمال استایل یکپارچه Bank Aria Fa روی نمودارهای Plotly با حفظ کامل margin دلخواه."""
    default_margin = {"l": 48, "r": 48, "t": 24, "b": 42}
    if margin is not None:
        default_margin.update(margin)

    fig.update_layout(
        height=height,
        margin=default_margin,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fbfdfb",
        font=dict(
            family="Vazirmatn FD, Vazirmatn, Tahoma, sans-serif",
            size=12,
            color=COLOR_TEXT,
        ),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            bgcolor="rgba(255,255,255,0.9)",
            font=dict(size=11.5),
        ),
        hoverlabel=dict(
            font_family="Vazirmatn FD, Vazirmatn, Tahoma, sans-serif",
            font_size=12,
            align="right",
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#eef4f0",
        linecolor="#cfe0d7",
        tickfont=dict(family="Vazirmatn FD, Vazirmatn, Tahoma, sans-serif", size=11.5),
        title_font=dict(family="Vazirmatn FD, Vazirmatn, Tahoma, sans-serif", size=12, color=COLOR_MUTED),
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#eef4f0",
        linecolor="#cfe0d7",
        tickfont=dict(family="Vazirmatn FD, Vazirmatn, Tahoma, sans-serif", size=11.5),
        title_font=dict(family="Vazirmatn FD, Vazirmatn, Tahoma, sans-serif", size=12, color=COLOR_MUTED),
        automargin=True,
    )
    return fig


@st.cache_data(show_spinner=False)
def load_data() -> dict[str, Any]:
    if not (PROCESSED_DIR / "fact_snapshot.csv").exists():
        from scripts.build_data import main as build_data_main
        build_data_main()

    dim_customer = pd.read_csv(PROCESSED_DIR / "dim_customer.csv")
    dim_branch = pd.read_csv(PROCESSED_DIR / "dim_branch.csv")
    dim_product = pd.read_csv(PROCESSED_DIR / "dim_product.csv")
    dim_date = pd.read_csv(PROCESSED_DIR / "dim_date.csv")
    fact_snapshot = pd.read_csv(PROCESSED_DIR / "fact_snapshot.csv")
    fact_product_holding = pd.read_csv(PROCESSED_DIR / "fact_product_holding.csv")
    with open(PROCESSED_DIR / "summary_stats.json", "r", encoding="utf-8") as f:
        summary_stats = json.load(f)

    df_360 = fact_snapshot.merge(
        dim_customer[
            [
                "customer_id",
                "full_name_fa",
                "original_surname",
                "gender",
                "age_group",
                "province",
                "source_geography",
                "tenure_group",
                "credit_band",
                "has_credit_card_label",
                "activity_status_label",
            ]
        ],
        on="customer_id",
        how="left",
    ).merge(
        dim_branch[["branch_id", "branch_name", "city", "branch_tier", "region_manager"]],
        on="branch_id",
        how="left",
    )

    holdings_enriched = fact_product_holding.merge(
        dim_product[["product_id", "product_name", "product_category", "is_credit_product"]],
        on="product_id",
        how="left",
    ).merge(
        df_360[
            [
                "customer_id",
                "province",
                "age_group",
                "num_of_products",
                "activity_status_label",
                "exited",
                "churn_status_label",
            ]
        ],
        on="customer_id",
        how="left",
    )

    return {
        "dim_customer": dim_customer,
        "dim_branch": dim_branch,
        "dim_product": dim_product,
        "dim_date": dim_date,
        "fact_snapshot": fact_snapshot,
        "fact_product_holding": fact_product_holding,
        "df_360": df_360,
        "holdings_enriched": holdings_enriched,
        "summary_stats": summary_stats,
    }


def render_kpi_row(df: pd.DataFrame) -> None:
    total_cust = len(df)
    if total_cust == 0:
        st.warning("هیچ مشتری با ترکیب فیلترهای انتخابی یافت نشد. لطفاً فیلترهای نوار راست را بازنگری کنید.")
        return

    total_balance_irr = float(df["balance_irr"].sum())
    avg_balance_irr = float(df["balance_irr"].mean())
    churn_rate_pct = float(df["exited"].mean() * 100.0)
    churn_count = int(df["exited"].sum())
    retained_pct = 100.0 - churn_rate_pct
    avg_products = float(df["num_of_products"].mean())
    total_holdings = int(df["num_of_products"].sum())
    active_share_pct = float(df["is_active_member"].mean() * 100.0)
    active_count = int(df["is_active_member"].sum())
    zero_bal_pct = float(df["is_zero_balance"].mean() * 100.0)
    cr_card_pct = float(df["has_cr_card"].mean() * 100.0)

    bal_num, bal_unit = fmt_irr_card_fa(total_balance_irr)
    avg_bal_str = fmt_irr_inline_fa(avg_balance_irr)

    st.markdown(
        f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-title">مانده کل سپرده‌ها</span>
                    <span class="kpi-tag">مقیاس نمایشی ریال</span>
                </div>
                <div class="kpi-main">
                    <span class="kpi-value">{bal_num}</span>
                    <span class="kpi-unit">{bal_unit}</span>
                </div>
                <div class="kpi-sub">
                    میانگین سرانه: {avg_bal_str} | حساب با مانده صفر: {fmt_pct_fa(zero_bal_pct, 1)}
                </div>
            </div>
            <div class="kpi-card alert">
                <div class="kpi-top">
                    <span class="kpi-title">نرخ ریزش مشتریان</span>
                    <span class="kpi-tag alert">نرخ نگهداشت: {fmt_pct_fa(retained_pct, 2)}</span>
                </div>
                <div class="kpi-main">
                    <span class="kpi-value">{fmt_pct_fa(churn_rate_pct, 2)}</span>
                    <span class="kpi-unit">({fmt_int_fa(churn_count)} نفر)</span>
                </div>
                <div class="kpi-sub">
                    از مجموع {fmt_int_fa(total_cust)} مشتری در برش انتخابی
                </div>
            </div>
            <div class="kpi-card gold">
                <div class="kpi-top">
                    <span class="kpi-title">میانگین محصول هر مشتری</span>
                    <span class="kpi-tag gold">عمق رابطه بانکی</span>
                </div>
                <div class="kpi-main">
                    <span class="kpi-value">{to_fa(f"{avg_products:.2f}")}</span>
                    <span class="kpi-unit">محصول فعال</span>
                </div>
                <div class="kpi-sub">
                    مجموع کل محصولات سبد مشتریان: {fmt_int_fa(total_holdings)} فقره
                </div>
            </div>
            <div class="kpi-card teal">
                <div class="kpi-top">
                    <span class="kpi-title">سهم مشتریان فعال</span>
                    <span class="kpi-tag">تعامل مستمر</span>
                </div>
                <div class="kpi-main">
                    <span class="kpi-value">{fmt_pct_fa(active_share_pct, 1)}</span>
                    <span class="kpi-unit">({fmt_int_fa(active_count)} نفر)</span>
                </div>
                <div class="kpi-sub">
                    ضریب نفوذ کارت اعتباری: {fmt_pct_fa(cr_card_pct, 1)} از مشتریان
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_overview(df: pd.DataFrame) -> None:
    render_kpi_row(df)
    if df.empty:
        return

    # در چیدمان RTL، ستون اول (col_right) در سمت راست و ستون دوم (col_left) در سمت چپ قرار می‌گیرد
    col_right, col_left = st.columns(2, gap="medium")

    with col_right:
        render_chart_header(
            "نرخ ریزش مشتریان به تفکیک استان (نگاشت ۱:۱ منبع)",
            "نرخ ۳۲.۴۴٪ در اصفهان بازتاب زیرجامعه آلمان در دیتاست اصلی است (نه واقعیت اقتصادی استان)",
        )
        prov_grp = (
            df.groupby(["province", "source_geography"], as_index=False)
            .agg(
                customers=("customer_id", "count"),
                churned=("exited", "sum"),
                churn_rate_pct=("exited", lambda s: s.mean() * 100.0),
            )
            .sort_values("churn_rate_pct", ascending=True)
        )
        prov_grp["y_label"] = prov_grp.apply(
            lambda r: svg_rtl(f"استان {r['province']} — منبع {GEO_FA_MAP.get(r['source_geography'], r['source_geography'])}"),
            axis=1,
        )
        prov_grp["bar_text"] = prov_grp.apply(
            lambda r: svg_rtl(f"{fmt_pct_fa(r['churn_rate_pct'], 2)} — {fmt_int_fa(r['churned'])} نفر"),
            axis=1,
        )

        fig_prov = go.Figure(
            go.Bar(
                x=prov_grp["churn_rate_pct"],
                y=prov_grp["y_label"],
                orientation="h",
                text=prov_grp["bar_text"],
                textposition="outside",
                cliponaxis=False,
                marker_color=[
                    COLOR_CHURN if v > 25 else COLOR_PRIMARY for v in prov_grp["churn_rate_pct"]
                ],
                hovertemplate="<b>%{y}</b><br>نرخ ریزش: %{x:.2f}%<extra></extra>",
            )
        )
        fig_prov.update_layout(
            xaxis_title=svg_rtl("نرخ ریزش مشتریان (درصد)"),
            yaxis_title="",
            xaxis_range=[0, max(44.0, float(prov_grp["churn_rate_pct"].max()) * 1.32)],
        )
        style_fig(fig_prov, height=320, margin={"l": 175, "r": 110, "t": 18, "b": 42}, show_legend=False)
        st.plotly_chart(fig_prov, width="stretch")

    with col_left:
        render_chart_header(
            "نرخ ریزش بر اساس تعداد محصولات بانکی مشتری",
            "پایین‌ترین نرخ ریزش در مشتریان دارای ۲ محصول (۷.۵۸٪) و جهش ریسک در سبدهای ۳ و ۴ محصولی",
        )
        prod_grp = (
            df.groupby("num_of_products", as_index=False)
            .agg(
                customers=("customer_id", "count"),
                churn_rate_pct=("exited", lambda s: s.mean() * 100.0),
            )
            .sort_values("num_of_products")
        )
        prod_grp["x_label"] = prod_grp["num_of_products"].apply(
            lambda n: svg_rtl(f"سبد {to_fa(n)} محصولی")
        )
        prod_grp["bar_text"] = prod_grp.apply(
            lambda r: svg_rtl(f"{fmt_pct_fa(r['churn_rate_pct'], 1)} — {fmt_int_fa(r['customers'])} نفر"),
            axis=1,
        )

        fig_prod = go.Figure(
            go.Bar(
                x=prod_grp["x_label"],
                y=prod_grp["churn_rate_pct"],
                text=prod_grp["bar_text"],
                textposition="outside",
                cliponaxis=False,
                marker_color=[COLOR_PRIMARY, "#1f8a65", COLOR_ACCENT, COLOR_CHURN][: len(prod_grp)],
                hovertemplate="<b>%{x}</b><br>نرخ ریزش: %{y:.2f}%<extra></extra>",
            )
        )
        fig_prod.update_layout(
            xaxis_title=svg_rtl("تعداد محصولات در سبد مشتری"),
            yaxis_title=svg_rtl("نرخ ریزش (درصد)"),
            yaxis_range=[0, 118],
        )
        style_fig(fig_prod, height=320, margin={"l": 52, "r": 36, "t": 22, "b": 42}, show_legend=False)
        st.plotly_chart(fig_prod, width="stretch")

    col_r2, col_l2 = st.columns(2, gap="medium")

    with col_r2:
        render_chart_header(
            "توزیع سنی مشتریان بانک آریا",
            "تمرکز اصلی جمعیت مشتریان در رده سنی ۳۰ تا ۳۹ سال (۴٬۳۴۶ نفر معادل ۴۳.۵٪ کل مشتریان)",
        )
        age_order = ["زیر ۳۰ سال", "۳۰ تا ۳۹ سال", "۴۰ تا ۴۹ سال", "۵۰ تا ۵۹ سال", "۶۰ سال به بالا"]
        age_grp = (
            df.groupby("age_group", as_index=False)
            .agg(
                customers=("customer_id", "count"),
                churn_rate_pct=("exited", lambda s: s.mean() * 100.0),
            )
        )
        age_grp["order"] = age_grp["age_group"].apply(
            lambda x: age_order.index(x) if x in age_order else 99
        )
        age_grp = age_grp.sort_values("order")
        age_grp["x_label"] = age_grp["age_group"].apply(svg_rtl)
        age_grp["bar_text"] = age_grp["customers"].apply(lambda c: svg_rtl(f"{fmt_int_fa(c)} نفر"))

        fig_age = go.Figure(
            go.Bar(
                x=age_grp["x_label"],
                y=age_grp["customers"],
                marker_color=COLOR_PRIMARY,
                text=age_grp["bar_text"],
                textposition="outside",
                cliponaxis=False,
            )
        )
        fig_age.update_layout(
            xaxis_title=svg_rtl("رده سنی مشتریان"),
            yaxis_title=svg_rtl("تعداد مشتریان"),
            yaxis_range=[0, float(age_grp["customers"].max()) * 1.24 if not age_grp.empty else 100],
        )
        style_fig(fig_age, height=320, margin={"l": 56, "r": 32, "t": 22, "b": 42}, show_legend=False)
        st.plotly_chart(fig_age, width="stretch")

    with col_l2:
        render_chart_header(
            "مقایسه وضعیت ماندگاری در مشتریان فعال و غیرفعال",
            "نرخ ریزش در مشتریان غیرفعال (۲۶.۸۵٪) تقریباً دو برابر مشتریان فعال (۱۴.۲۷٪) است",
        )
        act_grp = (
            df.groupby(["activity_status_label", "churn_status_label"], as_index=False)
            .agg(customers=("customer_id", "count"))
        )
        act_grp["x_label"] = act_grp["activity_status_label"].apply(
            lambda s: svg_rtl(f"مشتریان {s}")
        )
        act_grp["status_rtl"] = act_grp["churn_status_label"].apply(svg_rtl)
        act_grp["bar_text"] = act_grp["customers"].apply(lambda c: svg_rtl(fmt_int_fa(c)))

        fig_act = px.bar(
            act_grp,
            x="x_label",
            y="customers",
            color="status_rtl",
            barmode="group",
            text="bar_text",
            color_discrete_map={
                svg_rtl("مانده"): COLOR_PRIMARY,
                svg_rtl("ریزش‌کرده"): COLOR_CHURN,
            },
            labels={
                "x_label": svg_rtl("وضعیت تعامل و فعالیت مشتری"),
                "customers": svg_rtl("تعداد مشتریان"),
                "status_rtl": "",
            },
        )
        fig_act.update_traces(textposition="outside", cliponaxis=False)
        fig_act.update_layout(
            yaxis_range=[0, float(act_grp["customers"].max()) * 1.25 if not act_grp.empty else 100]
        )
        style_fig(fig_act, height=320, margin={"l": 56, "r": 32, "t": 34, "b": 42}, show_legend=True)
        st.plotly_chart(fig_act, width="stretch")


def render_page_churn_analysis(df: pd.DataFrame) -> None:
    render_kpi_row(df)
    if df.empty:
        return

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        render_chart_header(
            "نرخ ریزش به تفکیک گروه سنی و جنسیت",
            "بیشترین آسیب‌پذیری ریزش در رده سنی ۵۰ تا ۵۹ سال (به‌ویژه در گروه بانوان) مشاهده می‌شود",
        )
        age_order = ["زیر ۳۰ سال", "۳۰ تا ۳۹ سال", "۴۰ تا ۴۹ سال", "۵۰ تا ۵۹ سال", "۶۰ سال به بالا"]
        ag = (
            df.groupby(["age_group", "gender"], as_index=False)
            .agg(
                churn_rate_pct=("exited", lambda s: s.mean() * 100.0),
                customers=("customer_id", "count"),
            )
        )
        ag["order"] = ag["age_group"].apply(lambda x: age_order.index(x) if x in age_order else 99)
        ag = ag.sort_values("order")
        ag["x_label"] = ag["age_group"].apply(svg_rtl)
        ag["gender_rtl"] = ag["gender"].apply(svg_rtl)
        ag["bar_text"] = ag["churn_rate_pct"].apply(lambda v: svg_rtl(fmt_pct_fa(v, 1)))

        fig_ag = px.bar(
            ag,
            x="x_label",
            y="churn_rate_pct",
            color="gender_rtl",
            barmode="group",
            text="bar_text",
            color_discrete_map={svg_rtl("زن"): COLOR_ACCENT, svg_rtl("مرد"): COLOR_PRIMARY},
            labels={
                "x_label": svg_rtl("گروه سنی"),
                "churn_rate_pct": svg_rtl("نرخ ریزش (درصد)"),
                "gender_rtl": "",
            },
        )
        fig_ag.update_traces(textposition="outside", cliponaxis=False)
        fig_ag.update_layout(
            yaxis_range=[0, max(68.0, float(ag["churn_rate_pct"].max()) * 1.25)]
        )
        style_fig(fig_ag, height=340, margin={"l": 52, "r": 36, "t": 34, "b": 42})
        st.plotly_chart(fig_ag, width="stretch")

    with c2:
        render_chart_header(
            "نرخ ریزش بر اساس رده امتیاز اعتباری مشتری",
            "مشتریان با امتیاز اعتباری ضعیف (زیر ۵۸۰) بالاترین نرخ خروج را در بین طبقات اعتباری دارند",
        )
        credit_order = [
            "ضعیف (<۵۸۰)",
            "متوسط (۵۸۰-۶۶۹)",
            "خوب (۶۷۰-۷۳۹)",
            "عالی (۷۴۰-۷۹۹)",
            "ممتاز (۸۰۰+)",
        ]
        credit_clean_labels = {
            "ضعیف (<۵۸۰)": "رده ضعیف — زیر ۵۸۰",
            "متوسط (۵۸۰-۶۶۹)": "رده متوسط — ۵۸۰ تا ۶۶۹",
            "خوب (۶۷۰-۷۳۹)": "رده خوب — ۶۷۰ تا ۷۳۹",
            "عالی (۷۴۰-۷۹۹)": "رده عالی — ۷۴۰ تا ۷۹۹",
            "ممتاز (۸۰۰+)": "رده ممتاز — بالای ۸۰۰",
        }
        cb = (
            df.groupby("credit_band", as_index=False)
            .agg(
                churn_rate_pct=("exited", lambda s: s.mean() * 100.0),
                customers=("customer_id", "count"),
            )
        )
        cb["order"] = cb["credit_band"].apply(
            lambda x: credit_order.index(x) if x in credit_order else 99
        )
        cb = cb.sort_values("order")
        cb["x_label"] = cb["credit_band"].apply(
            lambda s: svg_rtl(credit_clean_labels.get(s, s))
        )
        cb["bar_text"] = cb["churn_rate_pct"].apply(lambda v: svg_rtl(fmt_pct_fa(v, 1)))

        fig_cb = go.Figure(
            go.Bar(
                x=cb["x_label"],
                y=cb["churn_rate_pct"],
                text=cb["bar_text"],
                textposition="outside",
                cliponaxis=False,
                marker_color=COLOR_SECONDARY,
            )
        )
        fig_cb.update_layout(
            xaxis_title=svg_rtl("طبقه امتیاز اعتباری"),
            yaxis_title=svg_rtl("نرخ ریزش (درصد)"),
            yaxis_range=[0, max(34.0, float(cb["churn_rate_pct"].max()) * 1.25)],
        )
        style_fig(fig_cb, height=340, margin={"l": 52, "r": 36, "t": 22, "b": 42}, show_legend=False)
        st.plotly_chart(fig_cb, width="stretch")

    c3, c4 = st.columns(2, gap="medium")
    with c3:
        render_chart_header(
            "توزیع مانده سپرده در مشتریان مانده و ریزش‌کرده",
            "میانه مانده سپرده در مشتریان ریزش‌کرده بالاتر از مشتریان وفادار است (لزوم برنامه حفظ مشتریان کلیدی)",
        )
        df_bal = df.copy()
        df_bal["balance_billion_irr"] = df_bal["balance_irr"] / 1e9
        df_bal["status_rtl"] = df_bal["churn_status_label"].apply(
            lambda s: svg_rtl(f"مشتریان {s}")
        )
        fig_box = px.box(
            df_bal,
            x="status_rtl",
            y="balance_billion_irr",
            color="status_rtl",
            color_discrete_map={
                svg_rtl("مشتریان مانده"): COLOR_PRIMARY,
                svg_rtl("مشتریان ریزش‌کرده"): COLOR_CHURN,
            },
            labels={
                "status_rtl": svg_rtl("وضعیت ماندگاری مشتری"),
                "balance_billion_irr": svg_rtl("مانده سپرده (میلیارد ریال نمایشی)"),
            },
        )
        style_fig(fig_box, height=335, margin={"l": 56, "r": 36, "t": 22, "b": 42}, show_legend=False)
        st.plotly_chart(fig_box, width="stretch")

    with c4:
        render_chart_header(
            "نرخ ریزش بر حسب سنوات حضور مشتری در بانک (Tenure)",
            "تغییرات نرخ ریزش در طول ۰ تا ۱۰ سال سابقه همراهی مشتری با بانک",
        )
        ten_grp = (
            df.groupby("tenure", as_index=False)
            .agg(
                churn_rate_pct=("exited", lambda s: s.mean() * 100.0),
                customers=("customer_id", "count"),
            )
            .sort_values("tenure")
        )
        ten_grp["bar_text"] = ten_grp["churn_rate_pct"].apply(lambda v: svg_rtl(fmt_pct_fa(v, 1)))
        fig_ten = go.Figure(
            go.Scatter(
                x=ten_grp["tenure"],
                y=ten_grp["churn_rate_pct"],
                mode="lines+markers+text",
                text=ten_grp["bar_text"],
                textposition="top center",
                cliponaxis=False,
                line=dict(color=COLOR_PRIMARY, width=3),
                marker=dict(size=8.5, color=COLOR_ACCENT, line=dict(width=2, color=COLOR_PRIMARY)),
            )
        )
        fig_ten.update_layout(
            xaxis_title=svg_rtl("سنوات حضور مشتری (سال)"),
            yaxis_title=svg_rtl("نرخ ریزش (درصد)"),
            yaxis_range=[0, max(32.0, float(ten_grp["churn_rate_pct"].max()) * 1.25)],
        )
        style_fig(fig_ten, height=335, margin={"l": 52, "r": 42, "t": 26, "b": 42}, show_legend=False)
        st.plotly_chart(fig_ten, width="stretch")


def render_page_provinces_branches(df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div class="honesty-box">
            <b>یادداشت روش‌شناختی و صداقت تحلیلی (نگاشت جغرافیایی):</b>
            ستون <code>Geography</code> از دیتاست اروپایی منبع به‌صورت ۱:۱ به استان‌های ایران برچسب‌گذاری شده است
            (<b>فرانسه ← تهران</b> با ۵٬۰۱۴ مشتری، <b>آلمان ← اصفهان</b> با ۲٬۵۰۹ مشتری، <b>اسپانیا ← خراسان رضوی</b> با ۲٬۴۷۷ مشتری) تا توزیع‌های آماری دست‌نخورده بمانند.
            بنابراین نرخ ریزش <b>۳۲.۴۴٪</b> در «اصفهان» صرفاً ویژگی دادهٔ آلمان در دیتاست اصلی است و <b>نباید به اقتصاد واقعی استان اصفهان تعمیم داده شود.</b>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_kpi_row(df)
    if df.empty:
        return

    br_grp = (
        df.groupby(
            ["branch_id", "branch_name", "province", "source_geography", "branch_tier"],
            as_index=False,
        )
        .agg(
            customers=("customer_id", "count"),
            churned=("exited", "sum"),
            churn_rate_pct=("exited", lambda s: s.mean() * 100.0),
            total_balance_b_irr=("balance_irr", lambda s: s.sum() / 1e9),
            avg_balance_b_irr=("balance_irr", lambda s: s.mean() / 1e9),
            active_share_pct=("is_active_member", lambda s: s.mean() * 100.0),
        )
        .sort_values("total_balance_b_irr", ascending=True)
    )

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        render_chart_header(
            "حجم مانده سپرده‌ها به تفکیک شعب هفت‌گانه بانک آریا",
            "مقایسه مانده کل سپرده‌ها (میلیارد ریال نمایشی) در شعب تهران، اصفهان و مشهد",
        )
        br_grp["y_label"] = br_grp["branch_name"].apply(svg_rtl)
        br_grp["bal_text"] = br_grp["total_balance_b_irr"].apply(
            lambda v: svg_rtl(f"{to_fa(f'{v:,.0f}')} میلیارد")
        )
        fig_br_bal = go.Figure(
            go.Bar(
                x=br_grp["total_balance_b_irr"],
                y=br_grp["y_label"],
                orientation="h",
                text=br_grp["bal_text"],
                textposition="outside",
                cliponaxis=False,
                marker_color=COLOR_PRIMARY,
            )
        )
        fig_br_bal.update_layout(
            xaxis_title=svg_rtl("مانده کل سپرده‌ها (میلیارد ریال نمایشی)"),
            yaxis_title="",
            xaxis_range=[0, float(br_grp["total_balance_b_irr"].max()) * 1.3],
        )
        style_fig(
            fig_br_bal,
            height=350,
            margin={"l": 155, "r": 100, "t": 18, "b": 42},
            show_legend=False,
        )
        st.plotly_chart(fig_br_bal, width="stretch")

    with c2:
        render_chart_header(
            "نرخ ریزش مشتریان در شعب هفت‌گانه بانک آریا",
            "شعب چهارباغ و نقش‌جهان اصفهان به دلیل نگاشت از داده آلمان نرخ ریزش ~۳۲٪ را نشان می‌دهند",
        )
        br_churn = br_grp.sort_values("churn_rate_pct", ascending=True).copy()
        br_churn["y_label"] = br_churn["branch_name"].apply(svg_rtl)
        br_churn["ch_text"] = br_churn["churn_rate_pct"].apply(
            lambda v: svg_rtl(fmt_pct_fa(v, 2))
        )
        fig_br_ch = go.Figure(
            go.Bar(
                x=br_churn["churn_rate_pct"],
                y=br_churn["y_label"],
                orientation="h",
                text=br_churn["ch_text"],
                textposition="outside",
                cliponaxis=False,
                marker_color=[
                    COLOR_CHURN if v > 25 else COLOR_ACCENT for v in br_churn["churn_rate_pct"]
                ],
            )
        )
        fig_br_ch.update_layout(
            xaxis_title=svg_rtl("نرخ ریزش مشتریان (درصد)"),
            yaxis_title="",
            xaxis_range=[0, max(43.0, float(br_churn["churn_rate_pct"].max()) * 1.28)],
        )
        style_fig(
            fig_br_ch,
            height=350,
            margin={"l": 155, "r": 85, "t": 18, "b": 42},
            show_legend=False,
        )
        st.plotly_chart(fig_br_ch, width="stretch")

    st.markdown("#### جدول کارنامه عملکرد شعب هفت‌گانه (اسنپ‌شات ۲۹ اسفند ۱۴۰۳)")
    display_br = br_grp.sort_values("branch_id").copy()
    tbl_br = pd.DataFrame(
        {
            "کد شعبه": display_br["branch_id"],
            "نام شعبه": display_br["branch_name"],
            "استان": display_br["province"],
            "کشور منبع": display_br["source_geography"].apply(lambda g: GEO_FA_MAP.get(g, g)),
            "درجه شعبه": display_br["branch_tier"],
            "تعداد کل مشتریان": display_br["customers"].apply(fmt_int_fa),
            "مشتریان ریزش‌کرده": display_br["churned"].apply(fmt_int_fa),
            "نرخ ریزش": display_br["churn_rate_pct"].apply(lambda v: fmt_pct_fa(v, 2)),
            "سهم اعضای فعال": display_br["active_share_pct"].apply(lambda v: fmt_pct_fa(v, 1)),
            "مانده کل (میلیارد ریال نمایشی)": display_br["total_balance_b_irr"].apply(
                lambda v: to_fa(f"{v:,.1f}")
            ),
        }
    )
    render_rtl_html_table(tbl_br)


def render_page_product_portfolio(df: pd.DataFrame, holdings_df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div class="honesty-box">
            <b>شفافیت مهندسی داده (سبد محصولات):</b>
            تعداد محصولات هر مشتری (<code>NumOfProducts</code> از ۱ تا ۴ محصول، مجموعاً <b>۱۵٬۳۰۲</b> فقره) عیناً از منبع اصلی حفظ شده است.
            جدول <code>fact_product_holding</code> با <code>seed</code> ثابت از روی تعداد محصولات مشتری مشتق شده تا تحلیل ستاره‌ای چند-فکتی و ارتباط با جدول <code>dim_product</code> را نمایش دهد.
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_kpi_row(df)
    if df.empty:
        return

    filtered_cids = set(df["customer_id"].unique())
    h_sub = holdings_df[holdings_df["customer_id"].isin(filtered_cids)].copy()

    c1, c2 = st.columns(2, gap="medium")
    with c1:
        render_chart_header(
            "مقایسه مشتریان وفادار و ریزش‌کرده بر حسب تعداد محصول",
            "مشتریان ۲ محصولی بیشترین وفاداری (۹۲.۴۲٪ ماندگاری) را در کل پورتفولیو ثبت کرده‌اند",
        )
        p_summary = (
            df.groupby("num_of_products", as_index=False)
            .agg(
                customers=("customer_id", "count"),
                churned=("exited", "sum"),
                retained=("exited", lambda s: int((s == 0).sum())),
                churn_rate_pct=("exited", lambda s: s.mean() * 100.0),
                avg_balance_b_irr=("balance_irr", lambda s: s.mean() / 1e9),
            )
            .sort_values("num_of_products")
        )
        p_summary["label_plain"] = p_summary["num_of_products"].apply(
            lambda n: f"سبد {to_fa(n)} محصولی"
        )
        p_summary["x_label"] = p_summary["label_plain"].apply(svg_rtl)

        fig_p_stack = go.Figure()
        fig_p_stack.add_trace(
            go.Bar(
                x=p_summary["x_label"],
                y=p_summary["retained"],
                name=svg_rtl("مشتریان مانده"),
                marker_color=COLOR_PRIMARY,
                text=p_summary["retained"].apply(lambda v: svg_rtl(fmt_int_fa(v))),
                textposition="outside",
                cliponaxis=False,
            )
        )
        fig_p_stack.add_trace(
            go.Bar(
                x=p_summary["x_label"],
                y=p_summary["churned"],
                name=svg_rtl("مشتریان ریزش‌کرده"),
                marker_color=COLOR_CHURN,
                text=p_summary["churned"].apply(lambda v: svg_rtl(fmt_int_fa(v))),
                textposition="outside",
                cliponaxis=False,
            )
        )
        fig_p_stack.update_layout(
            barmode="group",
            xaxis_title=svg_rtl("تعداد محصولات در سبد مشتری"),
            yaxis_title=svg_rtl("تعداد مشتریان"),
            yaxis_range=[0, float(p_summary[["retained", "churned"]].max().max()) * 1.25],
        )
        style_fig(fig_p_stack, height=350, margin={"l": 56, "r": 36, "t": 34, "b": 42})
        st.plotly_chart(fig_p_stack, width="stretch")

    with c2:
        render_chart_header(
            "توزیع کل محصولات نگهداری‌شده بر اساس نوع محصول بانکی",
            "تفکیک ۱۵٬۳۰۲ فقره محصول مشتق‌شده در ۴ گروه محصولی بین مشتریان فعال و ریزش‌کرده",
        )
        cat_grp = (
            h_sub.groupby(["product_name", "holding_status"], as_index=False)
            .agg(holdings_count=("holding_id", "count"))
        )
        cat_grp["y_label"] = cat_grp["product_name"].apply(svg_rtl)
        cat_grp["status_rtl"] = cat_grp["holding_status"].apply(svg_rtl)
        cat_grp["bar_text"] = cat_grp["holdings_count"].apply(lambda v: svg_rtl(fmt_int_fa(v)))

        fig_cat = px.bar(
            cat_grp,
            x="holdings_count",
            y="y_label",
            color="status_rtl",
            orientation="h",
            barmode="group",
            text="bar_text",
            color_discrete_map={
                svg_rtl("فعال"): COLOR_PRIMARY,
                svg_rtl("بسته/ریزش"): COLOR_CHURN,
            },
            labels={
                "holdings_count": svg_rtl("تعداد فقره محصول"),
                "y_label": "",
                "status_rtl": "",
            },
        )
        fig_cat.update_traces(textposition="outside", cliponaxis=False)
        fig_cat.update_layout(
            xaxis_range=[0, float(cat_grp["holdings_count"].max()) * 1.3 if not cat_grp.empty else 100]
        )
        style_fig(fig_cat, height=350, margin={"l": 205, "r": 85, "t": 34, "b": 42})
        st.plotly_chart(fig_cat, width="stretch")

    st.markdown("#### خلاصه شاخص‌های ماندگاری و مانده سپرده بر اساس عمق رابطه محصولی")
    tbl_prod = pd.DataFrame(
        {
            "ترکیب سبد محصول": p_summary["label_plain"],
            "تعداد کل مشتریان": p_summary["customers"].apply(fmt_int_fa),
            "مشتریان مانده (وفادار)": p_summary["retained"].apply(fmt_int_fa),
            "مشتریان ریزش‌کرده": p_summary["churned"].apply(fmt_int_fa),
            "نرخ ریزش": p_summary["churn_rate_pct"].apply(lambda v: fmt_pct_fa(v, 2)),
            "میانگین مانده سرانه (میلیارد ریال نمایشی)": p_summary["avg_balance_b_irr"].apply(
                lambda v: to_fa(f"{v:,.2f}")
            ),
        }
    )
    render_rtl_html_table(tbl_prod)


def render_page_customer_search(df: pd.DataFrame, holdings_df: pd.DataFrame) -> None:
    render_kpi_row(df)
    if df.empty:
        return

    col_s1, col_s2, col_s3 = st.columns([2, 1, 1], gap="medium")
    with col_s1:
        search_query = st.text_input(
            "جستجوی مشتری (شناسه مشتری، نام فارسی یا نام خانوادگی منبع):",
            value="",
            placeholder="نمونه: 15634602 یا آرش یا Hargrave",
            key="cust_search_q",
        )
    with col_s2:
        churn_filter = st.selectbox(
            "فیلتر وضعیت ماندگاری:",
            options=["همه مشتریان", "فقط ریزش‌کرده", "فقط مانده (وفادار)"],
            key="cust_churn_filter",
        )
    with col_s3:
        sort_by = st.selectbox(
            "ترتیب نمایش:",
            options=[
                "مانده سپرده (نزولی)",
                "امتیاز اعتباری (نزولی)",
                "سنوات حضور (نزولی)",
                "شناسه مشتری",
            ],
            key="cust_sort_by",
        )

    res = df.copy()
    if search_query.strip():
        q = search_query.strip()
        mask = (
            res["customer_id"].astype(str).str.contains(q, case=False, na=False)
            | res["full_name_fa"].astype(str).str.contains(q, case=False, na=False)
            | res["original_surname"].astype(str).str.contains(q, case=False, na=False)
        )
        res = res[mask]

    if churn_filter == "فقط ریزش‌کرده":
        res = res[res["exited"] == 1]
    elif churn_filter == "فقط مانده (وفادار)":
        res = res[res["exited"] == 0]

    if sort_by == "مانده سپرده (نزولی)":
        res = res.sort_values("balance_irr", ascending=False)
    elif sort_by == "امتیاز اعتباری (نزولی)":
        res = res.sort_values("credit_score", ascending=False)
    elif sort_by == "سنوات حضور (نزولی)":
        res = res.sort_values("tenure", ascending=False)
    else:
        res = res.sort_values("customer_id", ascending=True)

    st.markdown(
        f"**تعداد مشتریان منطبق با جستجو:** `{fmt_int_fa(len(res))}` نفر (نمایش ۱۰۰ ردیف اول)"
    )

    top_res = res.head(100)
    if not top_res.empty:
        selected_cid = st.selectbox(
            "انتخاب پرونده مشتری برای مشاهده نمای ۳۶۰ درجه:",
            options=top_res["customer_id"].tolist(),
            format_func=lambda cid: (
                f"شناسه {to_fa(cid)} — {top_res.loc[top_res['customer_id'] == cid, 'full_name_fa'].iloc[0]} "
                f"({top_res.loc[top_res['customer_id'] == cid, 'branch_name'].iloc[0]})"
            ),
            key="selected_customer_360",
        )

        cust_row = top_res[top_res["customer_id"] == selected_cid].iloc[0]
        cust_holdings = holdings_df[holdings_df["customer_id"] == selected_cid]
        badge_cls = "churn" if cust_row["exited"] == 1 else "ok"

        st.markdown(
            f"""
            <div class="section-card">
                <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #e5eee9;padding-bottom:0.6rem;margin-bottom:0.75rem;">
                    <div>
                        <span style="font-size:1.08rem;font-weight:700;color:{COLOR_PRIMARY_DARK};">
                            پرونده ۳۶۰ درجه مشتری: {cust_row['full_name_fa']}
                        </span>
                        <span style="font-size:0.82rem;color:{COLOR_MUTED};margin-right:0.6rem;">
                            (شناسه یکتا: {to_fa(cust_row['customer_id'])} | نام منبع: {cust_row['original_surname']})
                        </span>
                    </div>
                    <span class="status-badge {badge_cls}">{cust_row['churn_status_label']}</span>
                </div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.8rem;font-size:0.84rem;">
                    <div><b>شعبه و استان:</b><br>{cust_row['branch_name']} ({cust_row['province']})</div>
                    <div><b>جنسیت و رده سنی:</b><br>{cust_row['gender']} — {fmt_int_fa(cust_row['age'])} ساله ({cust_row['age_group']})</div>
                    <div><b>تاریخ عضویت و سابقه:</b><br>{to_fa(cust_row['acquisition_jalali'])} ({fmt_int_fa(cust_row['tenure'])} سال)</div>
                    <div><b>امتیاز اعتباری:</b><br>{fmt_int_fa(cust_row['credit_score'])} ({cust_row['credit_band']})</div>
                    <div><b>مانده سپرده (نمایشی):</b><br>{fmt_int_fa(cust_row['balance_irr'])} ریال</div>
                    <div><b>حقوق تخمینی (نمایشی):</b><br>{fmt_int_fa(cust_row['estimated_salary_irr'])} ریال</div>
                    <div><b>تعداد محصولات سبد:</b><br>{fmt_int_fa(cust_row['num_of_products'])} محصول ({cust_row['has_credit_card_label']})</div>
                    <div><b>وضعیت تعامل:</b><br>{cust_row['activity_status_label']}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if not cust_holdings.empty:
            st.markdown("##### فهرست محصولات نگهداری‌شده در سبد این مشتری (مشتق از NumOfProducts)")
            h_tbl = pd.DataFrame(
                {
                    "ردیف": cust_holdings["product_sequence"].apply(fmt_int_fa),
                    "کد محصول": cust_holdings["product_id"],
                    "عنوان محصول بانکی": cust_holdings["product_name"],
                    "طبقه محصول": cust_holdings["product_category"],
                    "تاریخ بازگشایی (نمایشی)": cust_holdings["opened_date_jalali"].apply(to_fa),
                    "مانده تخصیص‌یافته (ریال نمایشی)": cust_holdings["allocated_balance_irr"].apply(
                        fmt_int_fa
                    ),
                    "وضعیت نگهداری": cust_holdings["holding_status"],
                }
            )
            render_rtl_html_table(h_tbl)

    st.markdown("#### فهرست مشتریان منطبق با فیلترها (۵۰ ردیف اول)")
    top_50 = top_res.head(50)
    tbl_cust = pd.DataFrame(
        {
            "شناسه مشتری": top_50["customer_id"].apply(to_fa),
            "نام کامل (ساختگی)": top_50["full_name_fa"],
            "استان": top_50["province"],
            "شعبه": top_50["branch_name"],
            "سن": top_50["age"].apply(fmt_int_fa),
            "سابقه (سال)": top_50["tenure"].apply(fmt_int_fa),
            "امتیاز اعتباری": top_50["credit_score"].apply(fmt_int_fa),
            "تعداد محصول": top_50["num_of_products"].apply(fmt_int_fa),
            "وضعیت فعالیت": top_50["activity_status_label"],
            "وضعیت ماندگاری": top_50["churn_status_label"],
            "مانده سپرده (ریال نمایشی)": top_50["balance_irr"].apply(fmt_int_fa),
        }
    )
    render_rtl_html_table(tbl_cust)


def main() -> None:
    st.set_page_config(
        page_title="بانک آریا | سامانه نمای ۳۶۰ درجه مشتری و تحلیل ریزش",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_rtl_css()

    data = load_data()
    df_360 = data["df_360"]
    holdings_enriched = data["holdings_enriched"]

    # سایدبار سمت راست — ناوبری و فیلترهای سراسری
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-title">🏦 بانک آریا</div>
                <div class="sidebar-brand-sub">معاونت برنامه‌ریزی و هوش تجاری | نمای ۳۶۰° مشتری</div>
            </div>
            <div class="sidebar-section-label">بخش‌های تحلیلی گزارش</div>
            """,
            unsafe_allow_html=True,
        )

        selected_page = st.radio(
            "انتخاب صفحه گزارش:",
            options=PAGES,
            index=0,
            key="page_nav",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="sidebar-section-label">فیلترهای سراسری پورتفولیو</div>',
            unsafe_allow_html=True,
        )

        all_provinces = sorted(df_360["province"].unique().tolist())
        sel_provinces = st.multiselect(
            "استان (نگاشت ۱:۱ منبع):",
            options=all_provinces,
            default=all_provinces,
            key="filter_province",
        )

        age_order = ["زیر ۳۰ سال", "۳۰ تا ۳۹ سال", "۴۰ تا ۴۹ سال", "۵۰ تا ۵۹ سال", "۶۰ سال به بالا"]
        avail_ages = [a for a in age_order if a in df_360["age_group"].unique()]
        sel_ages = st.multiselect(
            "رده سنی مشتریان:",
            options=avail_ages,
            default=avail_ages,
            format_func=lambda s: s.replace(" سال به بالا", "+").replace(" سال", ""),
            key="filter_age_group",
        )

        all_prods = sorted(df_360["num_of_products"].unique().tolist())
        sel_prods = st.multiselect(
            "تعداد محصول در سبد:",
            options=all_prods,
            default=all_prods,
            format_func=lambda x: f"{to_fa(x)} محصول",
            key="filter_num_products",
        )

        all_acts = sorted(df_360["activity_status_label"].unique().tolist())
        sel_acts = st.multiselect(
            "وضعیت تعامل و فعالیت:",
            options=all_acts,
            default=all_acts,
            key="filter_activity",
        )

        st.markdown(
            """
            <div class="sidebar-section-label">شناسنامه و صداقت داده</div>
            <div style="font-size:0.74rem;color:#4f665d;line-height:1.6;direction:rtl;text-align:right;">
                • <b>منبع داده:</b> دیتاست عمومی <code>Churn_Modelling.csv</code><br>
                • <b>مقیاس ریالی:</b> ضرب نمایشی <code>×۲۵۰٬۰۰۰</code><br>
                • <b>نگاشت استان:</b> فرانسه←تهران، آلمان←اصفهان، اسپانیا←خراسان رضوی<br>
                • <b>ماهیت:</b> نام بانک، شعب و افراد کاملاً ساختگی است.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # اعمال فیلترها
    filtered_df = df_360[
        df_360["province"].isin(sel_provinces)
        & df_360["age_group"].isin(sel_ages)
        & df_360["num_of_products"].isin(sel_prods)
        & df_360["activity_status_label"].isin(sel_acts)
    ].copy()

    page_descriptions = {
        "نمای کلی": "پایش کلان شاخص‌های ماندگاری، توزیع سپرده‌ها، الگوی تعدد محصول و ترکیب سنی مشتریان",
        "تحلیل ریزش مشتری": "بررسی عوامل کلیدی خروج مشتریان بر اساس سن، جنسیت، طبقه اعتباری، مانده سپرده و سابقه حضور",
        "استان‌ها و شعب": "مقایسه کارنامه عملکرد ۷ شعبه بانک آریا در ۳ استان به همراه شفاف‌سازی نگاشت جغرافیایی منبع",
        "سبد محصولات": "تحلیل فروش متقاطع (Cross-Sell)، نگهداشت چندمحصولی و ترکیب ۱۵٬۳۰۲ فقره محصول بانکی",
        "جستجوی مشتریان": "جستجوی آنی و مشاهده پرونده ۳۶۰ درجه تک‌تک مشتریان و محصولات نگهداری‌شده",
    }

    # نوار سربرگ مدیریتی راست‌چین
    st.markdown(
        f"""
        <div class="top-masthead">
            <div class="masthead-right">
                <div class="masthead-breadcrumb">سامانه هوش تجاری بانک آریا ◂ مدیریت ارتباط با مشتری ◂ {selected_page}</div>
                <div class="masthead-title">نمای ۳۶۰ درجه مشتری و تحلیل ریزش — {selected_page}</div>
                <p class="masthead-desc">{page_descriptions.get(selected_page, "")}</p>
            </div>
            <div class="masthead-meta">
                <div class="meta-row">
                    <div class="meta-pill">تاریخ مرجع: <b>۲۹ اسفند ۱۴۰۳</b></div>
                    <div class="meta-pill">جامعه فعلی: <b>{fmt_int_fa(len(filtered_df))} از {fmt_int_fa(len(df_360))} مشتری</b></div>
                    <div class="meta-pill">پوشش: <b>۷ شعبه (۳ استان)</b></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if selected_page == "نمای کلی":
        render_page_overview(filtered_df)
    elif selected_page == "تحلیل ریزش مشتری":
        render_page_churn_analysis(filtered_df)
    elif selected_page == "استان‌ها و شعب":
        render_page_provinces_branches(filtered_df)
    elif selected_page == "سبد محصولات":
        render_page_product_portfolio(filtered_df, holdings_enriched)
    elif selected_page == "جستجوی مشتریان":
        render_page_customer_search(filtered_df, holdings_enriched)


if __name__ == "__main__":
    main()
