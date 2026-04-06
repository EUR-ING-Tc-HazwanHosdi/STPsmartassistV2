import streamlit as st
import cv2
import numpy as np
from PIL import Image

# ---------------------------------------------------------
# KNOWLEDGE BASE: MSIG Vol 4 STANDARDS & TROUBLESHOOTING
# ---------------------------------------------------------
# These values are derived from MSIG Vol 4, Section 5 & App D
[span_7](start_span)[span_8](start_span)[span_9](start_span)#
MSIG_KNOWLEDGE = {
    "FOAM_WHITE": {
        "Diagnosis": "Young Sludge / High F:M Ratio",
        "MSIG_Ref": "Vol 4, Section 5.8.3 (EA Systems)",
        "Action": "Increase Sludge Age (MCRT) by reducing wasting (WAS) rates."
    },
    "FOAM_BROWN": {
        "Diagnosis": "Old Sludge / Nocardia Growth",
        "MSIG_Ref": "Vol 4, Section 5.12 (Sludge Management)",
        "Action": "Increase wasting rate (WAS) and check for grease influent."
    },
    "DARK_SEPTIC": {
        "Diagnosis": "Anaerobic Conditions / Low Dissolved Oxygen",
        "MSIG_Ref": "Vol 4, Section 5.8.2 (CAS Process)",
        "Action": "Increase blower output. Target DO > 2.0 mg/L as per MSIG D.1."
    },
    "SYSTEM_OK": {
        "Diagnosis": "Normal Operation",
        "MSIG_Ref": "Vol 4, Table 3.2 (Design Effluent Values)",
        "Action": "Maintain routine inspection and log parameters."
    }
}

# ---------------------------------------------------------
# BRAIN LOGIC: Translating Visuals to MSIG Actions
# ---------------------------------------------------------
def msig_inference_engine(features, foam_trigger):
    """
    Acts as the 'Reasoning Engine' by comparing CV features 
    to MSIG Vol 4 standards[span_7](end_span)[span_8](end_span)[span_9](end_span).
    """
    # 1. [span_10](start_span)Check for Septic/Dark Sludge (MSIG Section 7.6.2.VIII)[span_10](end_span)
    if features["dark_sludge"] > 0.45:
        return MSIG_KNOWLEDGE["DARK_SEPTIC"]
    
    # 2. [span_11](start_span)[span_12](start_span)Check for Foam Issues (MSIG Section 5.8.3)[span_11](end_span)[span_12](end_span)
    if features["foam"] > foam_trigger:
        # If it's bright/white foam
        if features["brightness"] > 200:
            return MSIG_KNOWLEDGE["FOAM_WHITE"]
        else:
            return MSIG_KNOWLEDGE["FOAM_BROWN"]
            
    return MSIG_KNOWLEDGE["SYSTEM_OK"]

# ---------------------------------------------------------
# CORE CV PROCESSOR (Your Eyes)
# ---------------------------------------------------------
def extract_features(pil_image):
    image = np.array(pil_image)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # [span_13](start_span)Texture Analysis for Bubbles[span_13](end_span)
    edges = cv2.Canny(gray, 50, 150)
    foam_density = np.sum(edges > 0) / edges.size
    
    # [span_14](start_span)Brightness/Color Analysis[span_14](end_span)
    avg_brightness = np.mean(gray)
    dark_pixels = np.sum(gray < 40) / gray.size
    
    return {
        "foam": foam_density,
        "brightness": avg_brightness,
        "dark_sludge": dark_pixels,
        "debug_mask": edges
    }

# ---------------------------------------------------------
# STREAMLIT INTERFACE (Your Voice)
# ---------------------------------------------------------
st.title("🌊 MSIG Smart Assist Pro")
st.caption("Integrated with Malaysian Sewerage Industry Guidelines Vol 4")

