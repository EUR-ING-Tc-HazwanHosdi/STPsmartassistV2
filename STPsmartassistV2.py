import streamlit as st
import cv2
import numpy as np
from PIL import Image
import datetime
import pandas as pd
import math

# ---------------------------------------------------------
# 1. KNOWLEDGE BASE & BRAIN LOGIC (MSIG VOL 4)
# ---------------------------------------------------------
MSIG_KNOWLEDGE = {
    "FOAM_WHITE": {
        "Diagnosis": "Young Sludge / High F:M Ratio",
        "MSIG_Ref": "Vol 4, Section 5.8.3",
        "Action": "Increase Sludge Age (MCRT) by reducing wasting (WAS)."
    },
    "FOAM_BROWN": {
        "Diagnosis": "Old Sludge / Nocardia Growth",
        "MSIG_Ref": "Vol 4, Section 5.12",
        "Action": "Increase wasting rate (WAS) and check for grease influent."
    },
    "DARK_SEPTIC": {
        "Diagnosis": "Anaerobic Conditions / Low DO",
        "MSIG_Ref": "Vol 4, Section 5.8.2",
        "Action": "Increase blower output. Target DO > 2.0 mg/L."
    },
    "SYSTEM_OK": {
        "Diagnosis": "Normal Operation",
        "MSIG_Ref": "Vol 4, Table 3.2",
        "Action": "Maintain routine inspection."
    }
}

def extract_features(pil_image):
    image = np.array(pil_image)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    return {
        "foam": np.sum(edges > 0) / edges.size,
        "brightness": np.mean(gray),
        "dark_sludge": np.sum(gray < 40) / gray.size,
        "debug_mask": edges
    }

def msig_inference_engine(features, foam_trigger=0.15):
    if features["dark_sludge"] > 0.45:
        return MSIG_KNOWLEDGE["DARK_SEPTIC"]
    if features["foam"] > foam_trigger:
        if features["brightness"] > 180:
            return MSIG_KNOWLEDGE["FOAM_WHITE"]
        else:
            return MSIG_KNOWLEDGE["FOAM_BROWN"]
    return MSIG_KNOWLEDGE["SYSTEM_OK"]

def calculate_tdh(static_head, flow_lps, pipe_dia_mm, pipe_len_m):
    C = 140 # Hazen-Williams constant for smooth pipe
    Q = flow_lps / 1000  # L/s to m3/s
    D = pipe_dia_mm / 1000 # mm to m
    # Friction Loss Formula
    hf = 10.67 * (Q/C)**1.852 * (D**-4.87) * pipe_len_m
    tdh = static_head + (hf * 1.1) # 10% safety factor
    return round(tdh, 2)

def stp_wizard():
    st.sidebar.markdown("---")
    st.sidebar.header("🧙 Troubleshooting Wizard")
    st.sidebar.write("Refine diagnosis with field observations.")
    
    settle = st.sidebar.selectbox(
        "Sludge Settlement (30 min test):",
        ["Select...", "Settles fast, leaves cloudy water", "Settles slowly, stays suspended", "Plumes/Clumps rising to top"]
    )
    
    texture = st.sidebar.selectbox(
        "Physical Texture:",
        ["Select...", "Leathery/Thick Brown", "Crisp/White/Bubbly", "Greasy/Oily"]
    )

    if settle == "Settles fast, leaves cloudy water" and texture == "Crisp/White/Bubbly":
        st.sidebar.warning("🎯 **Confirmed: Young Sludge**")
        st.sidebar.write("Action: Reduce WAS rate by 10% daily.")
    elif settle == "Settles slowly, stays suspended" and texture == "Leathery/Thick Brown":
        st.sidebar.warning("🎯 **Confirmed: Old Sludge**")
        st.sidebar.write("Action: Increase wasting and check for grease.")
    elif settle == "Plumes/Clumps rising to top":
        st.sidebar.error("🎯 **Confirmed: Denitrification**")
        st.sidebar.write("Action: Increase RAS rate or check for blocked hopper.")

# ---------------------------------------------------------
# 2. STREAMLIT UI
# ---------------------------------------------------------
st.set_page_config(page_title="MSIG Smart Assist", layout="wide")
st.title("🌊 MSIG Smart Assist Pro")
st.caption("Integrated with Malaysian Sewerage Industry Guidelines Vol 4")

