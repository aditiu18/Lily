import pandas as pd
import openai
import os
from tqdm import tqdm

# Set your OpenAI API key (use dotenv or env vars in prod)
# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = "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"

# Load the scored companies dataset
scored_df = pd.read_csv("scored_companies.csv")
scored_df = scored_df.rename(columns={"Industry Relation": "Industry"})

# Filter companies based on Overall Fit
fit_df = scored_df[scored_df["Overall Fit"].isin(["Best Fit", "Mid Fit", "Low Fit"])].copy()

# Prep for message generation
fit_df["Fit Level"] = fit_df["Overall Fit"].apply(lambda x: "strong match" if x == "Best Fit" else "good potential match")

# GPT message generator
def generate_gpt_message(row):
    name = row["Company Name"]
    industry = row.get("Industry", "")
    event = row.get("Event Name", "")
    description = row.get("Description", "")
    decision_maker = row.get("Decision Maker", "there")
    size = row.get("Size", "")
    revenue = row.get("2024 Revenue USD", "")
    fit_level = row["Fit Level"]

    if pd.isna(decision_maker) or str(decision_maker).strip().lower() == "nan":
        decision_maker = "there"

    revenue_phrase = f"with over ${revenue:,.0f} in annual revenue" if pd.notna(revenue) and revenue > 0 else "with a strong market presence"
    if pd.isna(description) or len(str(description).strip()) < 30:
        description = f"{name} is a notable player in the {industry} industry."
    
    prompt = f"""
Write a concise and professional cold outreach email from Aditi Rani Uppari at DuPont Tedlar to {decision_maker} at {name}, a company in the {industry} industry. The email is about a potential collaboration around weather-resistant graphic film applications.

Details:
- Event: {event}
- Size: {size}
- Revenue: {revenue_phrase}
- Description: {description}
- Fit Level: {fit_level}

The tone should be personalized, professional, and confident. End with a question about meeting or discussing further. It should start with Hi {decision_maker}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful B2B marketing assistant."},
                {"role": "user", "content": prompt.strip()}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating message for {name}: {e}")
        return None

# Generate emails using GPT
tqdm.pandas()
fit_df["Email Body"] = fit_df.progress_apply(generate_gpt_message, axis=1)

# Email subject generator
def generate_subject(row):
    name = row["Company Name"]
    fit = row["Overall Fit"]
    return (
        f"{name} x Trade Show Growth Opportunity" if fit == "Best Fit"
        else f"Let's connect after {name}'s showcase at the event"
    )

fit_df["Subject"] = fit_df.apply(generate_subject, axis=1)

# Merge GPT results back into full dataset
scored_df = scored_df.merge(
    fit_df[["Company Name", "Subject", "Email Body"]],
    on="Company Name",
    how="left"
)

# Save results
output_path = "scored_companies_1.csv"
scored_df.to_csv(output_path, index=False)

