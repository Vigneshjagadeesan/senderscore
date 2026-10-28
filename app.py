import streamlit as st
import pandas as pd
import asyncio
from playwright.async_api import async_playwright
import time

st.set_page_config(page_title="Bulk SenderScore Extractor", layout="wide")
st.title("Bulk SenderScore Full Detail Extractor")

async def scrape_ip_details(ip):
    async with async_playwright() as p:
        # Browser launch panrom
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = f"https://senderscore.org/assess/check-your-score/?ip={ip.strip()}"
        try:
            await page.goto(url, timeout=30000)
            await page.wait_for_timeout(4000) # Wait for widgets to load
            
            # Extract Score
            score_elem = await page.query_selector("div.score, div[class*='score']")
            score = await score_elem.inner_text() if score_elem else "N/A"
            
            # Extract Hostname
            host_elem = await page.query_selector("text=Hostname >> xpath=..")
            hostname = await host_elem.inner_text() if host_elem else "N/A"
            hostname = hostname.replace("Hostname", "").strip()
            
            # Extract Volume
            vol_elem = await page.query_selector("text=Volume >> xpath=..")
            volume = await vol_elem.inner_text() if vol_elem else "N/A"
            volume = volume.replace("Volume", "").strip()
            
            await browser.close()
            return {
                "IP": ip.strip(),
                "Sender Score": score.strip(),
                "Hostname": hostname,
                "Volume": volume
            }
        except Exception as e:
            await browser.close()
            return {"IP": ip.strip(), "Sender Score": "Error", "Hostname": str(e), "Volume": "N/A"}

# User Input
ip_input = st.text_area("IPs-ai enter pannunga (One per line):", height=150)

if st.button("Extract Bulk Details"):
    ips = [line.strip() for line in ip_input.split("\n") if line.strip()]
    if ips:
        results = []
        progress_bar = st.progress(0)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for idx, ip in enumerate(ips):
            data = loop.run_until_complete(scrape_ip_details(ip))
            results.append(data)
            progress_bar.progress((idx + 1) / len(ips))
        
        res_df = pd.DataFrame(results)
        st.subheader("Extracted Results")
        st.dataframe(res_df, use_container_width=True)
        
        csv_file = res_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv_file, file_name="senderscore_bulk.csv")
