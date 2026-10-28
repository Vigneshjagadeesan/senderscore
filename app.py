import streamlit as st
import pandas as pd
import dns.resolver
import dns.reversename
import socket
import time

st.set_page_config(page_title="Bulk SenderScore Checker", layout="wide", page_icon="✉️")
st.title("Bulk SenderScore & IP Reputation Extractor")
st.write("Sender Score, Hostname, matrum Reputation status-ai bulk-ah check pannunga.")

def check_ip_details(ip):
    ip = ip.strip()
    if not ip:
        return None
    
    # 1. Reverse DNS moolama Hostname kandupidikrom
    hostname = "N/A"
    try:
        rev_name = dns.reversename.from_address(ip)
        hostname = str(dns.resolver.resolve(rev_name, "PTR")[0]).rstrip('.')
    except Exception:
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except Exception:
            hostname = "Unknown Host"

    # 2. Sender Score Database Query
    score = "N/A"
    status = "Unknown"
    try:
        reversed_ip = '.'.join(reversed(ip.split('.')))
        query_host = f"{reversed_ip}.score.senderscore.com"
        answers = dns.resolver.resolve(query_host, 'A')
        for rdata in answers:
            # Response address-oda last octet thaan exact Sender Score (0-100)
            score_val = int(rdata.to_text().split('.')[-1])
            score = str(score_val)
            if score_val >= 80:
                status = "GOOD"
            elif score_val >= 70:
                status = "AVERAGE"
            else:
                status = "POOR"
    except dns.resolver.NXDOMAIN:
        score = "Not Listed"
        status = "Low Volume / No History"
    except Exception as e:
        score = "Lookup Error"
        status = str(e)

    # 3. Domain extraction from Hostname
    domain = "N/A"
    if hostname not in ["N/A", "Unknown Host"]:
        parts = hostname.split('.')
        if len(parts) >= 2:
            domain = '.'.join(parts[-2:])

    return {
        "IP Address": ip,
        "Sender Score": score,
        "Reputation Status": status,
        "Hostname": hostname,
        "Root Domain": domain
    }

# Input Box
ip_input = st.text_area(
    "IPs-ai enter pannunga (One per line):",
    value="134.128.99.186\n204.220.169.114",
    height=150
)

if st.button("Check Scores"):
    ips = [line.strip() for line in ip_input.split("\n") if line.strip()]
    if ips:
        results = []
        progress_bar = st.progress(0)
        
        for idx, ip in enumerate(ips):
            data = check_ip_details(ip)
            if data:
                results.append(data)
            progress_bar.progress((idx + 1) / len(ips))
            time.sleep(0.05)
            
        res_df = pd.DataFrame(results)
        st.subheader("Results")
        st.dataframe(res_df, use_container_width=True)
        
        csv_file = res_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv_file,
            file_name="bulk_senderscore_results.csv",
            mime="text/csv"
        )
