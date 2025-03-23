import streamlit as st
import pandas as pd
import os

# File path
DATA_PATH = "data/scored_companies.csv"
MESSAGE_COL = "Email Body"
SUBJECT_COL = "Subject"

# Load or create message + subject column
@st.cache_data(ttl=10, show_spinner=False)
def load_data(path):
    df = pd.read_csv(path)
    if MESSAGE_COL not in df.columns:
        df[MESSAGE_COL] = ""
    if SUBJECT_COL not in df.columns:
        df[SUBJECT_COL] = ""
    return df

df = load_data(DATA_PATH)

st.title("LeadFlow AI – Smart Outreach Builder")
st.caption("Curated by Aditi Rani Uppari")

# ---- Filters ----
st.sidebar.header("🔍 Filters")

# Event filter
event_options = sorted(df["Event Name"].dropna().unique())
selected_events = st.sidebar.multiselect("Filter by Event", event_options, default=event_options)

# Fit level filter
fit_options = ["Best Fit", "Mid Fit"]
selected_fits = st.sidebar.multiselect("Filter by Overall Fit", fit_options, default=fit_options)

# Apply filters
filtered_df = df[df["Event Name"].isin(selected_events) & df["Overall Fit"].isin(selected_fits)]

st.write(f"Showing {len(filtered_df)} companies matching your filters.")

# ---- Editable message section per row ----
updated_content = {}

for i, row in filtered_df.iterrows():
    with st.expander(f"{row['Company Name']} ({row['Overall Fit']})"):
        st.markdown(f"**Industry:** {row.get('Industry', 'N/A')}")
        st.markdown(f"**Event:** {row.get('Event Name', 'N/A')}")
        decision_maker = row.get("Decision Maker")
        if pd.isna(decision_maker) or str(decision_maker).strip().lower() == "nan":
            decision_maker_display = "Unavailable"
        else:
            decision_maker_display = decision_maker

        st.markdown(f"**Decision Maker:** {decision_maker_display}")
        st.markdown("---")

        current_subject = row.get(SUBJECT_COL, "")
        new_subject = st.text_input("✏️ Email Subject", value=current_subject, key=f"subj_{i}")

        current_msg = row.get(MESSAGE_COL, "")
        new_msg = st.text_area("✏️ Personalized Message", value=current_msg, key=f"msg_{i}", height=300)

        if new_msg != current_msg or new_subject != current_subject:
            updated_content[row.name] = {
                SUBJECT_COL: new_subject,
                MESSAGE_COL: new_msg
            }

# ---- Save button ----
if updated_content:
    if st.button("💾 Save All Edits"):
        for index, content in updated_content.items():
            df.at[index, SUBJECT_COL] = content[SUBJECT_COL]
            df.at[index, MESSAGE_COL] = content[MESSAGE_COL]
        df.to_csv(DATA_PATH, index=False)
        st.success("✅ Messages and subjects saved!")

# ---- View full filtered table (non-editable) ----
with st.expander("📄 View Filtered Table"):
    st.dataframe(filtered_df.drop(columns=[MESSAGE_COL, SUBJECT_COL], errors="ignore"))