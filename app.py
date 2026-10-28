import streamlit as st
import pandas as pd
import dns.resolver
import time

# Page config
st.set_page_config(page_title="Bulk Sender Score Checker", page_icon="✉️", layout="wide")

st.title("✉️ Bulk Sender Score Checker")
st.write("Upload a CSV file or enter IP addresses manually to check reputation scores.")

def get_sender_score(ip):
    ip = ip.strip()
    if not ip:
        return "Empty"
    try:
        # IP octets reverse panrom
        parts = ip.split('.')
        if len(parts) != 4:
            return "Invalid IP"
        reversed_ip = '.'.join(reversed(parts))
        query_host = f"{reversed_ip}.score.senderscore.com"
        
        # DNS query
        answers = dns.resolver.resolve(query_host, 'A')
        for rdata in answers:
            score = rdata.to_text().split('.')[-1]
            return score
    except dns.resolver.NXDOMAIN:
        return "No Data / Clean"
    except Exception as e:
        return f"Error: {type(e).__name__}"

# Tab interface
tab1, tab2 = st.tabs(["📁 Upload CSV", "✍️ Manual Input"])

results = []

with tab1:
    uploaded_file = st.file_uploader("Upload CSV file (Must contain an 'ip' column)", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        ip_column = None
        for col in df.columns:
            if "ip" in col.lower():
                ip_column = col
                break
        
        if ip_column:
            st.success(f"Detected IP column: `{ip_column}`")
            if st.button("Check Scores (CSV)"):
                ips = df[ip_column].dropna().astype(str).tolist()
                progress_bar = st.progress(0)
                
                for idx, ip in enumerate(ips):
                    score = get_sender_score(ip)
                    results.append({"IP": ip, "Sender Score": score})
                    progress_bar.progress((idx + 1) / len(ips))
                    time.sleep(0.05)
        else:
            st.error("No column named 'ip' found in CSV. Please rename your column to 'ip'.")

with tab2:
    text_input = st.text_area("Enter IP addresses (one per line):", height=150)
    if st.button("Check Scores (Manual)"):
        ips = [line.strip() for line in text_input.split('\n') if line.strip()]
        if ips:
            progress_bar = st.progress(0)
            for idx, ip in enumerate(ips):
                score = get_sender_score(ip)
                results.append({"IP": ip, "Sender Score": score})
                progress_bar.progress((idx + 1) / len(ips))
                time.sleep(0.05)

# Display Results & Download
if results:
    result_df = pd.DataFrame(results)
    st.subheader("Results")
    st.dataframe(result_df, use_container_width=True)
    
    csv_data = result_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv_data,
        file_name="sender_scores.csv",
        mime="text/csv"
    )