import pandas as pd
import json

# ------------------------------
# Step 0: Load datasets
# ------------------------------
scored_path = "data/scored_companies.csv"
enriched_path = "data/agent_enriched_exhibitors.csv"

scored_df = pd.read_csv(scored_path)
enriched_df = pd.read_csv(enriched_path)

# ------------------------------
# Step 1: Parse JSON from Enrichment column
# ------------------------------
def parse_enrichment(json_str):
    try:
        json_str = json_str.strip().strip('```json').strip('```').strip()
        data = json.loads(json_str)
        return pd.Series({
            "Industry": data.get("Industry"),
            "EstimatedEmployees": data.get("EstimatedEmployees"),
            "AnnualRevenue": data.get("AnnualRevenue"),
            "Summary": data.get("Summary"),
            "Rationale": data.get("Rationale")
        })
    except:
        return pd.Series({
            "Industry": None,
            "EstimatedEmployees": None,
            "AnnualRevenue": None,
            "Summary": None,
            "Rationale": None
        })

parsed_cols = enriched_df["Enrichment"].apply(parse_enrichment)
enriched_df = pd.concat([enriched_df, parsed_cols], axis=1)

# ------------------------------
# Step 2: Add missing decision makers and event names
# ------------------------------
# Create lookup dictionaries
decision_maker_lookup = scored_df.set_index("Company Name")["Decision Maker"].to_dict()
event_lookup = scored_df.set_index("Company Name")["Event Name"].to_dict()

# Function to fill missing fields from scored_df
def enrich_row(row):
    company = row["Company Name"]
    decision_maker = row.get("Decision Maker", "")
    event_name = row.get("Event Name", "")

    return pd.Series({
        "Decision Maker": decision_maker if pd.notna(decision_maker) and str(decision_maker).strip() else decision_maker_lookup.get(company),
        "Event Name": event_name if pd.notna(event_name) and str(event_name).strip() else event_lookup.get(company)
    })


# Apply enrichment
enriched_df[["Decision Maker", "Event Name"]] = enriched_df.apply(enrich_row, axis=1)

# ------------------------------
# Step 3: Fit scoring functions
# ------------------------------
def score_industry(industry):
    industry = str(industry).lower()
    if any(keyword in industry for keyword in ['signage', 'graphics', 'wrap']):
        return 'Best Fit'
    elif any(keyword in industry for keyword in ['tools', 'technology', 'printing', 'films']):
        return 'Mid Fit'
    else:
        return 'Low Fit'

def score_size(size_str):
    try:
        size_str = str(size_str).replace("+", "").replace(",", "")
        size_parts = size_str.split("-")
        min_size = int(size_parts[0])
        if min_size >= 500:
            return 'Best Fit'
        elif 50 <= min_size < 500:
            return 'Mid Fit'
        else:
            return 'Low Fit'
    except:
        return 'Low Fit'

def score_revenue(revenue_str):
    try:
        revenue_str = str(revenue_str).lower().replace("$", "").replace(",", "")
        revenue_str = revenue_str.replace("million", "").replace("billion", "").strip()
        if "not available" in revenue_str or revenue_str == "":
            return 'Low Fit'
        if "b" in revenue_str:
            return 'Best Fit'
        revenue = float(revenue_str)
        if revenue >= 100:
            return 'Best Fit'
        elif 10 <= revenue < 100:
            return 'Mid Fit'
        else:
            return 'Low Fit'
    except:
        return 'Low Fit'

enriched_df["Industry Fit"] = enriched_df["Industry"].apply(score_industry)
enriched_df["Size Fit"] = enriched_df["EstimatedEmployees"].apply(score_size)
enriched_df["Revenue Fit"] = enriched_df["AnnualRevenue"].apply(score_revenue)

# ------------------------------
# Step 4: Compute overall fit
# ------------------------------
def overall_fit(row):
    scores = [row["Industry Fit"], row["Size Fit"], row["Revenue Fit"]]
    if scores.count("Best Fit") >= 2:
        return "Best Fit"
    elif scores.count("Mid Fit") >= 2:
        return "Mid Fit"
    else:
        return "Low Fit"

enriched_df["Overall Fit"] = enriched_df.apply(overall_fit, axis=1)

# ------------------------------
# Step 5: Save enriched + scored file
# ------------------------------
output_path = "data/agent_enriched_scored_companies.csv"
enriched_df.to_csv(output_path, index=False)
print(f"✅ Done! File saved to: {output_path}")