uploaded_file = st.file_uploader("Upload STP Surface Photo", type=["jpg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    data = extract_features(img)
    
    # Run the "Brain"
    diagnosis = msig_inference_engine(data, foam_trigger=0.15)
    
    # UI Display
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="Live Feed", use_container_width=True)
    with col2:
        st.image(data["debug_mask"], caption="MSIG Texture Map", use_container_width=True)
        
    st.subheader(f"Status: {diagnosis['Diagnosis']}")
    st.warning(f"**Manual Reference:** {diagnosis['MSIG_Ref']}")
    st.info(f"**Action Required:** {diagnosis['Action']}")
# MSIG Vol 4 SBR Brain Module
def sbr_smart_logic(current_cycle_time, measured_mlss):
    # [span_15](start_span)MSIG Table 5.16 Standards[span_15](end_span)
    MIN_MLSS = 3000
    MAX_MLSS = 4500
    
    advice = []
    
    if measured_mlss < MIN_MLSS:
        advice.append({
            "Issue": "Low MLSS",
            "Action": "Reduce sludge wasting (WAS). Check MSIG Vol 4, Table 5.16.",
            "Ref": "Section 5.8.6.2"
        })
    elif measured_mlss > MAX_MLSS:
        advice.append({
            "Issue": "High MLSS",
            "Action": "Increase wasting to prevent solids carry-over during Decant.",
            "Ref": "Section 5.8.6.1"
        })
        
    return advice
def msig_pump_validator(start_lvl, stop_lvl, assist_lvl, well_width):
    # MSIG 5.3.2 Standards
    MIN_DELTA = 450
    MAX_DELTA = 900
    MIN_WIDTH = 2000 # in mm
    
    current_delta = start_lvl - stop_lvl
    reports = []

    # Check Stop/Start Level Compliance (MSIG 5.3.2.II.f)
    if current_delta < MIN_DELTA or current_delta > MAX_DELTA:
        reports.append("❌ Level Delta Violation: Must be 450mm-900mm.")
    
    # Check Duty/Assist Gap (MSIG 5.3.2.II.g)
    if (assist_lvl - start_lvl) < 150:
        reports.append("❌ Assist Gap Violation: Min 150mm required.")
        
    # Check Structural Width (MSIG 5.3.2.II.h)
    if well_width < MIN_WIDTH:
        reports.append(f"❌ Well Width Violation: {well_width}mm is below 2000mm limit.")
        
    return reports if reports else ["✅ Pump Station Settings MSIG Compliant"]
import math

def calculate_friction_loss(flow_rate_lps, pipe_diameter_mm, pipe_length_m, C=140):
    """
    Calculates friction head loss (Hf) using Hazen-Williams.
    Flow rate in Liters per second (Lps).
    Diameter in mm.
    """
    # Convert flow to m^3/s and diameter to meters
    Q = flow_rate_lps / 1000
    D = pipe_diameter_mm / 1000
    
    # Hazen-Williams Formula for Head Loss (m)
    # Hf = 10.67 * (Q/C)^1.852 * (1/D^4.87) * L
    hf = 10.67 * (Q/C)**1.852 * (1/D**4.87) * pipe_length_m
    return hf

def stp_tdh_brain(static_lift, flow_lps, pipe_dia, pipe_len):
    friction = calculate_friction_loss(flow_lps, pipe_dia, pipe_len)
    
    # Adding a 10% safety margin for 'Minor Losses' (valves/bends)
    total_head = static_lift + (friction * 1.1) 
    
    return round(total_head, 2)
import streamlit as st
import math

# ---------------------------------------------------------
# HYDRAULIC ENGINE (MSIG SECTION 5.3.3)
# ---------------------------------------------------------
def calculate_tdh(static_head, flow_lps, pipe_dia_mm, pipe_len_m):
    # MSIG Standard: Minimum pipe diameter for sewage is 100mm
    is_compliant_dia = pipe_dia_mm >= 100
    
    # Hazen-Williams Constants (C=140 for smooth plastic/lined pipe)
    C = 140
    Q = flow_lps / 1000  # Convert L/s to m3/s
    D = pipe_dia_mm / 1000 # Convert mm to m
    
    # Friction Loss Formula: Hf = 10.67 * (Q/C)^1.852 * D^-4.87 * L
    f_loss = 10.67 * (Q/C)**1.852 * (D**-4.87) * pipe_len_m
    
    # Total Dynamic Head (Static + Friction + 10% for fittings/valves)
    tdh = static_head + (f_loss * 1.1)
    
    return round(tdh, 2), is_compliant_dia

# ---------------------------------------------------------
# STREAMLIT DASHBOARD UI
# ---------------------------------------------------------
st.header("📏 MSIG Design Verification")
st.info("Verify if your Pump Station & Piping meet SPAN standards.")

with st.expander("Pipe & Pump Input Parameters"):
    col1, col2 = st.columns(2)
    with col1:
        s_head = st.number_input("Static Lift (meters)", min_value=0.0, value=5.0)
        p_len = st.number_input("Total Pipe Length (meters)", min_value=0.0, value=50.0)
    with col2:
        p_dia = st.number_input("Pipe Inner Diameter (mm)", min_value=1, value=100)
        flow = st.number_input("Design Flow Rate (L/s)", min_value=0.1, value=15.0)

# Run Calculation
total_head, dia_check = calculate_tdh(s_head, flow, p_dia, p_len)

# ---------------------------------------------------------
# BRAIN OUTPUT & COMPLIANCE CHECK
# ---------------------------------------------------------
st.subheader("Results & Compliance")

c1, c2 = st.columns(2)
c1.metric("Calculated TDH", f"{total_head} m")

if dia_check:
    c2.success("Pipe Diameter: MSIG Compliant (≥100mm)")
else:
    c2.error("Pipe Diameter: NON-COMPLIANT (<100mm)")
    st.warning("⚠️ MSIG Vol 4 Section 5.3.3.I requires a minimum 100mm diameter for forcemains.")

# Automated Advice from the "Brain"
st.write("---")
st.markdown("### 🤖 Engineering Advice")
if total_head > 25:
    st.error("High TDH detected. Consider increasing pipe diameter to reduce friction or check for high-head pump suitability.")
elif total_head < s_head:
    st.error("Calculation Error: TDH cannot be lower than Static Head.")
else:
    st.success("TDH is within normal operational range for standard STP submersible pumps.")
import streamlit as st
import pandas as pd
import datetime

# ---------------------------------------------------------
# REPORT GENERATION BRAIN
# ---------------------------------------------------------
def generate_summary_report(diag, features, tdh_val, dia_ok):
    # Consolidating all "Brain" data into a single dictionary
    report_data = {
        "Metric": [
            "Inspection Timestamp",
            "Visual Finding",
            "MSIG Reference",
            "Foam Density",
            "Sludge Darkness",
            "Calculated TDH",
            "Pipe Diameter Compliance"
        ],
        "Value": [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            diag['Diagnosis'],
            diag['MSIG_Ref'],
            f"{round(features['foam']*100, 1)}%",
            f"{round(features['dark_sludge']*100, 1)}%",
            f"{tdh_val} meters",
            "PASS" if dia_ok else "FAIL"
        ]
    }
    return pd.DataFrame(report_data)

# ---------------------------------------------------------
# UI: FINAL REPORT CENTER
# ---------------------------------------------------------
st.divider()
st.header("📋 Plant Inspection Report")

# Check if analysis has been run
if 'features' in locals() and 'diagnosis' in locals():
    # Gather data from previous modules
    final_df = generate_summary_report(diagnosis, features, total_head, dia_check)
    
    # Display the structured report
    st.table(final_df)
    
    # Add the "Expert Action" section
    st.subheader("🛠️ Recommended Action Plan")
    st.success(f"**Immediate Step:** {diagnosis['Action']}")
    
    if not dia_check:
        st.error("🚨 URGENT: Upgrade forcemain to 100mm to meet MSIG Vol 4 standards.")

    # Download Button for CSV/Excel
    csv = final_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Inspection Report (CSV)",
        data=csv,
        file_name=f"STP_Report_{datetime.date.today()}.csv",
        mime="text/csv",
    )
