"""
Security Dashboard — STUDENT TODO

A Streamlit dashboard that displays security findings and
AI-generated recommendations.

Your job: fill in the two TODO sections below.
"""
import streamlit as st
import pandas as pd
from scanner.main import run_full_scan
from ai.recommender import get_recommendation


# --- Page config (already done for you) ---
st.set_page_config(
    page_title="AWS Security Guardian",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ AWS AI Security Scanner")
st.caption("Grounded in Least Privilege & Zero Trust")

st.markdown("""
This tool scans your AWS account for security misconfigurations
and uses AI to generate plain-English remediation guidance.
""")

# --- Scan button ---
if st.button("🔍 Run Full Scan", type="primary"):

    # -----------------------------------------------------------
    # TODO #1: Run the scan and store findings
    #
    # Use a st.spinner to show a loading message while scanning.
    # Call run_full_scan() and save the result to a variable
    # called `findings`.
    #
    # Example:
    #   with st.spinner("Scanning AWS account..."):
    #       findings = run_full_scan()
    # -----------------------------------------------------------


    # Convert findings to a DataFrame (already done for you)
    if findings:
        df = pd.DataFrame(findings)

        # --- Severity metrics ---
        st.subheader("Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🔴 Critical", len(df[df['severity'] == 'CRITICAL']))
        col2.metric("🟠 High", len(df[df['severity'] == 'HIGH']))
        col3.metric("🟡 Medium", len(df[df['severity'] == 'MEDIUM']))
        col4.metric("Total", len(df))

        # --- Findings table ---
        st.subheader("Findings")
        st.dataframe(
            df[['service', 'severity', 'resource', 'issue', 'principle_violated']],
            use_container_width=True,
        )

        # --- AI Recommendations ---
        st.subheader("🤖 AI Recommendations")
        st.caption("Click any finding to see Claude's remediation plan.")

        # -------------------------------------------------------
        # TODO #2: Loop through findings and show AI recommendations
        #
        # For each finding, create a st.expander with the severity
        # and issue as its label. Inside the expander, call
        # get_recommendation(finding) and display the result with
        # st.write() or st.markdown().
        #
        # Example:
        #   for finding in findings:
        #       label = f"[{finding['severity']}] {finding['issue']}"
        #       with st.expander(label):
        #           recommendation = get_recommendation(finding)
        #           st.markdown(recommendation)
        # -------------------------------------------------------


    else:
        st.success("No security issues found! 🎉")

# --- Footer ---
st.markdown("---")
st.caption(
    "This scanner uses read-only AWS permissions (SecurityAudit policy). "
    "It cannot modify any resources."
)
