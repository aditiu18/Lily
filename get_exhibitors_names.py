from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from bs4 import BeautifulSoup
import os

def get_rendered_html(url, event_slug):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(5)  # Let JS render content
    html = driver.page_source
    driver.quit()

    # Save HTML for debugging
    debug_path = f"soup_debug_{event_slug}.html"
    with open(debug_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"💾 Saved soup HTML to {debug_path}")

    return html

def extract_exhibitor_names_from_html(html, event_slug):
    soup = BeautifulSoup(html, "html.parser")

    if event_slug in ["isa", "printing_united"]:
        company_spans = soup.select("li.js-Card a")
        return list({span.get_text(strip=True) for span in company_spans})

    elif event_slug == "signuk":
        titles = soup.select(".efp-ehl-items__name")
        return list({el.get_text(strip=True) for el in titles})

    else:
        print(f"⚠️ No extractor defined for slug: {event_slug}")
        return []


# === Event Configs ===
events = [
    {
        "name": "ISA Sign Expo 2025",
        "url": "https://isasignexpo2025.mapyourshow.com/8_0/explore/exhibitor-gallery.cfm?featured=false&categories=1%7C20~~~~1%7C47~~~~1%7C52~~~~1%7C57",
        "slug": "isa"
    },
    {
        "name": "PRINTING United Expo 2025",
        "url": "https://pru25.mapyourshow.com/8_0/explore/exhibitor-gallery.cfm?featured=false",
        "slug": "printing_united"
    },
    {
        "name": "Sign & Digital UK 2025",
        "url": "https://signuk.com/a-z-exhibitor-list/",
        "slug": "signuk"
    }
]

# === Main Runner ===
all_companies = []
for event in events:
    print(f"\n🔍 Processing {event['name']} ...")
    html = get_rendered_html(event["url"], event["slug"])
    companies = extract_exhibitor_names_from_html(html, event["slug"])
    print(f"✅ Found {len(companies)} companies for {event['name']}")
    for name in companies:
        all_companies.append({"Event": event["name"], "Company Name": name})

# Save to CSV
df = pd.DataFrame(all_companies)
df.drop_duplicates(inplace=True)
df.to_csv("all_exhibitors_scraped.csv", index=False)
print("📁 Final output saved to all_exhibitors_scraped.csv")