else:
    st.info("Please upload an image and run the design verification to generate a full report.")
# ---------------------------------------------------------
# TROUBLESHOOTING WIZARD (REFINEMENT ENGINE)
# ---------------------------------------------------------
def stp_wizard():
    st.sidebar.markdown("---")
    st.sidebar.header("🧙 Troubleshooting Wizard")
    st.sidebar.write("Refine your diagnosis with field observations.")
    
    # Question 1: Settling Test (Standard MSIG Settleability Test)
    settle = st.sidebar.selectbox(
        "Sludge Settlement (30 min test):",
        ["Select...", "Settles fast, leaves cloudy water", "Settles slowly, stays suspended", "Plumes/Clumps rising to top"]
    )
    
    # Question 2: Color/Texture
    texture = st.sidebar.selectbox(
        "Physical Texture:",
        ["Select...", "Leathery/Thick Brown", "Crisp/White/Bubbly", "Greasy/Oily"]
    )

    # Logic Bridge
    if settle == "Settles fast, leaves cloudy water" and texture == "Crisp/White/Bubbly":
        st.sidebar.warning("🎯 **Confirmed: Young Sludge (Low MCRT)**")
        st.sidebar.write("Action: Reduce WAS rate by 10% daily until MLSS stabilizes.")
        
    elif settle == "Settles slowly, stays suspended" and texture == "Leathery/Thick Brown":
        st.sidebar.warning("🎯 **Confirmed: Old Sludge / Nocardia**")
        st.sidebar.write("Action: Increase wasting and check for anaerobic zones in Aeration Tank.")
        
    elif settle == "Plumes/Clumps rising to top":
        st.sidebar.error("🎯 **Confirmed: Denitrification in Clarifier**")
        st.sidebar.write("Action: Increase RAS (Return Sludge) rate or check for blocked hopper.")

# Call the wizard in your main app
stp_wizard()
