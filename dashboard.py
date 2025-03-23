import streamlit as st
import pandas as pd

# --- Load Data ---
# Load scored company data for rationale
df_scored = pd.read_csv("scored_companies.csv")

# Load generated outreach messages
df_messages = pd.read_csv("generated_outreach_messages.csv")

# Merge messages with company data for rationale
df = pd.merge(
    df_messages,
    df_scored[['Company Name', 'Event Name', 'Industry Relation',
               '2024 Revenue USD', 'Size', 'Decision Maker', 'Overall Fit']],
    on='Company Name',
    how='left'
)

# Clean column names
df.columns = df.columns.str.strip()

# --- Generate Concise Rationale ---
def generate_short_rationale(row):
    industry_summary = row['Industry Relation']

    # Revenue tier
    revenue = row['2024 Revenue USD']
    if pd.isnull(revenue):
        revenue_tier = "unknown revenue"
    elif revenue >= 100_000_000:
        revenue_tier = "large revenue"
    elif revenue >= 10_000_000:
        revenue_tier = "mid-sized revenue"
    else:
        revenue_tier = "small revenue"

    # Event participation summary
    event_summary = f"exhibits at {row['Event Name']}" if pd.notnull(row['Event Name']) else "no event data"

    return f"Specializes in {industry_summary}; {revenue_tier}; {event_summary}."

# --- Streamlit Dashboard UI ---
st.title("📊 DuPont Tedlar Outreach Dashboard")
st.markdown("Review, edit, and export personalized outreach messages with strategic rationale.")

# Search bar
search = st.text_input("🔍 Search by Company Name or Decision Maker")

if search:
    df_display = df[df['Company Name'].str.contains(search, case=False, na=False) |
                    df['Decision Maker'].fillna("").str.contains(search, case=False, na=False)]
else:
    df_display = df

# Message editing and rationale display
for index, row in df_display.iterrows():
    st.markdown(f"### {row['Company Name']} ({row.get('Overall Fit_x', 'N/A')})")
    st.markdown(f"**Decision Maker:** {row.get('Decision Maker_x', 'N/A')}")
    st.markdown(f"**Event:** {row.get('Event Name', 'N/A')}")

    # Show concise rationale
    rationale = generate_short_rationale(row)
    st.markdown(f"**Rationale for Qualification:** {rationale}")

    # Editable outreach message
    message = st.text_area("✉️ Outreach Message", row['Outreach Message'], key=f"msg_{index}")
    df.at[index, 'Outreach Message'] = message

    # Ready to send checkbox
    ready_to_send = st.checkbox("✅ Ready to Send", key=f"send_{index}")
    df.at[index, 'Ready to Send'] = "Yes" if ready_to_send else "No"

    st.markdown("---")

# --- Download Updated CSV ---
csv_data = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Messages + Rationale CSV",
    data=csv_data,
    file_name='updated_outreach_messages_with_rationale.csv',
    mime='text/csv'
)
