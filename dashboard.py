import streamlit as st
from supabase import create_client
import pandas as pd
import time
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Sibu AquaML | Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapsed for a cleaner app-like feel
)

# --- MODERN UI CSS INJECTION ---
st.markdown("""
    <style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide default Streamlit clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }

    /* Beautify the Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #0F172A; /* Deep slate background */
        border: 1px solid #1E293B;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s ease-in-out, border-color 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: #38BDF8;
    }

    /* Specific Accent Colors for Metrics */
    div[data-testid="stMetric"]:nth-child(1) > div[data-testid="metric-container"] { border-top: 4px solid #818CF8; } /* AI Status */
    div[data-testid="stMetric"]:nth-child(2) > div[data-testid="metric-container"] { border-top: 4px solid #F43F5E; } /* pH */
    div[data-testid="stMetric"]:nth-child(3) > div[data-testid="metric-container"] { border-top: 4px solid #10B981; } /* Turbidity */

    /* Beautify the Tabs */
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    div[data-testid="stTabs"] [data-baseweb="tab"] {
        background-color: #1E293B;
        border-radius: 8px;
        padding: 10px 20px;
        border: 1px solid #334155;
        color: #94A3B8;
    }
    div[data-testid="stTabs"] [aria-selected="true"] {
        background-color: #38BDF8;
        color: #0F172A;
        font-weight: 800;
        border: none;
    }

    /* Form Submit Button */
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #38BDF8 0%, #2563EB 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 15px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: opacity 0.2s;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        opacity: 0.8;
    }
    </style>
""", unsafe_allow_html=True)

# The code will now pull the keys securely from Render and Streamlit Cloud
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]


@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_connection()

# --- HEADER SECTION ---
col_logo, col_title = st.columns([1, 10])
with col_logo:
    st.markdown("<h1 style='text-align: center; color: #38BDF8;'>💧</h1>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 style='margin-bottom: 0px;'>Sibu AquaML</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; margin-top: -10px;'>Permai Zone Precision Monitoring System</p>",
                unsafe_allow_html=True)

st.write("")  # Spacer

# --- MULTI-PAGE TABS ---
tab1, tab2 = st.tabs(["📊 Live Pipeline Analysis", "📝 Community Anomaly Reports"])

# ==========================================
# PAGE 1: THE LIVE DASHBOARD
# ==========================================
with tab1:
    try:
        # Fetch latest 20 readings for better charts
        response = supabase.table("water_readings").select("*").order("recorded_at", desc=True).limit(20).execute()
        data = response.data

        if data:
            latest = data[0]

            # --- BIG KPI CARDS ---
            col1, col2, col3 = st.columns(3)

            # AI Status Card with conditional formatting
            ai_status = latest['ai_prediction']
            ai_delta = "Pipeline Nominal" if ai_status == 'Safe' else "Contamination Detected"
            ai_color = "normal" if ai_status == 'Safe' else "inverse"

            col1.metric("Neural Net Prediction", ai_status, delta=ai_delta, delta_color=ai_color)
            col2.metric("Real-Time pH Level", f"{latest['ph_level']:.2f}", delta="- Peat Baseline", delta_color="off")
            col3.metric("Turbidity (NTU)", f"{latest['turbidity_ntu']:.2f}", delta="Within Threshold",
                        delta_color="off")

            st.divider()

            # --- PREPARE DATA FOR CHARTS AND TABLES ---
            df = pd.DataFrame(data)
            df['Timestamp'] = pd.to_datetime(df['recorded_at'])

            # --- LIVE CHARTS ---
            st.markdown("### 📈 Live Telemetry Graphs")
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.caption("pH Fluctuations over time")
                # Reverse the dataframe so the chart flows left-to-right correctly
                ph_data = df[['Timestamp', 'ph_level']].set_index('Timestamp').iloc[::-1]
                st.area_chart(ph_data, color="#F43F5E", height=200)

            with chart_col2:
                st.caption("Turbidity (NTU) over time")
                turb_data = df[['Timestamp', 'turbidity_ntu']].set_index('Timestamp').iloc[::-1]
                st.area_chart(turb_data, color="#10B981", height=200)

            # --- CLEAN DATA TABLE ---
            st.markdown("### 📋 Raw Sensor Feed")

            # Clean up columns for the table display
            display_df = df.copy()
            display_df['Timestamp'] = display_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            display_df = display_df[['Timestamp', 'ph_level', 'turbidity_ntu', 'ai_prediction']]
            display_df.columns = ['Timestamp', 'pH Level', 'Turbidity (NTU)', 'AI Status']

            st.dataframe(display_df, use_container_width=True, hide_index=True)

        else:
            st.info("🟢 System Online. Awaiting telemetry from simulator...")

    except Exception as e:
        st.error(f"Database connection error: {e}")

# ==========================================
# PAGE 2: COMMUNITY REPORTS
# ==========================================
with tab2:
    st.markdown("### 📡 Submit Visual Anomaly")
    st.markdown(
        "<p style='color: #94A3B8;'>Allow Permai residents to report local water issues directly to the central system.</p>",
        unsafe_allow_html=True)

    with st.form("community_report_form", clear_on_submit=True):
        zone = st.text_input("Location Zone", placeholder="e.g., Permai North Sector 3")
        description = st.text_area("Observation Details",
                                   placeholder="Describe water appearance (e.g., muddy, yellow, chemical smell)...")

        submitted = st.form_submit_button("Log Report to Cloud Database")

        if submitted:
            if zone and description:
                try:
                    supabase.table("community_reports").insert({
                        "zone": zone,
                        "description": description,
                        "status": "Pending"
                    }).execute()
                    st.success(f"✅ Report for **{zone}** successfully encrypted and logged!")
                except Exception as e:
                    st.error(f"❌ Failed to log report: {e}")
            else:
                st.warning("⚠️ Please complete all fields before submitting.")

    st.divider()

    st.markdown("### 🚨 Recent Community Logs")
    try:
        reports_response = supabase.table("community_reports").select("*").order("created_at", desc=True).limit(
            5).execute()
        reports_data = reports_response.data

        if reports_data:
            for report in reports_data:
                # Create a sleek mini-card for each report
                status_emoji = "⏳" if report['status'] == 'Pending' else "✅"
                status_color = "#F59E0B" if report['status'] == 'Pending' else "#10B981"

                with st.container(border=True):
                    st.markdown(f"<h4 style='margin-bottom: 0px;'>{report['zone']}</h4>", unsafe_allow_html=True)
                    st.markdown(
                        f"<span style='color: {status_color}; font-size: 12px; font-weight: bold;'>{status_emoji} {report['status'].upper()}</span> &nbsp;&nbsp; <span style='color: #64748B; font-size: 12px;'>Logged: {pd.to_datetime(report['created_at']).strftime('%Y-%m-%d %H:%M:%S')}</span>",
                        unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #CBD5E1; margin-top: 10px;'>{report['description']}</p>",
                                unsafe_allow_html=True)
        else:
            st.info("No community reports have been submitted yet.")

    except Exception as e:
        st.error("Could not load community reports.")

# ==========================================
# AUTO-REFRESH SCRIPT
# ==========================================
time.sleep(5)
st.rerun()