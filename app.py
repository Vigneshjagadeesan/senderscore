import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="Bulk SenderScore Detail Extractor", layout="wide", page_icon="✉️")
st.title("Bulk SenderScore Full Detail Extractor")
st.write("Sender Score, Volume, Hostname, matrum Sending Domains-ai bulk-ah extract pannunga.")

# Sidebar-la unga authenticated session cookie-ai enter panna option
st.sidebar.header("Authentication Settings")
cookie_input = st.sidebar.text_area(
    "Website Cookie (Required for Sending Domains)", 
    help="Browser inspect element (F12) -> Network tab -> copy cookie from senderscore request",
    height=120
)

def fetch_senderscore_full_report(ip, cookie_header=""):
    ip = ip.strip()
    if not ip:
        return None

    url = f"https://senderscore.org/assess/get-your-score/report/?lookup={ip}&authenticated=true"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }
    
    if cookie_header.strip():
        headers["Cookie"] = cookie_header.strip()

    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            return {"IP": ip, "Score": f"HTTP {response.status_code}", "Hostname": "Error", "Sending Domains": "Error"}
        
        soup = BeautifulSoup(response.text, "html.parser")

        # 1. Score Extraction
        score_tag = soup.find(class_=lambda x: x and "score" in x.lower())
        score = score_tag.get_text(strip=True) if score_tag else "N/A"

        # 2. Hostname Extraction
        hostname = "N/A"
        for td in soup.find_all(["td", "div", "span"]):
            if "hostname" in td.get_text().lower():
                sibling = td.find_next_sibling() or td.parent.find_next_sibling()
                if sibling:
                    hostname = sibling.get_text(strip=True)
                    break

        # 3. Sending Domains List Extraction
        domains = []
        domain_table = soup.find("div", string=lambda t: t and "sending domains" in t.lower())
        if domain_table:
            table_container = domain_table.find_parent("div")
            if table_container:
                for a_tag in table_container.find_all(["a", "span", "td"]):
                    text = a_tag.get_text(strip=True)
                    if "." in text and " " not in text and text.lower() not in ["next", "previous", "domain"]:
                        domains.append(text)
        
        # Deduplicate list
        domains = list(dict.fromkeys(domains))
        domains_str = ", ".join(domains) if domains else "None Listed / Login Expired"

        return {
            "IP Address": ip,
            "Sender Score": score,
            "Hostname": hostname,
            "Sending Domains": domains_str
        }

    except Exception as e:
        return {
            "IP Address": ip,
            "Sender Score": "Error",
            "Hostname": str(e),
            "Sending Domains": "Error"
        }

# User IP Input
ip_input = st.text_area(
    "IPs-ai enter pannunga (One per line):",
    value="142.0.85.188\n134.128.99.186",
    height=150
)

if st.button("Extract Bulk Data"):
    ips = [line.strip() for line in ip_input.split("\n") if line.strip()]
    if ips:
        results = []
        progress_bar = st.progress(0)
        
        for idx, ip in enumerate(ips):
            data = fetch_senderscore_full_report(ip, cookie_input)
            if data:
                results.append(data)
            progress_bar.progress((idx + 1) / len(ips))
            time.sleep(1) # Block aagama irukka konjam delay
            
        res_df = pd.DataFrame(results)
        st.subheader("Results")
        st.dataframe(res_df, use_container_width=True)
        
        csv_file = res_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv_file,
            file_name="senderscore_full_details.csv",
            mime="text/csv"
        )
