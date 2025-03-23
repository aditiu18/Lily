import pandas as pd

# Load the scored companies dataset
scored_df = pd.read_csv("data/scored_companies.csv")

# Fix inconsistent column name if needed
scored_df = scored_df.rename(columns={"Industry Relation": "Industry"})

# Filter companies based on Overall Fit
fit_df = scored_df[scored_df["Overall Fit"].isin(["Best Fit", "Mid Fit"])].copy()

# Message generation function
def generate_message(row, fit_level):
    name = row["Company Name"]
    industry = row.get("Industry", "")
    event = row.get("Event Name", "")
    description = row.get("Description", "")
    decision_maker = row.get("Decision Maker")
    if pd.isna(decision_maker) or str(decision_maker).strip().lower() == "nan":
        decision_maker = "there"
    size = row.get("Size", "")
    revenue = row.get("2024 Revenue USD", "")
    revenue_phrase = f"with over ${revenue:,.0f} in annual revenue" if pd.notna(revenue) and revenue > 0 else "with a strong global presence"

    # Shorten or fallback description
    if pd.isna(description) or len(str(description).strip()) < 30:
        description = f"{name} is a notable player in the {industry} industry."
    else:
        description = str(description).strip().split(".")[0] + "."

    # Message
    fit_phrase = "a top-tier fit" if fit_level == "strong match" else "a promising opportunity"

    message = f"""
Hi {decision_maker},

While reviewing exhibitors for {event}, I came across {name}, and your leadership in the {industry} space stood out. From what I’ve gathered, {description} You appear to be a well-established company ({size}, {revenue_phrase}), actively involved in the signage and graphics industry.

We're specifically seeking companies expanding into durable, weather-resistant graphic applications—an area where your innovation clearly aligns. Your involvement in key events like {event} reinforces your commitment to the market.

Given your profile, I believe {name} is {fit_phrase} for a collaboration with DuPont Tedlar. Would you be open to a brief conversation this week?

Best regards,  
Aditi Rani Uppari
"""
    return message.strip()

# Email template formatting
def format_email_template(row, message):
    name = row["Company Name"]
    fit = row["Overall Fit"]
    subject = (
        f"{name} x Trade Show Growth Opportunity" if fit == "Best Fit"
        else f"Let's connect after {name}'s showcase at the event"
    )
    return subject, message

# Apply message generation and formatting
fit_df["Fit Level"] = fit_df["Overall Fit"].apply(lambda x: "strong match" if x == "Best Fit" else "good potential match")
fit_df["Email Body"] = fit_df.apply(lambda row: generate_message(row, row["Fit Level"]), axis=1)
fit_df["Subject"] = fit_df.apply(lambda row: format_email_template(row, row["Email Body"])[0], axis=1)

# Merge personalized fields back into the full scored_df
scored_df = scored_df.merge(
    fit_df[["Company Name", "Subject", "Email Body"]],
    on="Company Name",
    how="left"
)

# Save the updated dataframe
output_path = "data/scored_companies.csv"
scored_df.to_csv(output_path, index=False)