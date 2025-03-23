import pandas as pd

# Load the dataset
df = pd.read_csv("data/agent_enriched_scored_companies.csv")

# Filter companies based on Overall Fit
best_fit_companies = df[df["Overall Fit"] == "Best Fit"]
mid_fit_companies = df[df["Overall Fit"] == "Mid Fit"]

# Message generation function
def generate_message(row, fit_level):
    name = row["Company Name"]
    industry = row["Industry"]
    event = row["Event Name"]
    description = row["Summary"]
    decision_maker = row["Decision Maker"] if pd.notna(row["Decision Maker"]) else "there"
    size = row["EstimatedEmployees"]
    revenue_raw = row["AnnualRevenue"]

    # Handle revenue formatting
    revenue = None
    try:
        revenue = float(str(revenue_raw).replace("$", "").replace(",", "").replace("million", "").replace("billion", "").strip())
    except:
        pass
    revenue_phrase = f"with over ${revenue:,.0f} in annual revenue" if revenue and revenue > 0 else "with a strong global presence"

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

# Apply generation and formatting
all_companies = pd.concat([best_fit_companies, mid_fit_companies])
all_companies["Fit Level"] = all_companies["Overall Fit"].apply(
    lambda x: "strong match" if x == "Best Fit" else "good potential match"
)

all_companies["Message"] = all_companies.apply(lambda row: generate_message(row, row["Fit Level"]), axis=1)
all_companies[["Subject", "Email Body"]] = all_companies.apply(
    lambda row: pd.Series(format_email_template(row, row["Message"])), axis=1
)

# Export to CSV
output_path = "data/agent_enriched_personalized_emails.csv"
all_companies[["Company Name", "Fit Level", "Subject", "Email Body"]].to_csv(output_path, index=False)
print("✅ Personalized email templates saved to:", output_path)
