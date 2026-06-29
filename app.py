import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

st.set_page_config(
    page_title="StockScope",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>

    /* ═══════════════════════════════════════════════════════
       SIDEBAR — fully hidden; controls live on main page
    ═══════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        display: none !important;
        width: 0 !important;
        min-width: 0 !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }

    /* ═══════════════════════════════════════════════════════
       BASE LAYOUT
    ═══════════════════════════════════════════════════════ */
    [data-testid="stAppViewContainer"] {
        background-color: #111111;
        color: #F5F5F5;
    }
    [data-testid="stAppViewContainer"] > .main > .block-container {
        padding-top: 0;
        padding-bottom: 4rem;
        max-width: 1400px;
    }

    /* ── Streamlit top chrome ── */
    [data-testid="stHeader"] {
        background-color: #111111 !important;
        border-bottom: none !important;
    }
    [data-testid="stToolbar"] {
        background-color: #111111 !important;
    }
    [data-testid="stDecoration"] {
        background-image: linear-gradient(to right, #D4AF37, #F5C542) !important;
        height: 2px !important;
    }
    [data-testid="stHeader"] button svg {
        fill: #444444 !important;
    }
    [data-testid="stHeader"] button:hover svg {
        fill: #888888 !important;
    }

    /* ═══════════════════════════════════════════════════════
       MAIN CONTENT TEXT — scoped to semantic nodes only
    ═══════════════════════════════════════════════════════ */
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] li,
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3 {
        color: #F5F5F5;
    }

    /* ═══════════════════════════════════════════════════════
       PRODUCT BAR
    ═══════════════════════════════════════════════════════ */
    .product-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.9rem 0 0.9rem 0;
        border-bottom: 1px solid #1C1C1C;
        margin-bottom: 3rem;
    }
    .product-bar-left {
        display: flex;
        align-items: center;
        gap: 0.55rem;
    }
    .product-mark {
        color: #D4AF37;
        font-size: 0.8rem;
        line-height: 1;
    }
    .product-name {
        color: #F5F5F5;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.22em;
    }
    .product-divider {
        color: #2A2A2A;
        font-size: 0.9rem;
        margin: 0 0.15rem;
    }
    .product-status {
        color: #888888;
        font-size: 0.68rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .product-nav {
        display: flex;
        gap: 2.2rem;
        align-items: center;
    }
    .product-nav span {
        color: #9A9A9A;
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        cursor: default;
        transition: color 0.15s;
    }
    .product-nav span:hover {
        color: #E0E0E0;
    }

    /* ═══════════════════════════════════════════════════════
       HERO — LEFT COLUMN
    ═══════════════════════════════════════════════════════ */
    .hero-eyebrow {
        color: #D4AF37;
        font-size: 0.62rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        margin: 0 0 1.1rem 0;
    }
    .hero-headline {
        color: #F5F5F5;
        font-size: clamp(1.9rem, 3.5vw, 2.9rem);
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.015em;
        margin: 0 0 1.2rem 0;
    }
    .hero-gold {
        color: #D4AF37;
    }
    .hero-copy {
        color: #9A9A9A;
        font-size: clamp(0.82rem, 1.3vw, 0.95rem);
        line-height: 1.75;
        max-width: 400px;
        margin: 0 0 2.2rem 0;
    }

    /* ═══════════════════════════════════════════════════════
       CONTROLS PANEL  ("BUILD YOUR COMPARISON")
    ═══════════════════════════════════════════════════════ */
    .controls-label {
        color: #888888;
        font-size: 0.6rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        padding-bottom: 0.65rem;
        border-bottom: 1px solid #1C1C1C;
        margin-bottom: 0.9rem;
    }

    /* ═══════════════════════════════════════════════════════
       HERO — RIGHT COLUMN  (race chart area)
    ═══════════════════════════════════════════════════════ */
    .race-period {
        color: #888888;
        font-size: 0.6rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin: 0 0 0.3rem 0;
    }
    .hero-placeholder {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        height: 100%;
        min-height: 260px;
        padding: 2rem 1.5rem;
        border: 1px dashed #222222;
        border-radius: 12px;
        margin-top: 1rem;
    }
    .hero-placeholder-label {
        color: #888888;
        font-size: 0.62rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        margin: 0 0 0.6rem 0;
    }
    .hero-placeholder-text {
        color: #888888;
        font-size: 0.88rem;
        line-height: 1.6;
        margin: 0;
    }

    /* ═══════════════════════════════════════════════════════
       MARKET PULSE STRIP
    ═══════════════════════════════════════════════════════ */
    .pulse-strip {
        display: flex;
        flex-wrap: wrap;
        background-color: #0C0C0C;
        border-top: 1px solid #181818;
        border-bottom: 1px solid #181818;
        margin: 2.5rem 0 0 0;
    }
    .pulse-item {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.7rem 1.6rem 0.7rem 1.3rem;
        border-right: 1px solid #181818;
    }
    .pulse-ticker {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        color: #9A9A9A;
    }
    .pulse-val {
        font-size: 0.82rem;
        font-weight: 600;
        color: #B8B8B8;
    }
    .pulse-arrow {
        font-size: 0.72rem;
        color: #B8B8B8;
    }
    .pulse-best-v {
        color: #F5C542 !important;
    }
    .pulse-neg-v {
        color: #A05050 !important;
    }

    /* ═══════════════════════════════════════════════════════
       TAB NAVIGATION — editorial text style
    ═══════════════════════════════════════════════════════ */
    [data-testid="stTabs"] [role="tablist"] {
        border-bottom: 1px solid #1C1C1C;
        gap: 0;
        margin-bottom: 0;
    }
    [data-testid="stTabs"] button[role="tab"] {
        background-color: transparent !important;
        color: #9A9A9A !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        padding: 0.65rem 1.4rem !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        border-radius: 0 !important;
        transition: color 0.15s ease, border-color 0.15s ease !important;
    }
    [data-testid="stTabs"] button[role="tab"]:hover {
        color: #E0E0E0 !important;
        border-bottom-color: #666666 !important;
        background-color: transparent !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: #D4AF37 !important;
        border-bottom: 2px solid #D4AF37 !important;
        background-color: transparent !important;
    }
    [data-testid="stTabContent"] {
        padding-top: 2rem;
    }

    /* ═══════════════════════════════════════════════════════
       OVERVIEW — EDITORIAL SUMMARY
    ═══════════════════════════════════════════════════════ */
    .summary-block {
        display: flex;
        gap: 3rem;
        align-items: flex-start;
        padding: 0 0 2rem 0;
        border-bottom: 1px solid #1A1A1A;
        margin-bottom: 3rem;
        flex-wrap: wrap;
    }
    .summary-left {
        min-width: 140px;
    }
    .summary-sm-label {
        color: #8F8F8F;
        font-size: 0.6rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin: 0 0 0.4rem 0;
    }
    .summary-large-val {
        color: #F5C542;
        font-size: 4rem;
        font-weight: 900;
        line-height: 1;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .summary-right {
        display: flex;
        flex-direction: column;
        gap: 0.55rem;
        padding-top: 0.25rem;
    }
    .stat-row {
        display: flex;
        gap: 1.2rem;
        align-items: baseline;
    }
    .stat-key {
        color: #8F8F8F;
        font-size: 0.6rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        min-width: 58px;
    }
    .stat-val {
        color: #C8C8C8;
        font-size: 0.82rem;
    }
    .stat-val-gold {
        color: #D4AF37;
        font-size: 0.82rem;
        font-weight: 600;
    }

    /* ═══════════════════════════════════════════════════════
       CHART SECTION HEADER
    ═══════════════════════════════════════════════════════ */
    .chart-hdr {
        display: flex;
        align-items: flex-start;
        gap: 1rem;
        margin-bottom: 1.2rem;
    }
    .sec-num {
        color: #2A2A2A;
        font-size: 2.8rem;
        font-weight: 900;
        line-height: 1;
        letter-spacing: -0.03em;
        margin-top: -0.2rem;
        user-select: none;
        flex-shrink: 0;
    }
    .chart-sec-title {
        color: #C0C0C0;
        font-size: 1rem;
        font-weight: 700;
        margin: 0 0 0.25rem 0;
        letter-spacing: -0.01em;
    }
    .chart-sec-desc {
        color: #888888;
        font-size: 0.78rem;
        margin: 0;
        line-height: 1.5;
    }

    /* ═══════════════════════════════════════════════════════
       BEST PERFORMER — st.metric editorial override
       delta_color="off" gives grey; CSS promotes to gold.
       Arrow SVG hidden — ± prefix in the string is enough.
    ═══════════════════════════════════════════════════════ */
    [data-testid="stMetric"] {
        background-color: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
    }
    [data-testid="stMetric"]:hover {
        transform: none !important;
        border-color: transparent !important;
        box-shadow: none !important;
    }
    [data-testid="stMetricLabel"] > div {
        color: #888888 !important;
        font-size: 0.58rem !important;
        letter-spacing: 0.22em !important;
        text-transform: uppercase !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] > div {
        color: #F5F5F5 !important;
        font-size: clamp(2rem, 3.5vw, 3.2rem) !important;
        font-weight: 900 !important;
        letter-spacing: -0.02em !important;
        line-height: 1 !important;
    }
    [data-testid="stMetricDelta"] > div {
        color: #F5C542 !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricDelta"] svg {
        display: none !important;
    }
    [data-testid="stMetric"] [data-testid="stTooltipHoverTarget"] svg {
        fill: #555555 !important;
    }
    [data-testid="stMetric"] [data-testid="stTooltipHoverTarget"]:hover svg {
        fill: #C0C0C0 !important;
    }

    /* ── Best performer supporting text ── */
    .bp-divider {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        padding: 2rem 0 1.8rem 0;
    }
    .bp-divider-line {
        flex: 1;
        height: 1px;
        background-color: #1A1A1A;
    }
    .bp-divider-label {
        color: #555555;
        font-size: 0.58rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        white-space: nowrap;
    }
    .bp-subtitle {
        color: #9A9A9A;
        font-size: 0.9rem;
        font-weight: 500;
        line-height: 1.45;
        margin: 0.4rem 0 0.55rem 0;
    }
    .bp-period {
        color: #D4AF37;
        font-size: 0.65rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin: 0 0 1rem 0;
    }
    .bp-clarification {
        color: #888888;
        font-size: 0.78rem;
        line-height: 1.65;
        margin: 0 0 0.45rem 0;
    }
    .bp-disclaimer {
        color: #888888;
        font-size: 0.7rem;
        font-style: italic;
        margin: 0;
    }

    /* ═══════════════════════════════════════════════════════
       EDITORIAL PLACEHOLDERS (What If? / Insights)
    ═══════════════════════════════════════════════════════ */
    .editorial-ph {
        padding: 2rem 0 3rem 0;
        max-width: 560px;
    }
    .editorial-coming {
        display: inline-block;
        color: #111111;
        background-color: #D4AF37;
        font-size: 0.58rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        padding: 0.18rem 0.55rem;
        border-radius: 3px;
        margin: 0 0 1.2rem 0;
    }
    .editorial-ph-title {
        color: #F5F5F5;
        font-size: clamp(1.2rem, 2.5vw, 1.7rem);
        font-weight: 800;
        line-height: 1.15;
        letter-spacing: -0.015em;
        margin: 0 0 0.9rem 0;
    }
    .editorial-ph-desc {
        color: #888888;
        font-size: 0.88rem;
        line-height: 1.7;
        margin: 0;
    }

    /* ═══════════════════════════════════════════════════════
       DIVIDERS & CAPTIONS
    ═══════════════════════════════════════════════════════ */
    hr {
        border-color: #1A1A1A !important;
        margin: 1.5rem 0 !important;
    }
    [data-testid="stCaptionContainer"] p {
        color: #888888 !important;
        font-size: 0.72rem;
    }

    /* ═══════════════════════════════════════════════════════
       INFO / WARNING BOXES
    ═══════════════════════════════════════════════════════ */
    [data-testid="stAlert"] {
        background-color: #161616 !important;
        border: 1px solid #222222 !important;
        border-left: 3px solid #D4AF37 !important;
        border-radius: 6px !important;
    }
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span {
        color: #8A8A8A !important;
    }
    [data-testid="stAlert"] svg {
        fill: #D4AF37 !important;
    }

    /* ═══════════════════════════════════════════════════════
       DATE INPUT
    ═══════════════════════════════════════════════════════ */
    [data-testid="stDateInput"] label p {
        color: #C8C8C8 !important;
        font-size: 0.78rem;
    }
    [data-testid="stDateInput"] [data-baseweb="input"] {
        background-color: #161616 !important;
        border: 1px solid #444444 !important;
        border-radius: 6px !important;
    }
    [data-testid="stDateInput"] [data-baseweb="input"]:focus-within {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 0 1px #D4AF37 !important;
    }
    [data-testid="stDateInput"] [data-baseweb="input"]:hover {
        border-color: #444444 !important;
    }
    [data-testid="stDateInput"] input {
        color: #C0C0C0 !important;
        background-color: transparent !important;
        caret-color: #D4AF37;
    }
    [data-testid="stDateInput"] input::placeholder {
        color: #666666 !important;
    }
    [data-testid="stDateInput"] [data-baseweb="input"] svg {
        fill: #555555 !important;
    }
    [data-testid="stDateInput"] [data-baseweb="input"] button {
        color: #555555 !important;
        background-color: transparent !important;
        border: none !important;
    }
    [data-testid="stDateInput"] [data-baseweb="input"] button:hover svg {
        fill: #D4AF37 !important;
    }

    /* ═══════════════════════════════════════════════════════
       CALENDAR POPOVER
    ═══════════════════════════════════════════════════════ */
    [data-baseweb="popover"] {
        background-color: #1A1A1A !important;
        border: 1px solid #333333 !important;
        border-radius: 10px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.7) !important;
    }
    [data-baseweb="calendar"] {
        background-color: #1A1A1A !important;
        color: #F5F5F5 !important;
    }
    [data-baseweb="calendar"] div,
    [data-baseweb="calendar"] span,
    [data-baseweb="calendar"] p,
    [data-baseweb="calendar"] abbr,
    [data-baseweb="calendar"] button {
        color: #F5F5F5 !important;
        background-color: transparent !important;
    }
    [data-baseweb="calendar"] [role="heading"],
    [data-baseweb="calendar"] [aria-live="polite"],
    [data-baseweb="calendar"] [aria-live="polite"] * {
        color: #F5F5F5 !important;
        font-weight: 600 !important;
        background-color: transparent !important;
    }
    [data-baseweb="calendar"] button {
        border: none !important;
        border-radius: 4px !important;
    }
    [data-baseweb="calendar"] button:hover {
        background-color: #2A2A2A !important;
    }
    [data-baseweb="calendar"] button svg,
    [data-baseweb="calendar"] button path {
        fill: #D4AF37 !important;
    }
    [data-baseweb="calendar"] select {
        background-color: #222222 !important;
        color: #F5F5F5 !important;
        border: 1px solid #333333 !important;
        border-radius: 4px !important;
    }
    [data-baseweb="calendar"] select option {
        background-color: #1A1A1A !important;
        color: #F5F5F5 !important;
    }
    [data-baseweb="calendar"] [role="columnheader"],
    [data-baseweb="calendar"] [role="columnheader"] * {
        color: #555555 !important;
        background-color: transparent !important;
    }
    [data-baseweb="calendar"] [role="grid"],
    [data-baseweb="calendar"] [role="row"],
    [data-baseweb="calendar"] [role="gridcell"] {
        background-color: transparent !important;
    }
    [data-baseweb="calendar"] [role="gridcell"] > *,
    [data-baseweb="calendar"] [role="button"] {
        border-radius: 50% !important;
    }
    [data-baseweb="calendar"] [role="gridcell"] *,
    [data-baseweb="calendar"] [role="button"] * {
        color: #F5F5F5 !important;
        background-color: transparent !important;
    }
    [data-baseweb="calendar"] [role="gridcell"]:hover > *,
    [data-baseweb="calendar"] [role="button"]:hover {
        background-color: #2A2A2A !important;
        outline: 1px solid #D4AF37 !important;
    }
    [data-baseweb="calendar"] [role="button"]:hover *,
    [data-baseweb="calendar"] [role="gridcell"]:hover * {
        color: #FFFFFF !important;
        background-color: transparent !important;
    }
    [data-baseweb="calendar"] [aria-selected="true"] > *,
    [data-baseweb="calendar"] [aria-selected="true"] [role="button"],
    [data-baseweb="calendar"] [aria-selected="true"] button {
        background-color: #D4AF37 !important;
        border-radius: 50% !important;
        outline: none !important;
    }
    [data-baseweb="calendar"] [aria-selected="true"] [role="button"] *,
    [data-baseweb="calendar"] [aria-selected="true"] button *,
    [data-baseweb="calendar"] [aria-selected="true"] [role="button"],
    [data-baseweb="calendar"] [aria-selected="true"] button {
        color: #111111 !important;
        font-weight: 700 !important;
    }
    [data-baseweb="calendar"] [data-baseweb="calendar-day-range-highlighted"] > *,
    [data-baseweb="calendar"] [data-is-range-selected] > * {
        background-color: rgba(212,175,55,0.15) !important;
    }
    [data-baseweb="calendar"] [aria-current="date"] [role="button"],
    [data-baseweb="calendar"] [aria-current="date"] > *:first-child {
        outline: 1px solid #D4AF37 !important;
        border-radius: 50% !important;
    }
    [data-baseweb="calendar"] [aria-current="date"] *:not([aria-selected="true"] *) {
        color: #F5C542 !important;
    }
    [data-baseweb="calendar"] [aria-disabled="true"] {
        opacity: 0.3 !important;
        cursor: not-allowed !important;
    }
    [data-baseweb="calendar"] [aria-disabled="true"] * {
        color: #555555 !important;
        cursor: not-allowed !important;
    }
    [data-baseweb="datepicker"] [data-baseweb="input"],
    [data-baseweb="datepicker"] [data-baseweb="base-input"] {
        background-color: #222222 !important;
        border: 1px solid #333333 !important;
        border-radius: 6px !important;
    }
    [data-baseweb="datepicker"] [data-baseweb="input"]:focus-within {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 0 1px #D4AF37 !important;
    }
    [data-baseweb="datepicker"] input {
        background-color: transparent !important;
        color: #F5F5F5 !important;
    }
    [data-baseweb="datepicker"] input::placeholder {
        color: #888888 !important;
    }
    [data-baseweb="datepicker"] [data-baseweb="input"] svg,
    [data-baseweb="datepicker"] [data-baseweb="input"] path {
        fill: #D4AF37 !important;
    }
    [data-baseweb="datepicker"] label,
    [data-baseweb="datepicker"] label * {
        color: #888888 !important;
    }

    /* ═══════════════════════════════════════════════════════
       RADIO — GROUP LABEL plain text / OPTIONS pill buttons
    ═══════════════════════════════════════════════════════ */
    [data-testid="stRadio"] [data-testid="stWidgetLabel"],
    [data-testid="stRadio"] [data-testid="stWidgetLabel"] label {
        display: block !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 0 0 0.4rem 0 !important;
        cursor: default !important;
        color: #C8C8C8 !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        transition: none !important;
    }
    [data-testid="stRadio"] [data-testid="stWidgetLabel"]:hover,
    [data-testid="stRadio"] [data-testid="stWidgetLabel"] label:hover {
        background-color: transparent !important;
        border-color: transparent !important;
        color: #C8C8C8 !important;
    }
    [data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {
        display: none !important;
    }
    [data-testid="stRadio"] label:has(input[type="radio"]) {
        display: inline-flex !important;
        align-items: center !important;
        background-color: #161616 !important;
        border: 1px solid #444444 !important;
        border-radius: 5px !important;
        padding: 0.38rem 0.85rem !important;
        cursor: pointer !important;
        margin-right: 0.35rem !important;
        transition: background-color 0.15s ease, border-color 0.15s ease !important;
    }
    [data-testid="stRadio"] label:has(input[type="radio"]) p,
    [data-testid="stRadio"] label:has(input[type="radio"]) span {
        color: #AFAFAF !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stRadio"] label:has(input[type="radio"]):hover {
        background-color: #1E1E1E !important;
        border-color: #888888 !important;
    }
    [data-testid="stRadio"] label:has(input[type="radio"]):hover p,
    [data-testid="stRadio"] label:has(input[type="radio"]):hover span {
        color: #E0E0E0 !important;
    }
    [data-testid="stRadio"] label:has(input[type="radio"]:checked) {
        background-color: #D4AF37 !important;
        border-color: #D4AF37 !important;
    }
    [data-testid="stRadio"] label:has(input[type="radio"]:checked) p,
    [data-testid="stRadio"] label:has(input[type="radio"]:checked) span {
        color: #111111 !important;
        font-weight: 700 !important;
    }
    [data-testid="stRadio"] label:has(input[type="radio"]:focus-visible) {
        outline: 2px solid #F5C542 !important;
        outline-offset: 2px;
    }

    /* ═══════════════════════════════════════════════════════
       MULTISELECT
    ═══════════════════════════════════════════════════════ */
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        background-color: #161616 !important;
        border: 1px solid #444444 !important;
        border-radius: 6px !important;
    }
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 0 1px #D4AF37 !important;
    }
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div:hover {
        border-color: #444444 !important;
    }
    [data-testid="stMultiSelect"] input {
        color: #C0C0C0 !important;
        background-color: transparent !important;
        caret-color: #D4AF37;
    }
    [data-testid="stMultiSelect"] input::placeholder {
        color: #666666 !important;
    }
    [data-testid="stMultiSelect"] [data-testid="stWidgetLabel"] p {
        color: #C8C8C8 !important;
        font-size: 0.78rem !important;
    }
    [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
        background-color: #D4AF37 !important;
        color: #111111 !important;
    }
    [data-testid="stMultiSelect"] [data-baseweb="tag"] button svg {
        fill: #111111 !important;
    }
    [data-testid="stMultiSelect"] [data-baseweb="select"] svg {
        fill: #888888 !important;
    }
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within svg {
        fill: #D4AF37 !important;
    }

    /* ═══════════════════════════════════════════════════════
       DROPDOWN OPTION LIST
    ═══════════════════════════════════════════════════════ */
    [data-baseweb="menu"] {
        background-color: #181818 !important;
        border: 1px solid #2A2A2A !important;
        border-radius: 8px !important;
        box-shadow: 0 6px 24px rgba(0,0,0,0.6) !important;
    }
    [data-baseweb="menu"] li {
        background-color: #181818 !important;
        color: #B8B8B8 !important;
    }
    [data-baseweb="menu"] li:hover,
    [data-baseweb="menu"] [aria-selected="true"] {
        background-color: #222222 !important;
        color: #F5C542 !important;
    }
    [data-baseweb="menu"] [aria-selected="true"] svg {
        fill: #D4AF37 !important;
    }

    /* ═══════════════════════════════════════════════════════
       FORM — strip default Streamlit border / background
    ═══════════════════════════════════════════════════════ */
    [data-testid="stForm"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }

    /* ═══════════════════════════════════════════════════════
       NUMBER INPUT
    ═══════════════════════════════════════════════════════ */
    [data-testid="stNumberInput"] [data-testid="stWidgetLabel"] p {
        color: #C8C8C8 !important;
        font-size: 0.78rem !important;
    }
    [data-testid="stNumberInput"] [data-baseweb="input"] {
        background-color: #161616 !important;
        border: 1px solid #444444 !important;
        border-radius: 6px !important;
    }
    [data-testid="stNumberInput"] [data-baseweb="input"]:focus-within {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 0 1px #D4AF37 !important;
    }
    [data-testid="stNumberInput"] [data-baseweb="input"]:hover {
        border-color: #444444 !important;
    }
    [data-testid="stNumberInput"] input {
        color: #C0C0C0 !important;
        background-color: transparent !important;
        caret-color: #D4AF37;
    }
    [data-testid="stNumberInput"] button {
        background-color: transparent !important;
        color: #888888 !important;
        border: none !important;
    }
    [data-testid="stNumberInput"] button svg {
        fill: #888888 !important;
    }
    [data-testid="stNumberInput"] button:hover svg {
        fill: #D4AF37 !important;
    }

    /* ═══════════════════════════════════════════════════════
       SELECTBOX
    ═══════════════════════════════════════════════════════ */
    [data-testid="stSelectbox"] [data-testid="stWidgetLabel"] p {
        color: #C8C8C8 !important;
        font-size: 0.78rem !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #161616 !important;
        border: 1px solid #444444 !important;
        border-radius: 6px !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 0 1px #D4AF37 !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
        border-color: #444444 !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] svg {
        fill: #888888 !important;
    }
    [data-testid="stSelectbox"] input {
        color: #C0C0C0 !important;
        background-color: transparent !important;
    }
    /* Selected value text inside the box */
    [data-testid="stSelectbox"] [data-baseweb="select"] [class*="valueContainer"] {
        color: #C0C0C0 !important;
    }

    /* ═══════════════════════════════════════════════════════
       FORM SUBMIT BUTTON — gold, dark text
    ═══════════════════════════════════════════════════════ */
    [data-testid="stFormSubmitButton"] button {
        background-color: #D4AF37 !important;
        color: #111111 !important;
        border: 1px solid #D4AF37 !important;
        font-weight: 700 !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.08em !important;
        border-radius: 6px !important;
        padding: 0.55rem 1.5rem !important;
        transition: background-color 0.15s ease !important;
        width: 100% !important;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background-color: #F5C542 !important;
        border-color: #F5C542 !important;
        color: #111111 !important;
    }
    [data-testid="stFormSubmitButton"] button:focus-visible {
        outline: 2px solid #F5C542 !important;
        outline-offset: 3px;
    }

    /* ═══════════════════════════════════════════════════════
       CALCULATOR — layout & typography
    ═══════════════════════════════════════════════════════ */
    .calc-eyebrow {
        color: #D4AF37;
        font-size: 0.6rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        margin: 0 0 0.5rem 0;
    }
    .calc-title {
        color: #F5F5F5;
        font-size: clamp(1.3rem, 2.5vw, 1.9rem);
        font-weight: 800;
        letter-spacing: -0.015em;
        line-height: 1.1;
        margin: 0 0 0.7rem 0;
    }
    .calc-intro {
        color: #9A9A9A;
        font-size: 0.85rem;
        line-height: 1.65;
        max-width: 520px;
        margin: 0 0 1.8rem 0;
    }
    .calc-result-period {
        color: #8A8A8A;
        font-size: 0.6rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        margin: 0 0 0.5rem 0;
    }
    .calc-result-ticker {
        color: #F5F5F5;
        font-size: clamp(2.2rem, 4vw, 3.5rem);
        font-weight: 900;
        letter-spacing: -0.025em;
        line-height: 1;
        margin: 0 0 0.25rem 0;
    }
    .calc-result-value {
        color: #F5C542;
        font-size: clamp(1.4rem, 2.5vw, 2rem);
        font-weight: 800;
        letter-spacing: -0.01em;
        line-height: 1;
        margin: 0 0 1rem 0;
    }
    .calc-rows {
        border-top: 1px solid #2D2D2D;
    }
    .calc-row {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        padding: 0.5rem 0;
        border-bottom: 1px solid #2D2D2D;
    }
    .calc-label {
        color: #B8B8B8;
        font-size: 0.78rem;
    }
    .calc-value {
        color: #C0C0C0;
        font-size: 0.85rem;
        font-weight: 500;
        text-align: right;
    }
    .calc-portfolio-big {
        margin: 0 0 1rem 0;
        padding-bottom: 1rem;
        border-bottom: 1px solid #2D2D2D;
    }
    .calc-portfolio-label {
        color: #B8B8B8;
        font-size: 0.6rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin: 0 0 0.3rem 0;
    }
    .calc-portfolio-value {
        color: #F5C542;
        font-size: clamp(2rem, 3vw, 2.8rem);
        font-weight: 900;
        letter-spacing: -0.02em;
        line-height: 1;
        margin: 0 0 0.25rem 0;
    }
    .calc-portfolio-return {
        font-size: 0.95rem;
        font-weight: 600;
        margin: 0;
    }
    .calc-note {
        color: #9A9A9A;
        font-size: 0.72rem;
        font-style: italic;
        margin: 0.5rem 0 0.8rem 0;
    }
    .calc-stale-notice {
        color: #9A9A9A;
        font-size: 0.7rem;
        font-style: italic;
        margin-bottom: 0.8rem;
    }
    .calc-disclaimer {
        color: #7A7A7A;
        font-size: 0.68rem;
        line-height: 1.65;
        font-style: italic;
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid #282828;
    }
    .calc-empty {
        color: #8A8A8A;
        font-size: 0.82rem;
        line-height: 1.7;
        padding: 2.5rem 1.5rem;
        border: 1px dashed #333333;
        border-radius: 8px;
        text-align: center;
        margin-top: 0.5rem;
    }
    .calc-empty strong {
        color: #9A9A9A;
    }

    /* ═══════════════════════════════════════════════════════
       INSIGHTS — section layout & typography
    ═══════════════════════════════════════════════════════ */
    .ins-eyebrow {
        color: #D4AF37;
        font-size: 0.6rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        margin: 0 0 0.5rem 0;
    }
    .ins-title {
        color: #F5F5F5;
        font-size: clamp(1.3rem, 2.5vw, 1.9rem);
        font-weight: 800;
        letter-spacing: -0.015em;
        line-height: 1.1;
        margin: 0 0 0.7rem 0;
    }
    .ins-intro {
        color: #9A9A9A;
        font-size: 0.85rem;
        line-height: 1.65;
        max-width: 560px;
        margin: 0 0 2rem 0;
    }
    .ins-block {
        border-top: 1px solid #1A1A1A;
        padding-top: 1.2rem;
        padding-bottom: 1rem;
    }
    .ins-block--spaced {
        margin-top: 1.8rem;
    }
    .ins-num {
        display: inline-block;
        color: #D4AF37;
        font-size: 0.58rem;
        font-weight: 700;
        letter-spacing: 0.2em;
        border-bottom: 1px solid #D4AF37;
        padding-bottom: 0.1rem;
        margin-bottom: 0.5rem;
    }
    .ins-block-label {
        color: #8F8F8F;
        font-size: 0.62rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 0.2rem 0 0.6rem 0;
    }
    .ins-lead-ticker {
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 900;
        letter-spacing: -0.03em;
        line-height: 1;
        margin: 0 0 0.2rem 0;
    }
    .ins-lead-stat {
        font-size: clamp(1.5rem, 3vw, 2.4rem);
        font-weight: 800;
        letter-spacing: -0.02em;
        line-height: 1;
        margin: 0 0 0.9rem 0;
    }
    .ins-body {
        color: #9A9A9A;
        font-size: 0.83rem;
        line-height: 1.65;
        margin: 0;
        max-width: 360px;
    }
    .ins-fact-section {
        margin-top: 2.5rem;
        padding: 1.5rem 0;
        border-top: 1px solid #1A1A1A;
        border-bottom: 1px solid #1A1A1A;
    }
    .ins-fact-eyebrow {
        display: block;
        color: #888888;
        font-size: 0.58rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }
    .ins-fact-title {
        color: #F5F5F5;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        margin: 0 0 0.6rem 0;
    }
    .ins-fact-body {
        color: #C0C0C0;
        font-size: 0.88rem;
        line-height: 1.7;
        max-width: 620px;
        margin: 0 0 0.8rem 0;
        font-style: italic;
    }
    .ins-fact-source {
        color: #888888;
        font-size: 0.7rem;
        margin: 0;
    }
    .ins-fact-link {
        color: #9A9A9A;
        text-decoration: underline;
        text-underline-offset: 2px;
        text-decoration-color: #555555;
    }
    .ins-fact-link:hover {
        color: #D4AF37;
        text-decoration-color: #D4AF37;
    }
    .ins-how-section {
        margin-top: 2rem;
        padding-bottom: 1rem;
    }
    .ins-how-title {
        color: #888888;
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 0 0 0.8rem 0;
    }
    .ins-how-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .ins-how-item {
        color: #8A8A8A;
        font-size: 0.78rem;
        line-height: 1.65;
        padding: 0.4rem 0 0.4rem 1.2rem;
        border-bottom: 1px solid #161616;
        position: relative;
    }
    .ins-how-item::before {
        content: "—";
        position: absolute;
        left: 0;
        color: #555555;
    }

    /* ═══════════════════════════════════════════════════════
       RECENT MARKET SNAPSHOT — yfinance section
    ═══════════════════════════════════════════════════════ */
    .mkt-section {
        margin: 3rem 0 0 0;
        padding: 2rem 1.5rem 1.5rem 1.5rem;
        border-top: 2px solid #D4AF37;
        background-color: #0C0C0C;
        border-radius: 0 0 6px 6px;
    }
    .mkt-eyebrow {
        color: #D4AF37;
        font-size: 0.6rem;
        letter-spacing: 0.22em;
        text-transform: uppercase;
        margin: 0 0 0.5rem 0;
    }
    .mkt-title {
        color: #FFFFFF;
        font-size: clamp(1.3rem, 2.5vw, 1.9rem);
        font-weight: 800;
        letter-spacing: -0.015em;
        line-height: 1.1;
        margin: 0 0 0.5rem 0;
    }
    .mkt-desc {
        color: #AAAAAA;
        font-size: 0.82rem;
        line-height: 1.6;
        margin: 0 0 0.4rem 0;
        max-width: 540px;
    }
    .mkt-sep-note {
        color: #8A8A8A;
        font-size: 0.68rem;
        font-style: italic;
        margin: 0;
        line-height: 1.7;
    }
    .mkt-source {
        color: #888888;
        font-size: 0.68rem;
        font-style: italic;
        margin: 0.8rem 0 0 0;
    }
    .mkt-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 0;
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid #222222;
    }
    .mkt-item {
        flex: 0 0 auto;
        min-width: 160px;
        padding: 0.8rem 2.5rem 0.8rem 0;
        margin-bottom: 1rem;
        border-right: 1px solid #1E1E1E;
        margin-right: 2.5rem;
    }
    .mkt-item:last-child {
        border-right: none;
    }
    .mkt-ticker {
        display: block;
        color: #D4AF37;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 0.6rem;
    }
    .mkt-yf-note {
        color: #888888;
        font-size: 0.58rem;
        font-style: italic;
        margin: -0.3rem 0 0.5rem 0;
    }
    .mkt-price {
        color: #FFFFFF;
        font-size: 1.6rem;
        font-weight: 900;
        letter-spacing: -0.025em;
        line-height: 1;
        margin: 0 0 0.35rem 0;
    }
    .mkt-change-pos {
        color: #3DCC3D;
        font-size: 0.85rem;
        font-weight: 700;
        margin: 0 0 0.35rem 0;
    }
    .mkt-change-neg {
        color: #E05555;
        font-size: 0.85rem;
        font-weight: 700;
        margin: 0 0 0.35rem 0;
    }
    .mkt-change-flat {
        color: #AAAAAA;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0 0 0.35rem 0;
    }
    .mkt-date {
        color: #8A8A8A;
        font-size: 0.65rem;
        margin: 0;
    }
    .mkt-unavail {
        color: #8A8A8A;
        font-size: 0.82rem;
        line-height: 1.65;
        padding: 0.8rem 0;
        font-style: italic;
    }

    /* ═══════════════════════════════════════════════════════
       ONBOARDING — shown when no stock is selected yet
    ═══════════════════════════════════════════════════════ */
    .onboard-block {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem 2rem;
        text-align: center;
        border: 1px dashed #3A3A3A;
        border-radius: 8px;
        margin: 2rem 0;
    }
    .onboard-eyebrow {
        font-size: 0.65rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #D4AF37;
        margin: 0 0 0.75rem;
    }
    .onboard-headline {
        font-size: 1.3rem;
        font-weight: 700;
        color: #F5F5F5;
        margin: 0 0 0.5rem;
    }
    .onboard-body {
        font-size: 0.9rem;
        color: #888888;
        max-width: 440px;
        margin: 0;
        line-height: 1.6;
    }

    /* ═══════════════════════════════════════════════════════
       RESPONSIVE — stack hero on narrow screens
    ═══════════════════════════════════════════════════════ */
    @media (max-width: 768px) {
        .hero-headline {
            font-size: 1.7rem;
        }
        .product-nav {
            display: none;
        }
        .summary-block {
            flex-direction: column;
            gap: 1.5rem;
        }
        .mkt-strip {
            flex-wrap: wrap;
            gap: 1rem;
        }
        .mkt-item {
            min-width: 140px;
            flex: 1 1 140px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = px.data.stocks()
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


df = load_data()
tickers = [col for col in df.columns if col != "date"]
dataset_min = df["date"].min().date()
dataset_max = df["date"].max().date()

CHART_COLORS = ["#F5C542", "#E8E8E8", "#C98B2E", "#9FA8B3", "#FFF1A8", "#D4AF37"]
RACE_COLORS  = ["#F5C542", "#F28C28", "#D4AF37", "#B8B8B8", "#9FA8B3", "#FFF1B8"]


def _apply_chart_theme(fig: go.Figure, height: int = 420, margin: dict | None = None) -> go.Figure:
    """Apply a consistent dark editorial theme to any Plotly figure."""
    m = margin or dict(l=65, r=25, t=15, b=60)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111111",
        font=dict(color="#C8C8C8", family="sans-serif", size=11),
        legend=dict(
            title_text="",
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(color="#BFC3C7", size=11),
            orientation="h",
            y=-0.22,
            x=0,
            itemgap=14,
        ),
        xaxis=dict(
            title="",
            tickfont=dict(color="#9FA3A8", size=10),
            gridcolor="rgba(255,255,255,0.08)",
            linecolor="rgba(255,255,255,0.1)",
            zeroline=True,
            zerolinecolor="rgba(212,175,55,0.35)",
            zerolinewidth=1,
        ),
        yaxis=dict(
            tickfont=dict(color="#9FA3A8", size=10),
            title_font=dict(color="#AEB3B8", size=10),
            gridcolor="rgba(255,255,255,0.08)",
            linecolor="rgba(255,255,255,0.1)",
            zeroline=True,
            zerolinecolor="rgba(212,175,55,0.35)",
            zerolinewidth=1,
        ),
        margin=m,
        height=height,
    )
    return fig

# Verified via Fetch MCP on 2026-06-28 from the official Google company-history page.
# Tool: mcp__fetch__fetch  URL: https://about.google/our-story/
# The page states: "from Google's initial server (made of Lego)" and describes Larry Page
# and Sergey Brin working "from their dorm rooms" at Stanford before moving to a garage.
FETCH_FACT = {
    "company":      "Google",
    "fact":         (
        "Google’s very first web server — built by Larry Page and Sergey Brin "
        "while they were students at Stanford — was assembled from Lego bricks "
        "to hold the hard drives together."
    ),
    "source_title": "Our Story — Google",
    "source_url":   "https://about.google/our-story/",
}


# Maps Plotly dataset tickers to current yfinance tickers.
# FB was renamed META in 2022; all others are unchanged.
# Used only for the recent-market snapshot — never for historical calculations.
YFINANCE_TICKER_MAP = {
    "AAPL": "AAPL",
    "AMZN": "AMZN",
    "FB":   "META",
    "GOOG": "GOOG",
    "MSFT": "MSFT",
    "NFLX": "NFLX",
}


@st.cache_data(ttl=1800, show_spinner=False)
def load_latest_market_data(tickers: tuple) -> dict:
    """
    Fetches up to 5 trading days of daily closes from yfinance for each
    selected Plotly-dataset ticker.  Returns a dict mapping each Plotly
    ticker to its computed market-close stats.  Tickers that fail are
    silently omitted so the rest of the section degrades gracefully.
    Cache TTL: 30 minutes.
    """
    result = {}
    for plotly_ticker in tickers:
        yf_ticker = YFINANCE_TICKER_MAP.get(plotly_ticker, plotly_ticker)
        try:
            hist = yf.Ticker(yf_ticker).history(period="5d", auto_adjust=True)
            hist = hist.dropna(subset=["Close"])
            if len(hist) < 2:
                continue
            latest_close = float(hist["Close"].iloc[-1])
            prev_close   = float(hist["Close"].iloc[-2])
            if prev_close == 0 or not (
                math.isfinite(latest_close) and math.isfinite(prev_close)
            ):
                continue
            daily_change     = latest_close - prev_close
            daily_change_pct = (daily_change / prev_close) * 100
            idx = hist.index[-1]
            latest_date = idx.date() if hasattr(idx, "date") else str(idx)[:10]
            result[plotly_ticker] = {
                "yf_ticker":  yf_ticker,
                "close":      latest_close,
                "prev_close": prev_close,
                "change":     daily_change,
                "change_pct": daily_change_pct,
                "date":       latest_date,
            }
        except Exception:
            pass  # degrade gracefully — failed ticker is omitted from result
    return result


# ── Shared formatting utilities ───────────────────────────────────────────────
# Defined once at module level; used by the calculator, insights, and market
# sections so the same logic is not redefined on every Streamlit rerun.

def _fmt_usd(v: float) -> str:
    return f"${v:,.2f}"

def _fmt_signed_usd(v: float) -> str:
    return f"+${v:,.2f}" if v >= 0 else f"-${abs(v):,.2f}"

def _fmt_pct(v: float, decimals: int = 1) -> str:
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.{decimals}f}%"

