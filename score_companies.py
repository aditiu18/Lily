import pandas as pd

# Load CSV
df = pd.read_csv("Enriched-companies.csv")

# Define function to score industry relation
def score_industry(industry):
    industry = str(industry).lower()
    if any(keyword in industry for keyword in ['signage', 'graphics', 'wrap']):
        return 'Best Fit'
    elif any(keyword in industry for keyword in ['tools', 'technology', 'printing', 'films']):
        return 'Mid Fit'
    else:
        return 'Low Fit'

# Define function to score employee size
def score_size(size_str):
    try:
        size_parts = size_str.replace('+', '').split('-')
        min_size = int(size_parts[0])
        if min_size >= 500:
            return 'Best Fit'
        elif 50 <= min_size < 500:
            return 'Mid Fit'
        else:
            return 'Low Fit'
    except:
        return 'Low Fit'

# Define function to score revenue
def score_revenue(revenue):
    try:
        revenue = float(revenue)
        if revenue >= 100_000_000:
            return 'Best Fit'
        elif 10_000_000 <= revenue < 100_000_000:
            return 'Mid Fit'
        else:
            return 'Low Fit'
    except:
        return 'Low Fit'

# Apply scoring functions
df['Industry Fit'] = df['Industry Relation'].apply(score_industry)
df['Size Fit'] = df['Size'].apply(score_size)
df['Revenue Fit'] = df['2024 Revenue USD'].apply(score_revenue)

# Combine scores to determine overall fit
def overall_fit(row):
    scores = [row['Industry Fit'], row['Size Fit'], row['Revenue Fit']]
    if scores.count('Best Fit') >= 2:
        return 'Best Fit'
    elif scores.count('Mid Fit') >= 2:
        return 'Mid Fit'
    else:
        return 'Low Fit'

df['Overall Fit'] = df.apply(overall_fit, axis=1)

# Save results to CSV
df.to_csv("scored_companies.csv", index=False)

print("Done! Results saved to 'scored_companies.csv'")
