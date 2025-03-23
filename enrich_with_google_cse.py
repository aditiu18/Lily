
import os
import time
import random
import pandas as pd
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_community.chat_models import ChatOpenAI

# === CONFIG ===
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "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")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBYRkAUkUmq7NuSu_BDrjfPmasGsKgMOqc")
CSE_ID = "262f73e19222d4659"  # Your CSE ID

llm = ChatOpenAI(temperature=0, model="gpt-4o")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)"
]

# === GOOGLE SEARCH ===
def google_search(query, api_key=GOOGLE_API_KEY, cse_id=CSE_ID, max_results=3):
    try:
        service = build("customsearch", "v1", developerKey=api_key)
        response = service.cse().list(q=query, cx=cse_id, num=max_results).execute()
        return [item["link"] for item in response.get("items", [])]
    except Exception as e:
        return [f"Error during search: {e}"]

# === SCRAPER ===
def scrape_url(url: str) -> str:
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        res = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        return text[:3000]
    except Exception as e:
        return f"Scraping failed: {e}"

scrape_tool = Tool(
    name="ScrapeURL",
    func=scrape_url,
    description="Scrapes a given URL and returns raw text."
)

# === AGENT ===
agent = initialize_agent(
    tools=[scrape_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10,  # increase from default 3
    max_execution_time=500  # allow more time per company
)

# === MAIN ENRICHMENT LOOP ===
df = pd.read_csv("data/scored_companies.csv")
results = []

for company in tqdm(df["Company Name"]):
    try:
        print(f"🔍 {company}")
        homepage_url, linkedin_url = None, None

        links = google_search(f"{company} site:linkedin.com OR site:{company.lower().replace(' ', '')}.com")
        for link in links:
            if "linkedin.com/company" in link and not linkedin_url:
                linkedin_url = link
            elif "http" in link and not homepage_url:
                homepage_url = link

        linkedin_text = scrape_url(linkedin_url) if linkedin_url else ""
        time.sleep(2)
        homepage_text = scrape_url(homepage_url) if homepage_url else ""
        combined_text = f"{homepage_text}\n\n{linkedin_text}".strip()

        prompt = f"""
You are an expert business analyst enriching company metadata for a B2B outbound system.

Company: **{company}**

You are given raw text from both the company’s homepage and LinkedIn profile.

🎯 Your goal is to extract structured metadata and determine why this company may be a good fit for signage or durable film products (e.g. DuPont™ Tedlar®).

Return ONLY this JSON (no explanations):

{{
  "Industry": "...",
  "EstimatedEmployees": "...",
  "AnnualRevenue": "...",
  "Summary": "...",
  "Rationale": "..."
}}

✅ Estimate intelligently if numbers aren't available.
✅ Use context clues (e.g. if they do signage, printing, wraps, etc.)

Here is the combined text:
{combined_text}
"""

        output = agent.run(prompt)
        results.append({
            "Company Name": company,
            "Homepage URL": homepage_url or "N/A",
            "LinkedIn URL": linkedin_url or "N/A",
            "Enrichment": output
        })
    except Exception as e:
        results.append({
            "Company Name": company,
            "Homepage URL": "Error",
            "LinkedIn URL": "Error",
            "Enrichment": f"Error: {str(e)}"
        })
    time.sleep(2)

# === SAVE OUTPUT ===
df_out = pd.DataFrame(results)
df_out.to_csv("scored_exhibitors_enriched_outputs.csv", index=False)
print("✅ Done! Results saved.")
