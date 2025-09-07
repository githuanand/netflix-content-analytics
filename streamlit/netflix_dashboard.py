import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.express as px
import io

# ---------------------------
# Load Data
# ---------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")
    return df

df = load_data()

st.title("🎬 Netflix Interactive Analytics Dashboard")

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

# Apply filters
filtered_df = df[
    (df['type'].isin(content_type)) &
    (df['release_year'] >= year_range[0]) &
    (df['release_year'] <= year_range[1])
]

if 'listed_in' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['listed_in'].str.contains('|'.join(selected_genres), na=False)]
if 'director' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['director'].str.contains('|'.join(selected_directors), na=False)]
if 'country' in filtered_df.columns:
    filtered_df = filtered_df[filtered_df['country'].str.contains('|'.join(selected_countries), na=False)]

# ---------------------------
# Summary Metrics
# ---------------------------
st.markdown("### Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Titles", filtered_df.shape[0])
col2.metric("Movies", filtered_df[filtered_df['type']=='Movie'].shape[0])
col3.metric("TV Shows", filtered_df[filtered_df['type']=='TV Show'].shape[0])

# ---------------------------
# Duration Scatter Plot (Interactive)
# ---------------------------
if 'duration' in filtered_df.columns:
    filtered_df['duration_num'] = filtered_df['duration'].str.extract(r'(\d+)').astype(float)
    fig1 = px.scatter(
        filtered_df,
        x='release_year',
        y='duration_num',
        color='type',
        hover_data=['title', 'rating', 'director', 'country'],
        title="📈 Content Duration by Year",
        labels={'duration_num':'Duration'}
    )
    st.plotly_chart(fig1, use_container_width=True)

# ---------------------------
# Top Genres (Interactive)
# ---------------------------
st.markdown("### Top Genres")
if 'listed_in' in filtered_df.columns:
    genres_series = filtered_df['listed_in'].str.split(', ').explode()
    top_genres = genres_series.value_counts().head(10)
    fig2 = px.bar(
        x=top_genres.values,
        y=top_genres.index,
        orientation='h',
        title="Top 10 Genres",
        labels={'x':'Number of Titles','y':'Genre'},
        color=top_genres.values,
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# Top Directors (Interactive)
# ---------------------------
st.markdown("### Top Directors")
if 'director' in filtered_df.columns:
    directors_series = filtered_df['director'].dropna().str.split(', ').explode()
    top_directors = directors_series.value_counts().head(10)
    fig3 = px.bar(
        x=top_directors.values,
        y=top_directors.index,
        orientation='h',
        title="Top 10 Directors",
        labels={'x':'Number of Titles','y':'Director'},
        color=top_directors.values,
        color_continuous_scale='Magma'
    )
    st.plotly_chart(fig3, use_container_width=True)

# ---------------------------
# Ratings Distribution
# ---------------------------
st.markdown("### Ratings Distribution")
if 'rating' in filtered_df.columns:
    rating_counts = filtered_df['rating'].value_counts()
    fig4 = px.bar(
        x=rating_counts.values,
        y=rating_counts.index,
        orientation='h',
        title="Ratings Distribution",
        labels={'x':'Number of Titles','y':'Rating'},
        color=rating_counts.values,
        color_continuous_scale='Cividis'
    )
    st.plotly_chart(fig4, use_container_width=True)

# ---------------------------
# Country-wise Titles (Interactive)
# ---------------------------
st.markdown("### Top Countries")
if 'country' in filtered_df.columns:
    country_series = filtered_df['country'].dropna().str.split(', ').explode()
    top_countries = country_series.value_counts().head(10)
    fig5 = px.bar(
        x=top_countries.values,
        y=top_countries.index,
        orientation='h',
        title="Top 10 Countries",
        labels={'x':'Number of Titles','y':'Country'},
        color=top_countries.values,
        color_continuous_scale='Turbo'
    )
    st.plotly_chart(fig5, use_container_width=True)

# ---------------------------
# WordCloud of Titles
# ---------------------------
st.markdown("### WordCloud of Titles")
text = " ".join(filtered_df['title'].dropna())
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

plt.figure(figsize=(15, 7))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
st.pyplot(plt.gcf())

# ---------------------------
# Download Filtered Data
# ---------------------------
st.markdown("### Download Filtered Data")
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(filtered_df)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='filtered_netflix_data.csv',
    mime='text/csv',
)