def _fmt_abs_pct(v: float) -> str:
    return f"{abs(v):.1f}%"

def _pnl_color(v: float) -> str:
    return "#F5C542" if v >= 0 else "#A05050"

def _growth_verb(v: float) -> str:
    if v > 0:   return "increased by"
    elif v < 0: return "declined by"
    return "was unchanged at"

def _fmt_date(d) -> str:
    if hasattr(d, "day"):
        return f"{d.day} {d.strftime('%b %Y')}"
    return str(d)


# ── Race chart ────────────────────────────────────────────────────────────────
# Accepts the module-level `growths` dict so there is a single source of truth.
# Sorting and visualisation happen here; growth values are computed once upstream.
def build_race_chart(growths: dict[str, float], selected: list) -> go.Figure:
    if not growths:
        return go.Figure()
    sorted_s = sorted(selected, key=lambda t: growths.get(t, 0), reverse=True)
    vals = list(growths.values())
    x_max = max(max(vals) * 1.1 + 20, 20)
    x_min = min(min(vals) * 1.1 - 5, -8)

    fig = go.Figure()

    for i, t in enumerate(sorted_s):
        g = growths[t]
        color = RACE_COLORS[i % len(RACE_COLORS)]

        # Track background
        fig.add_trace(go.Scatter(
            x=[x_min, x_max], y=[t, t],
            mode="lines",
            line=dict(color="#181818", width=22),
            showlegend=False, hoverinfo="skip",
        ))

        # Progress bar
        fig.add_trace(go.Scatter(
            x=[0, g], y=[t, t],
            mode="lines",
            line=dict(color=color, width=4),
            showlegend=False, hoverinfo="skip",
        ))

        # Endpoint dot
        fig.add_trace(go.Scatter(
            x=[g], y=[t],
            mode="markers",
            marker=dict(size=16, color=color, line=dict(width=2, color="rgba(17,17,17,0.9)")),
            showlegend=False,
            hovertemplate=f"<b>{t}</b><br>{g:+.1f}%<extra></extra>",
        ))

        # Growth annotation
        fig.add_annotation(
            x=g, y=t,
            text=f"<b>{g:+.1f}%</b>",
            showarrow=False,
            xanchor="left" if g >= 0 else "right",
            xshift=13 if g >= 0 else -13,
            font=dict(color=color, size=11, family="sans-serif"),
        )

    fig.add_vline(x=0, line_width=1, line_color="#222222")

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title=dict(
            text="▸  THE BIG TECH RACE",
            font=dict(color="#666666", size=9, family="sans-serif"),
            x=0, y=0.99, xanchor="left",
        ),
        margin=dict(l=10, r=90, t=28, b=5),
        height=max(190, len(sorted_s) * 70 + 55),
        xaxis=dict(
            showgrid=True, gridcolor="rgba(255,255,255,0.07)", zeroline=False,
            tickfont=dict(color="#9FA3A8", size=8),
            ticksuffix="%", range=[x_min, x_max], fixedrange=True,
        ),
        yaxis=dict(
            showgrid=False, tickfont=dict(color="#BFC3C7", size=11),
            ticklen=0, fixedrange=True,
            categoryorder="array",
            categoryarray=list(reversed(sorted_s)),
        ),
        hovermode="closest", showlegend=False,
    )
    return fig


