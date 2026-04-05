"""
Security Dashboard — REFERENCE SOLUTION

Complete working version of dashboard/app.py for instructors.
"""
import streamlit as st
import pandas as pd
from scanner.main import run_full_scan
from ai.recommender import get_recommendation


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

if st.button("🔍 Run Full Scan", type="primary"):
    with st.spinner("Scanning AWS account..."):
        findings = run_full_scan()

    if findings:
        df = pd.DataFrame(findings)

        st.subheader("Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🔴 Critical", len(df[df['severity'] == 'CRITICAL']))
        col2.metric("🟠 High", len(df[df['severity'] == 'HIGH']))
        col3.metric("🟡 Medium", len(df[df['severity'] == 'MEDIUM']))
        col4.metric("Total", len(df))

        st.subheader("Findings")
        st.dataframe(
            df[['service', 'severity', 'resource', 'issue', 'principle_violated']],
            use_container_width=True,
        )

        st.subheader("🤖 AI Recommendations")
        st.caption("Click any finding to see Claude's remediation plan.")

        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_findings = sorted(
            findings,
            key=lambda f: severity_order.get(f.get('severity', 'LOW'), 4)
        )

        for finding in sorted_findings:
            label = f"[{finding['severity']}] {finding['issue']} — {finding['resource']}"
            with st.expander(label):
                with st.spinner("Generating AI recommendation..."):
                    recommendation = get_recommendation(finding)
                st.markdown(recommendation)
    else:
        st.success("No security issues found! 🎉")

st.markdown("---")
st.caption(
    "This scanner uses read-only AWS permissions (SecurityAudit policy). "
    "It cannot modify any resources."
)
