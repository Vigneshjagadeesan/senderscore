import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# Check panna vendiya IPs
ips_to_check = [
    "142.0.85.188",
    "134.128.99.186"
]

# Headless Chrome Browser setup
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

results = []

for ip in ips_to_check:
    print(f"Checking IP: {ip}...")
    url = f"https://senderscore.org/assess/get-your-score/report/?lookup={ip}&authenticated=true"
    driver.get(url)
    
    # Page render aaga wait panrom
    time.sleep(6)
    
    # Score extract panrom
    score = "N/A"
    try:
        score_elem = driver.find_element(By.CSS_SELECTOR, "div.score, div[class*='score']")
        score = score_elem.text.strip()
    except Exception:
        pass
        
    # Sending Domains extract panrom
    domains_list = []
    try:
        domain_elements = driver.find_elements(By.XPATH, "//div[contains(text(), 'Sending Domains')]/following::div//a | //div[contains(text(), 'Sending Domains')]/following::div//span")
        for elem in domain_elements:
            txt = elem.text.strip()
            if "." in txt and " " not in txt and txt.lower() not in ["next", "previous", "domain"]:
                domains_list.append(txt)
    except Exception:
        pass
    
    domains_list = list(dict.fromkeys(domains_list))
    
    results.append({
        "IP Address": ip,
        "Sender Score": score,
        "Sending Domains": ", ".join(domains_list) if domains_list else "None Found"
    })

driver.quit()

# Output CSV
df = pd.DataFrame(results)
df.to_csv("senderscore_bulk_results.csv", index=False)
print("Success! File saved as senderscore_bulk_results.csv")
