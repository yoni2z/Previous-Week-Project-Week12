import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml

st.set_page_config(page_title="Fintech Review Analytics", layout="wide")

def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

st.title("Fintech App Review Analytics Dashboard")
st.markdown("Analyze Google Play reviews for Ethiopian banks to improve customer satisfaction.")

# Load data
config = load_config()
banks = list(config['bank_names'].values())
df = pd.read_csv('data/insights/review_analysis.csv')

# Filters
col1, col2 = st.columns(2)
with col1:
    selected_bank = st.selectbox("Select Bank", ["All"] + banks)
with col2:
    rating_filter = st.slider("Filter by Rating", 1, 5, (1, 5))

# Filter data
filtered_df = df if selected_bank == "All" else df[df['bank_name'] == selected_bank]
filtered_df = filtered_df[filtered_df['rating'].between(rating_filter[0], rating_filter[1])]

# Display metrics
st.subheader("Summary Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Average Rating", f"{filtered_df['rating'].mean():.2f}")
col2.metric("Average Sentiment Score", f"{filtered_df['sentiment_score'].mean():.2f}")
col3.metric("Total Reviews", len(filtered_df))

# Visualizations
st.subheader("Visualizations")
tab1, tab2, tab3 = st.tabs(["Sentiment", "Ratings", "Themes"])

with tab1:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.countplot(data=filtered_df, x='sentiment_label', ax=ax)
    ax.set_title('Sentiment Distribution')
    st.pyplot(fig)

with tab2:
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.histplot(data=filtered_df, x='rating', bins=5, ax=ax)
    ax.set_title('Rating Distribution')
    st.pyplot(fig)

with tab3:
    themes_df = filtered_df.explode('themes')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(data=themes_df, y='themes', ax=ax)
    ax.set_title('Theme Frequency')
    st.pyplot(fig)

# Sample Reviews
st.subheader("Sample Reviews")
st.dataframe(filtered_df[['review_text', 'rating', 'sentiment_label', 'themes']].head(10))