# ── Product bar ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="product-bar">
      <div class="product-bar-left">
        <span class="product-mark">◆</span>
        <span class="product-name">STOCKSCOPE</span>
        <span class="product-divider">|</span>
        <span class="product-status">Historical Big Tech Explorer</span>
      </div>
      <div class="product-nav">
        <span>Explore</span>
        <span>Scenarios</span>
        <span>Insights</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Hero — two-column layout ──────────────────────────────────────────────────
hero_left, hero_right = st.columns([5, 7], gap="large")

with hero_left:
    st.markdown(
        """
        <p class="hero-eyebrow">BIG TECH PERFORMANCE, MADE CLEAR</p>
        <h1 class="hero-headline">See which tech leaders<br>
          <span class="hero-gold">actually won.</span>
        </h1>
        <p class="hero-copy">Compare the historical growth of the world's biggest
        technology companies, change the time period and explore what the numbers mean.</p>
        <p class="controls-label">BUILD YOUR COMPARISON</p>
        """,
        unsafe_allow_html=True,
    )

    default_selections = [t for t in ["AAPL", "MSFT", "GOOG"] if t in tickers]
    selected = st.multiselect(
        "Choose companies",
        options=tickers,
        default=default_selections,
        placeholder="Choose companies…",
    )

    date_col, mode_col = st.columns([3, 2])
    with date_col:
        date_range = st.date_input(
            "Analysis period",
            value=(dataset_min, dataset_max),
            min_value=dataset_min,
            max_value=dataset_max,
            format="DD/MM/YYYY",
        )
    with mode_col:
        display_mode = st.radio(
            "Display mode",
            options=["Growth %", "Indexed"],
            index=0,
            horizontal=True,
        )

    if display_mode is None:
        display_mode = "Growth %"

    st.caption(
        "Values represent relative performance since the selected start date, "
        "not actual share prices."
    )