# Sidebar for Design Parameters
st.sidebar.header("🛠️ Design Verification Settings")
s_head = st.sidebar.number_input("Static Lift (m)", value=5.0)
p_len = st.sidebar.number_input("Pipe Length (m)", value=50.0)
p_dia = st.sidebar.number_input("Pipe Dia (mm)", value=100)
flow = st.sidebar.number_input("Flow Rate (L/s)", value=10.0)

tab1, tab2 = st.tabs(["📸 Visual Inspection", "📊 Design Report"])

with tab1:
    uploaded_file = st.file_uploader("Upload Surface Photo", type=["jpg", "png"])
    if uploaded_file:
        img = Image.open(uploaded_file)
        features = extract_features(img)
        diagnosis = msig_inference_engine(features)
        
        # Save the finding to a variable we can use later
        st.session_state['current_visual'] = diagnosis['Diagnosis']
        
        c1, c2 = st.columns(2)
        c1.image(img, caption="Original Feed", use_container_width=True)
        c2.image(features["debug_mask"], caption="Texture Analysis", use_container_width=True)
        
        st.subheader(f"Finding: {diagnosis['Diagnosis']}")
        st.info(f"**Action:** {diagnosis['Action']} (Ref: {diagnosis['MSIG_Ref']})")

with tab2:
    tdh = calculate_tdh(s_head, flow, p_dia, p_len)
    dia_ok = p_dia >= 100
    
    st.subheader("Hydraulic Verification")
    col_r1, col_r2 = st.columns(2)
    col_r1.metric("Calculated TDH", f"{tdh} m")
    col_r2.metric("Pipe Compliance", "PASS" if dia_ok else "FAIL")
    
    if not dia_ok:
        st.error("🚨 MSIG Section 5.3.3 requires minimum 100mm forcemains.")
    
    # Check if analysis has been run for report generation
    if 'features' in locals():
        report_data = {
            "Metric": ["Timestamp", "Finding", "TDH", "Compliance"],
            "Value": [
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                diagnosis['Diagnosis'],
                f"{tdh} m",
                "PASS" if dia_ok else "FAIL"
            ]
        }
        df = pd.DataFrame(report_data)
        st.table(df)
        st.download_button("📥 Download Report (CSV)", df.to_csv(index=False), "STP_Report.csv")
# ---------------------------------------------------------
# CONSENSUS ENGINE (THE FINAL COMMAND)
# ---------------------------------------------------------
    def final_action_plan(visual_diag, wizard_settle, wizard_texture):
    st.write("---")
    st.header("⚡ High-Priority Action Plan")
    
    # Priority 1: Denitrification (Immediate Threat)
    if wizard_settle == "Plumes/Clumps rising to top":
        st.error("🚨 **CRITICAL: Secondary Clarifier Failure Imminent**")
        st.markdown("""
        **Consensus:** Visuals show process stress, but physical rising sludge is the priority.
        * **Immediate Action:** Increase RAS (Return Sludge) rate to 100-150% of influent.
        * **Process Check:** Reduce aeration slightly to minimize Nitrate formation.
        """)
        
    # Priority 2: Old Sludge / Nocardia
    elif "Old Sludge" in visual_diag or wizard_texture == "Leathery/Thick Brown":
        st.warning("⚠️ **STRATEGIC: Process Correction Required**")
        st.markdown("""
        **Consensus:** Both Visual and Field tests confirm high Sludge Age (MCRT).
        * **Immediate Action:** Increase WAS (Wasting) by 20% today.
        * **Maintenance:** Spray foam with water or chlorine solution if Nocardia is persistent.
        """)

    # Priority 3: Young Sludge
    elif "Young Sludge" in visual_diag or wizard_texture == "Crisp/White/Bubbly":
        st.info("ℹ️ **ADVISORY: Building Biomass**")
        st.markdown("""
        **Consensus:** System is under-loaded or recovering from a washout.
        * **Immediate Action:** Stop/Reduce wasting (WAS) until MLSS reaches >3000 mg/L.
        * **Ref:** MSIG Vol 4, Table 5.16.
        """)
    else:
        st.success("✅ **STABLE: Continue Routine Monitoring**")

# --- INTEGRATION STEPS ---
# In your 'tab1' section, after your 'diagnosis' is defined, 
# you should store the diagnosis in a session state so the 
# engine can read it alongside the sidebar inputs.

stp_wizard()
