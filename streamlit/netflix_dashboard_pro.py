import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.express as px

# ---------------------------
# Load Data
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    return df

df = load_data()

st.set_page_config(
    page_title="Netflix Analytics Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎬 Netflix Analytics Dashboard")

# ---------------------------
# Sidebar Filters
# ---------------------------
st.sidebar.header("Filters")

# Content Type
content_type = st.sidebar.multiselect(
    "Select Content Type",
    options=df['type'].unique(),
    default=df['type'].unique()
)

# Year Range
min_year = int(df['release_year'].min())
max_year = int(df['release_year'].max())
year_range = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))

# Genres
all_genres = df['listed_in'].dropna().str.split(', ').explode().unique()
selected_genres = st.sidebar.multiselect(
    "Select Genres",
    options=all_genres,
    default=all_genres
)

# Directors
all_directors = df['director'].dropna().str.split(', ').explode().unique()
selected_directors = st.sidebar.multiselect(
    "Select Directors",
    options=all_directors,
    default=all_directors
)

# Countries
all_countries = df['country'].dropna().str.split(', ').explode().unique()
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=all_countries,
    default=all_countries
)

# ---------------------------
# Apply Filters
# ---------------------------
filtered_df = df[
    (df['type'].isin(content_type)) &
    (df['release_year'] >= year_range[0]) &
    (df['release_year'] <= year_range[1])
].copy()

if 'listed_in' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['listed_in'].str.contains('|'.join(selected_genres), na=False)]
if 'director' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['director'].str.contains('|'.join(selected_directors), na=False)]
if 'country' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['country'].str.contains('|'.join(selected_countries), na=False)]

# ---------------------------
# Summary Metrics
# ---------------------------
st.markdown("### 📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Titles", filtered_df.shape[0])
col2.metric("Movies", filtered_df[filtered_df['type']=='Movie'].shape[0])
col3.metric("TV Shows", filtered_df[filtered_df['type']=='TV Show'].shape[0])
col4.metric("Unique Directors", filtered_df['director'].nunique())

# ---------------------------
# Tabs
# ---------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Genres & Directors", "Ratings", "Countries", "WordCloud & Download"])

# ---------------------------
# Tab 1: Overview
# ---------------------------
with tab1:
    st.markdown("### 📈 Content Duration by Year")
    if 'duration' in filtered_df.columns and not filtered_df.empty:
        filtered_df['duration_num'] = filtered_df['duration'].str.extract(r'(\d+)').astype(float)
        fig = px.scatter(
            filtered_df,
            x='release_year',
            y='duration_num',
            color='type',
            hover_data=['title', 'rating', 'director', 'country'],
            title="Content Duration by Year",
            labels={'duration_num':'Duration (min)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

# ---------------------------
# Tab 2: Genres & Directors
# ---------------------------
with tab2:
    st.markdown("### Top Genres")
    if 'listed_in' in filtered_df.columns and not filtered_df.empty:
        genres_series = filtered_df['listed_in'].str.split(', ').explode()
        top_genres = genres_series.value_counts().head(10)
        fig = px.bar(
            x=top_genres.values,
            y=top_genres.index,
            orientation='h',
            color=top_genres.values,
            color_continuous_scale='Viridis',
            labels={'x':'Number of Titles', 'y':'Genre'},
            title="Top 10 Genres"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No genre data to display.")

    st.markdown("### Top Directors")
    if 'director' in filtered_df.columns and not filtered_df.empty:
        directors_series = filtered_df['director'].dropna().str.split(', ').explode()
        top_directors = directors_series.value_counts().head(10)
        fig = px.bar(
            x=top_directors.values,
            y=top_directors.index,
            orientation='h',
            color=top_directors.values,
            color_continuous_scale='Magma',
            labels={'x':'Number of Titles', 'y':'Director'},
            title="Top 10 Directors"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No director data to display.")

# ---------------------------
# Tab 3: Ratings
# ---------------------------
with tab3:
    st.markdown("### Ratings Distribution")
    if 'rating' in filtered_df.columns and not filtered_df.empty:
        rating_counts = filtered_df['rating'].value_counts()
        fig = px.bar(
            x=rating_counts.values,
            y=rating_counts.index,
            orientation='h',
            color=rating_counts.values,
            color_continuous_scale='Cividis',
            labels={'x':'Number of Titles','y':'Rating'},
            title="Ratings Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No rating data to display.")

# ---------------------------
# Tab 4: Countries
# ---------------------------
with tab4:
    st.markdown("### Top Countries")
    if 'country' in filtered_df.columns and not filtered_df.empty:
        country_series = filtered_df['country'].dropna().str.split(', ').explode()
        top_countries = country_series.value_counts().head(10)
        fig = px.bar(
            x=top_countries.values,
            y=top_countries.index,
            orientation='h',
            color=top_countries.values,
            color_continuous_scale='Turbo',
            labels={'x':'Number of Titles','y':'Country'},
            title="Top 10 Countries by Content"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No country data to display.")

# ---------------------------
# Tab 5: WordCloud & Download
# ---------------------------
with tab5:
    st.markdown("### WordCloud of Titles")
    text = " ".join(filtered_df['title'].dropna())
    if text.strip():
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        plt.figure(figsize=(15,7))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(plt.gcf())
    else:
        st.warning("No titles available to generate WordCloud.")

    st.markdown("### Download Filtered Data")
    if not filtered_df.empty:
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="filtered_netflix_data.csv",
            mime="text/csv"
        )
    else:
        st.info("No data to download for the selected filters.")
