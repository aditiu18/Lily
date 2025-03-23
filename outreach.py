import openai
import pandas as pd

# Set your OpenAI API Key
openai.api_key = "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"  # Replace with your key, not safe to share publicly

# Load the full CSV file
df = pd.read_csv("scored_companies.csv")

# Prepare list to store messages
messages = []

for _, row in df.iterrows():
    company_name = row['Company Name']
    event = row['Event Name']
    industry = row['Industry Relation']
    revenue = row['2024 Revenue USD']
    decision_maker = row['Decision Maker']
    overall_fit = row['Overall Fit']

    # Construct prompt based on Decision Maker presence
    if pd.notnull(decision_maker):
        prompt = (
            f"Write a concise, friendly outreach email to {decision_maker} at {company_name}, "
            f"who attended {event}. They focus on {industry}. Their revenue in 2024 is ${revenue:.2f}. "
            f"I’m reaching out to explore potential collaborations. Keep it warm, personal, and under 100 words. "
            f"End with Best, DuPont Tedlar"
        )
    else:
        prompt = (
            f"Write a concise, friendly outreach email to the team at {company_name}, who attended {event}. "
            f"They focus on {industry}. Their revenue in 2024 is ${revenue:.2f}. "
            f"I’m reaching out to explore potential collaborations. Keep it under 100 words, warm and approachable. "
            f"End with Best, DuPont Tedlar"
        )

    try:
        # Call GPT-4o to generate message
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150
        )

        outreach_message = response.choices[0].message['content'].strip()
    except Exception as e:
        outreach_message = f"Error generating message: {e}"

    messages.append({
        "Company Name": company_name,
        "Decision Maker": decision_maker if pd.notnull(decision_maker) else "N/A",
        "Overall Fit": overall_fit,
        "Outreach Message": outreach_message
    })

# Create DataFrame from messages
df_output = pd.DataFrame(messages)

# Define custom sort order for Overall Fit
fit_order = {'Best Fit': 0, 'Mid Fit': 1, 'Low Fit': 2}
df_output['Fit Rank'] = df_output['Overall Fit'].map(fit_order)

# Sort by Overall Fit
df_output_sorted = df_output.sort_values(by='Fit Rank').drop(columns=['Fit Rank'])

# Save all messages to CSV
df_output_sorted.to_csv("generated_outreach_messages.csv", index=False)

print("✅ Outreach messages saved to 'generated_outreach_messages.csv' sorted by Overall Fit")