# ── Validate & prepare data (between column fills) ────────────────────────────
data_ready = False
filtered_df = None
chart_data = None
start_date = end_date = None
period_label = ""
growths: dict[str, float] = {}

if selected:
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        s, e = date_range
        if s < e:
            s_ts, e_ts = pd.Timestamp(s), pd.Timestamp(e)
            temp = df[(df["date"] >= s_ts) & (df["date"] <= e_ts)].reset_index(drop=True)
            if len(temp) >= 2:
                filtered_df = temp
                start_date, end_date = s, e
                period_label = f"{s.strftime('%b %Y')} – {e.strftime('%b %Y')}"

                # Build chart data
                chart_data = filtered_df[["date"]].copy()
                use_growth = (display_mode == "Growth %")
                for ticker in selected:
                    col_vals = filtered_df[ticker]
                    fv = col_vals.dropna()
                    if fv.empty or fv.iloc[0] == 0:
                        chart_data[ticker] = float("nan")
                        continue
                    first_val = fv.iloc[0]
                    chart_data[ticker] = (
                        ((col_vals / first_val) - 1) * 100
                        if use_growth
                        else (col_vals / first_val) * 100
                    )

                # Growth % for race / pulse (always % change)
                for ticker in selected:
                    col_vals = filtered_df[ticker].dropna()
                    if not col_vals.empty and col_vals.iloc[0] != 0:
                        growths[ticker] = ((col_vals.iloc[-1] / col_vals.iloc[0]) - 1) * 100
                    else:
                        growths[ticker] = 0.0

                data_ready = True

# ── Hero right column — race chart or placeholder ─────────────────────────────
with hero_right:
    if data_ready:
        st.markdown(
            f"<p class='race-period'>SELECTED PERIOD &nbsp;·&nbsp; {period_label}</p>",
            unsafe_allow_html=True,
        )
        race_fig = build_race_chart(growths, selected)
        st.plotly_chart(race_fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.markdown(
            """
            <div class="hero-placeholder">
              <p class="hero-placeholder-label">▸ THE BIG TECH RACE</p>
              <p class="hero-placeholder-text">
                Select companies and a date range in the panel to the left —
                their performance race will appear here.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Validation messages ───────────────────────────────────────────────────────
if not selected:
    st.markdown(
        '<div class="onboard-block">'
        '<p class="onboard-eyebrow">Getting started</p>'
        '<p class="onboard-headline">Select a company to begin</p>'
        '<p class="onboard-body">Use the <strong style="color:#D4AF37">Build your comparison</strong>'
        " panel on the left to choose one or more Big Tech companies."
        " Charts, metrics, and scenarios will appear here once you make a selection.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.stop()

if not data_ready:
    if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
        st.warning("Please select both a start and an end date to continue.")
    elif date_range[0] >= date_range[1]:
        st.warning("The start date must be before the end date.")
    else:
        st.warning(
            "The selected period does not contain enough data for a meaningful comparison."
        )
    st.stop()

# ── Market pulse strip ────────────────────────────────────────────────────────
best_ticker = max(growths, key=growths.get) if growths else None

pulse_html_items = ""
for ticker in selected:
    g = growths.get(ticker, 0.0)
    is_best = ticker == best_ticker
    is_neg = g < 0
    val_cls = "pulse-best-v" if is_best else ("pulse-neg-v" if is_neg else "")
    arrow = "↑" if g >= 0 else "↓"
    pulse_html_items += (
        f'<div class="pulse-item">'
        f'<span class="pulse-ticker">{ticker}</span>'
        f'<span class="pulse-val {val_cls}">{g:+.1f}%</span>'
        f'<span class="pulse-arrow {val_cls}">{arrow}</span>'
        f"</div>"
    )

st.markdown(
    f'<div class="pulse-strip">{pulse_html_items}</div>',
    unsafe_allow_html=True,
)

# ── Best performer featured insight ──────────────────────────────────────────
# Reuses the same `growths` dict that drives the race chart and pulse strip.
# One calculation — shared by the pulse strip, best-performer metric, and
# Insights tab.  No growth value is ever recalculated from the DataFrame.
best_growth        = growths.get(best_ticker, 0.0) if best_ticker else 0.0
worst_ticker       = min(growths, key=growths.get) if growths else None
worst_growth       = growths.get(worst_ticker, 0.0) if worst_ticker else 0.0
average_growth     = sum(growths.values()) / len(growths) if growths else 0.0
performance_spread = best_growth - worst_growth if growths else 0.0
selected_count     = len(growths)

st.markdown(
    """
    <div class="bp-divider">
      <div class="bp-divider-line"></div>
      <span class="bp-divider-label">Period standout</span>
      <div class="bp-divider-line"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

bp_metric_col, bp_text_col = st.columns([4, 8], gap="large")

with bp_metric_col:
    # st.metric — Context7 / Streamlit docs reference:
    #   label       → small accessible header; CSS promotes to uppercase gold
    #   value       → the winning ticker displayed large
    #   delta       → formatted growth string; delta_color="off" → neutral grey
    #                 overridden to gold via [data-testid="stMetricDelta"] CSS
    #   help        → tooltip shown next to the label (requires label_visibility="visible")
    st.metric(
        label="Highest growth",
        value=best_ticker,
        delta=f"{best_growth:+.1f}%",
        delta_color="off",
        help="The selected stock with the highest percentage growth during your chosen historical period.",
    )

with bp_text_col:
    st.markdown(
        f"""
        <div style="padding-top:0.6rem">
          <p class="bp-subtitle">Strongest historical growth among your selected stocks</p>
          <p class="bp-period">{period_label}</p>
          <p class="bp-clarification">
            This is the selected stock with the highest percentage growth
            between your chosen start and end dates.
          </p>
          <p class="bp-disclaimer">Historical performance does not predict future results.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Three lower sections ──────────────────────────────────────────────────────
st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

overview_tab, calculator_tab, insights_tab = st.tabs(
    ["01  Overview", "02  What If?", "03  Insights"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Overview
# ══════════════════════════════════════════════════════════════════════════════
with overview_tab:

    # Editorial summary — reuses module-level best_ticker/worst_ticker/best_growth/worst_growth
    # (no separate recalculation here).
    mode_label = "Growth percentage" if display_mode == "Growth %" else "Indexed performance"

    st.markdown(
        f"""
        <div class="summary-block">
          <div class="summary-left">
            <p class="summary-sm-label">Selected companies</p>
            <p class="summary-large-val">{len(selected)}</p>
          </div>
          <div class="summary-right">
            <div class="stat-row">
              <span class="stat-key">Period</span>
              <span class="stat-val">{period_label}</span>
            </div>
            <div class="stat-row">
              <span class="stat-key">Mode</span>
              <span class="stat-val">{mode_label}</span>
            </div>
            <div class="stat-row">
              <span class="stat-key">Highest</span>
              <span class="stat-val-gold">{best_ticker} &nbsp; {best_growth:+.1f}%</span>
            </div>
            <div class="stat-row">
              <span class="stat-key">Lowest</span>
              <span class="stat-val">{worst_ticker} &nbsp; {worst_growth:+.1f}%</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Chart section header
    if display_mode == "Growth %":
        y_axis_label  = "Growth (%)"
        y_tick_fmt    = ".1f"
        y_tick_suffix = "%"
        hover_fmt     = ".1f"
        chart_desc    = "Growth rebased to 0% at the start of the selected period."
    else:
        y_axis_label  = "Indexed performance"
        y_tick_fmt    = ".2f"
        y_tick_suffix = ""
        hover_fmt     = ".2f"
        chart_desc    = "Performance rebased to 100 at the start of the selected period."

    st.markdown(
        f"""
        <div class="chart-hdr">
          <span class="sec-num">01</span>
          <div>
            <p class="chart-sec-title">Performance through time</p>
            <p class="chart-sec-desc">{chart_desc}</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig = px.line(
        chart_data,
        x="date",
        y=selected,
        title="",
        labels={"date": "Date", "value": y_axis_label, "variable": "Stock"},
        color_discrete_sequence=CHART_COLORS[: len(selected)],
    )
    _apply_chart_theme(fig, height=420)
    fig.update_layout(
        yaxis=dict(
            title=y_axis_label,
            tickformat=y_tick_fmt,
            ticksuffix=y_tick_suffix,
        ),
        hovermode="x unified",
    )
    fig.update_traces(
        line=dict(width=2.5),
        hovertemplate=f"%{{y:{hover_fmt}}}{y_tick_suffix}<extra></extra>",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.caption(
        "Source: Plotly's built-in stocks dataset. "
        "Historical data for demonstration and educational use only."
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — What If?
# ══════════════════════════════════════════════════════════════════════════════
with calculator_tab:

    # ── Session state — persists results across tab switches / global reruns ──
    for _k, _v in {
        "wif_done": False,
        "wif_mode": "One stock",
        "wif_amount": 1_000.0,
        "wif_stock": selected[0] if selected else "",
        "wif_snap": {},
        "wif_period": "",
    }.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <p class="calc-eyebrow">HISTORICAL SCENARIO</p>
        <h2 class="calc-title">What if you had invested?</h2>
        <p class="calc-intro">
          Use the selected historical period to explore how a hypothetical
          investment would have changed based on each company's relative
          performance. This is an illustration — not an actual trading simulation.
        </p>
        """,
        unsafe_allow_html=True,
    )

    # ── Two-column layout ─────────────────────────────────────────────────────
    wif_form_col, wif_result_col = st.columns([5, 7], gap="large")

    # ── Form ──────────────────────────────────────────────────────────────────
    with wif_form_col:
        with st.form("calc_form"):
            calc_mode = st.radio(
                "Calculator mode",
                options=["One stock", "Compare all", "Split equally"],
                index=0,
                horizontal=True,
            )
            calc_amount = st.number_input(
                "Investment amount (USD)",
                min_value=0.01,
                max_value=10_000_000.0,
                value=1_000.0,
                step=100.0,
                format="%.2f",
                help="Enter the hypothetical amount you want to test.",
            )
            calc_stock = st.selectbox(
                "Company  —  used in One stock mode",
                options=selected,
            )
            submitted = st.form_submit_button(
                "Calculate scenario",
                use_container_width=True,
            )

        st.markdown(
            """
            <p class="calc-disclaimer">
              This is a historical illustration based on indexed performance
              data. It is not financial advice and does not include dividends,
              fees, taxes or currency effects.<br><br>
              The calculation applies the historical percentage change to the
              entered amount. It does not use actual historical share prices.
            </p>
            """,
            unsafe_allow_html=True,
        )

    # ── On submit — validate and snapshot ────────────────────────────────────
    if submitted:
        if calc_amount <= 0:
            with wif_result_col:
                st.warning("Enter an investment amount greater than zero.")
        elif not growths:
            with wif_result_col:
                st.warning(
                    "The selected historical period does not contain "
                    "enough information for this calculation."
                )
        else:
            st.session_state.wif_done = True
            st.session_state.wif_mode = calc_mode
            st.session_state.wif_amount = calc_amount
            st.session_state.wif_stock = calc_stock
            st.session_state.wif_snap = dict(growths)  # snapshot at submission
            st.session_state.wif_period = period_label

    # ── Results ───────────────────────────────────────────────────────────────
    with wif_result_col:
        if not st.session_state.wif_done:
            st.markdown(
                """
                <div class="calc-empty">
                  <p>Configure the scenario in the panel<br>
                  and press <strong>Calculate scenario</strong>.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Stale notice when global period changed since last calculation
            if st.session_state.wif_period != period_label:
                st.markdown(
                    "<p class='calc-stale-notice'>Period has changed — press "
                    "Calculate to update.</p>",
                    unsafe_allow_html=True,
                )

            s_mode   = st.session_state.wif_mode
            s_amount = st.session_state.wif_amount
            s_stock  = st.session_state.wif_stock
            s_snap   = st.session_state.wif_snap
            s_period = st.session_state.wif_period
            s_tickers = list(s_snap.keys())

            # ── MODE 1: One stock ─────────────────────────────────────────
            if s_mode == "One stock":
                if s_stock not in s_snap:
                    st.warning(
                        f"No growth data is available for {s_stock} in the "
                        "selected period."
                    )
                else:
                    g      = s_snap[s_stock]
                    ending = s_amount * (1 + g / 100)
                    profit = ending - s_amount
                    p_lbl  = "Profit" if profit >= 0 else "Loss"
                    c_pl   = _pnl_color(profit)
                    c_g    = _pnl_color(g)

                    st.markdown(
                        f"""
                        <p class="calc-result-period">{s_period.upper()}</p>
                        <p class="calc-result-ticker">{s_stock}</p>
                        <p class="calc-result-value">{_fmt_usd(ending)}</p>
                        <div class="calc-rows">
                          <div class="calc-row">
                            <span class="calc-label">Starting investment</span>
                            <span class="calc-value">{_fmt_usd(s_amount)}</span>
                          </div>
                          <div class="calc-row">
                            <span class="calc-label">Hypothetical ending value</span>
                            <span class="calc-value"
                              style="color:#D4AF37">{_fmt_usd(ending)}</span>
                          </div>
                          <div class="calc-row">
                            <span class="calc-label">{p_lbl}</span>
                            <span class="calc-value"
                              style="color:{c_pl}">{_fmt_signed_usd(profit)}</span>
                          </div>
                          <div class="calc-row">
                            <span class="calc-label">Historical return</span>
                            <span class="calc-value"
                              style="color:{c_g}">{_fmt_pct(g)}</span>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # ── MODE 2: Compare all ───────────────────────────────────────
            elif s_mode == "Compare all":
                rows = []
                for t in s_tickers:
                    g   = s_snap.get(t, 0.0)
                    end = s_amount * (1 + g / 100)
                    rows.append((t, end, end - s_amount, g))
                rows.sort(key=lambda x: x[1], reverse=True)
                best_t = rows[0][0] if rows else None

                rows_html = ""
                for i, (t, end, pl, g) in enumerate(rows):
                    is_best  = (t == best_t)
                    t_color  = "#F5C542" if is_best else "#888888"
                    t_weight = "700" if is_best else "400"
                    v_color  = _pnl_color(pl)
                    rows_html += (
                        f'<div class="calc-row">'
                        f'<span class="calc-label" style="color:{t_color};font-weight:{t_weight}">{t}</span>'
                        f'<span class="calc-value" style="text-align:right">'
                        f'<span style="color:#C0C0C0">{_fmt_usd(end)}</span>'
                        f'&nbsp;'
                        f'<span style="color:{v_color};font-size:0.75rem">{_fmt_pct(g)}</span>'
                        f'</span></div>'
                    )

                st.markdown(
                    f'<p class="calc-result-period">{s_period.upper()}</p>'
                    f'<p class="calc-note">{_fmt_usd(s_amount)} applied separately'
                    f' to each company — this is not a combined portfolio.</p>'
                    f'<div class="calc-rows">{rows_html}</div>',
                    unsafe_allow_html=True,
                )

            # ── MODE 3: Split equally ─────────────────────────────────────
            else:
                n_stocks  = len(s_tickers)
                if n_stocks == 0:
                    st.warning(
                        "Select at least one company before calculating "
                        "a scenario."
                    )
                else:
                    alloc      = s_amount / n_stocks
                    total_end  = 0.0
                    split_html = ""

                    for t in s_tickers:
                        g        = s_snap.get(t, 0.0)
                        end      = alloc * (1 + g / 100)
                        pl       = end - alloc
                        total_end += end
                        pl_color = _pnl_color(pl)
                        split_html += (
                            f'<div class="calc-row">'
                            f'<span class="calc-label">{t}</span>'
                            f'<span class="calc-value" style="text-align:right">'
                            f'<span style="color:#C0C0C0">{_fmt_usd(end)}</span>'
                            f'&nbsp;'
                            f'<span style="color:{pl_color};font-size:0.75rem">{_fmt_pct(g)}</span>'
                            f'</span></div>'
                        )

                    total_pl  = total_end - s_amount
                    total_pct = ((total_end / s_amount) - 1) * 100
                    port_col  = _pnl_color(total_pl)
                    coy_word  = "company" if n_stocks == 1 else "companies"

                    st.markdown(
                        f'<p class="calc-result-period">{s_period.upper()}</p>'
                        f'<div class="calc-portfolio-big">'
                        f'<p class="calc-portfolio-label">Combined portfolio value</p>'
                        f'<p class="calc-portfolio-value">{_fmt_usd(total_end)}</p>'
                        f'<p class="calc-portfolio-return" style="color:{port_col}">'
                        f'{_fmt_signed_usd(total_pl)} &nbsp; {_fmt_pct(total_pct)}'
                        f'</p></div>'
                        f'<p class="calc-note">{_fmt_usd(alloc)} allocated to each'
                        f' of {n_stocks} {coy_word}</p>'
                        f'<div class="calc-rows">'
                        f'<div class="calc-row">'
                        f'<span class="calc-label">Total starting portfolio</span>'
                        f'<span class="calc-value">{_fmt_usd(s_amount)}</span>'
                        f'</div>'
                        f'{split_html}'
                        f'<div class="calc-row">'
                        f'<span class="calc-label">Total profit / loss</span>'
                        f'<span class="calc-value" style="color:{port_col}">{_fmt_signed_usd(total_pl)}</span>'
                        f'</div></div>',
                        unsafe_allow_html=True,
                    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Insights
# ══════════════════════════════════════════════════════════════════════════════
with insights_tab:

    # ── Section header ────────────────────────────────────────────────────────
    st.markdown(
        """
        <p class="ins-eyebrow">PERFORMANCE INTERPRETATION</p>
        <h2 class="ins-title">What the selected period tells us</h2>
        <p class="ins-intro">
          StockScope turns the selected historical performance into a few simple
          observations. These insights describe the chosen period only and are
          not predictions.
        </p>
        """,
        unsafe_allow_html=True,
    )

    if not growths:
        st.markdown(
            '<p style="color:#333333;font-size:0.85rem">'
            "Select at least one company and a valid date range to see insights."
            "</p>",
            unsafe_allow_html=True,
        )
    else:
        # ── Build insight sentences ───────────────────────────────────────────
        n            = selected_count
        company_word = "company" if n == 1 else "companies"

        # Insight 01 — best performer
        if n == 1:
            ins01_body = (
                f"{best_ticker} was the only selected company and "
                f"{_growth_verb(best_growth)} {_fmt_abs_pct(best_growth)} "
                f"during the selected period."
            )
        elif best_growth >= 0:
            ins01_body = (
                f"{best_ticker} recorded the strongest growth in the selected "
                f"period, increasing by {_fmt_abs_pct(best_growth)}."
            )
        else:
            ins01_body = (
                f"{best_ticker} had the strongest relative result in the selected "
                f"period, declining by {_fmt_abs_pct(best_growth)} — the smallest "
                f"decline among the selected stocks."
            )

        # Insight 02 — average
        if n == 1:
            ins02_body = (
                f"With only one company selected, the group average equals that "
                f"company's result: {_fmt_pct(average_growth)}."
            )
        else:
            avg_noun = "growth" if average_growth >= 0 else "change"
            ins02_body = (
                f"Across {n} selected {company_word}, the average historical "
                f"{avg_noun} was {_fmt_pct(average_growth)}."
            )

        # Insight 03 — spread
        if n == 1:
            ins03_stat_html = ""
            ins03_body = (
                "Only one stock is selected, so there is no difference "
                "to compare within the group."
            )
        else:
            spread = performance_spread
            if spread < 10:
                spread_interp = "The selected stocks performed relatively similarly."
            elif spread < 30:
                spread_interp = (
                    "The selected stocks showed a moderate difference in performance."
                )
            else:
                spread_interp = (
                    "The selected stocks followed noticeably different performance paths."
                )
            ins03_stat_html = (
                f'<p class="ins-lead-stat" style="color:#C0C0C0">'
                f'{spread:.1f}'
                f'<span style="font-size:1rem;font-weight:500;color:#555555"> pp</span>'
                f"</p>"
            )
            ins03_body = (
                f"The gap between the strongest ({best_ticker}) and weakest "
                f"({worst_ticker}) was {spread:.1f} percentage points. "
                f"{spread_interp}"
            )

        # ── Two-column layout: 01 left, 02+03 right ───────────────────────────
        ins_left, ins_right = st.columns([5, 7], gap="large")

        with ins_left:
            b_color = _pnl_color(best_growth)
            st.markdown(
                f"""
                <div class="ins-block">
                  <span class="ins-num">01</span>
                  <p class="ins-block-label">Strongest historical performance</p>
                  <p class="ins-lead-ticker" style="color:#F5F5F5">{best_ticker}</p>
                  <p class="ins-lead-stat" style="color:{b_color}">{_fmt_pct(best_growth)}</p>
                  <p class="ins-body">{ins01_body}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with ins_right:
            avg_color = _pnl_color(average_growth)
            st.markdown(
                f"""
                <div class="ins-block">
                  <span class="ins-num">02</span>
                  <p class="ins-block-label">Selected-group average</p>
                  <p class="ins-lead-stat"
                    style="color:{avg_color}">{_fmt_pct(average_growth)}</p>
                  <p class="ins-body">{ins02_body}</p>
                </div>
                <div class="ins-block ins-block--spaced">
                  <span class="ins-num">03</span>
                  <p class="ins-block-label">Performance spread</p>
                  {ins03_stat_html}
                  <p class="ins-body">{ins03_body}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Fetch fact (full width) ────────────────────────────────────────────
        st.markdown(
            f"""
            <div class="ins-fact-section">
              <span class="ins-fact-eyebrow">FETCHED COMPANY FACT</span>
              <h3 class="ins-fact-title">Did you know?</h3>
              <p class="ins-fact-body">{FETCH_FACT["fact"]}</p>
              <p class="ins-fact-source">Source:&nbsp;<a
                class="ins-fact-link"
                href="{FETCH_FACT["source_url"]}"
                target="_blank"
                rel="noopener noreferrer">{FETCH_FACT["source_title"]}</a></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── How to read this (full width) ─────────────────────────────────────
        st.markdown(
            """
            <div class="ins-how-section">
              <h3 class="ins-how-title">How to read this</h3>
              <ul class="ins-how-list">
                <li class="ins-how-item">
                  Historical growth does not guarantee future growth.
                </li>
                <li class="ins-how-item">
                  The results describe only the dates and companies currently selected.
                </li>
                <li class="ins-how-item">
                  A larger performance spread means the selected stocks behaved
                  more differently during the period.
                </li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# RECENT MARKET SNAPSHOT — yfinance (entirely separate from Plotly 2018–2019)
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    """
    <div class="mkt-section">
      <p class="mkt-eyebrow">RECENT MARKET VIEW</p>
      <h2 class="mkt-title">Latest available market close</h2>
      <p class="mkt-desc">
        A separate recent-market snapshot from yfinance.
        This information is not connected to the 2018–2019 historical dataset above.
      </p>
      <p class="mkt-sep-note">Historical analysis above: Plotly built-in dataset, 2018–2019.</p>
      <p class="mkt-sep-note">Recent snapshot below: yfinance latest available market closes.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.spinner("Loading the latest available market close..."):
    mkt_data = load_latest_market_data(tuple(selected))

if not mkt_data:
    st.markdown(
        '<p class="mkt-unavail">'
        "The latest market snapshot is temporarily unavailable. "
        "Historical comparison tools are still working."
        "</p>",
        unsafe_allow_html=True,
    )
else:
    # ── Build strip HTML ─────────────────────────────────────────────────────
    strip_items_html = ""
    for plotly_ticker in selected:
        if plotly_ticker not in mkt_data:
            continue
        d = mkt_data[plotly_ticker]
        if d["change"] > 0:
            chg_cls = "mkt-change-pos"
        elif d["change"] < 0:
            chg_cls = "mkt-change-neg"
        else:
            chg_cls = "mkt-change-flat"

        yf_note_html = ""
        if d["yf_ticker"] != plotly_ticker:
            yf_note_html = (
                f'<p class="mkt-yf-note">Historical label: {plotly_ticker}</p>'
            )

        # No leading whitespace — Markdown's CommonMark parser treats 4+ spaces
        # at line start as an indented code block, which prevents HTML rendering.
        strip_items_html += (
            f'<div class="mkt-item">'
            f'<span class="mkt-ticker">{d["yf_ticker"]}</span>'
            + yf_note_html
            + f'<p class="mkt-price">{_fmt_usd(d["close"])}</p>'
            f'<p class="{chg_cls}">'
            f'{_fmt_signed_usd(d["change"])} &nbsp; {_fmt_pct(d["change_pct"], 2)}'
            f'</p>'
            f'<p class="mkt-date">Latest close: {_fmt_date(d["date"])}</p>'
            f'</div>'
        )

    st.markdown(
        f'<div class="mkt-strip">{strip_items_html}</div>',
        unsafe_allow_html=True,
    )

    failed_tickers = [t for t in selected if t not in mkt_data]
    if failed_tickers:
        st.markdown(
            f'<p class="mkt-unavail">Data could not be retrieved for: '
            f'{", ".join(failed_tickers)}.</p>',
            unsafe_allow_html=True,
        )

st.markdown(
    '<p class="mkt-source">Source: yfinance. Market information may be delayed.</p>',
    unsafe_allow_html=True,
)

_btn_col, _ = st.columns([2, 10])
with _btn_col:
    if st.button("Refresh market snapshot", type="secondary"):
        load_latest_market_data.clear()
        st.rerun()
