import streamlit as st
import pandas as pd
import requests
import re
from recommender import get_similar_movies

# TMDb API key
TMDB_API_KEY = "87ec5cda7883437062606f8416dbe8db"

# Load dataset
movies = pd.read_csv("movies.csv")
movie_list = movies['title'].sort_values().unique()

# Set page config
st.set_page_config(page_title="Movie Recommender", layout="wide")

# Session state for favorites
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# CSS for styling
st.markdown("""
    <style>
    .movie-box {
        border: 2px solid #4A90E2;
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        background-color: #f0f8ff;
        transition: 0.3s;
        cursor: pointer;
        font-size: 18px;
            color: black;
    }
    .movie-box:hover {
        background-color: #e0efff;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        transform: scale(1.02);
    }
    a {
        text-decoration: none;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Helper: Clean title & fetch poster, rating, overview ---
def fetch_movie_data(title_with_year):
    match = re.match(r"^(.*?)\s*\(\d{4}\)$", title_with_year)
    clean_title = match.group(1) if match else title_with_year

    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": clean_title
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            movie = data["results"][0]
            poster_path = movie.get("poster_path")
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
            rating = movie.get("vote_average", "N/A")
            overview = movie.get("overview", "No overview available.")
            return poster_url, rating, overview
    return "", "N/A", "No overview available."

# --- UI Header ---
st.title("🎬 Movie Recommendation System")
st.markdown("Select a movie to get similar genre-based recommendations.")

# Movie selector
movie_name = st.selectbox("🎥 Choose a movie:", movie_list)

# Recommend
if st.button("🎯 Recommend"):
    recommendations = get_similar_movies(movie_name)

    if isinstance(recommendations, str):
        st.error(recommendations)
    else:
        st.subheader("📽️ Recommended Movies:")

        cols = st.columns(2)  # 2-column layout
        for i, rec in enumerate(recommendations):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f'<div class="movie-box">{rec}</div>', unsafe_allow_html=True)

                    with st.expander("Show more details"):
                        # Fetch TMDb data
                        poster_url, rating, overview = fetch_movie_data(rec)

                        if poster_url:
                            st.image(poster_url, width=250)
                        else:
                            st.image("https://m.media-amazon.com/images/I/81-349iYbfL._AC_SY679_.jpg", width=250)

                        st.write(f"**Rating:** {rating}")
                        st.write(f"**Overview:** {overview}")

                        # Show dataset info
                        details = movies[movies['title'] == rec]
                        if not details.empty:
                            row = details.iloc[0]
                            for col in details.columns:
                                st.write(f"**{col.capitalize()}:** {row[col]}")

                        # IMDb & Google search
                        query = rec.replace(" ", "+")
                        st.markdown(f"""
                            <br>
                            <a href="https://www.google.com/search?q={query}+movie" target="_blank">🌐 Google</a><br>
                            <a href="https://www.imdb.com/find?q={query}" target="_blank">🎥 IMDb</a>
                        """, unsafe_allow_html=True)

                        # Save to favorites
                        if st.button(f"❤️ Save to Favorites", key=f"fav_{i}"):
                            if rec not in st.session_state.favorites:
                                st.session_state.favorites.append(rec)
                                st.success(f"'{rec}' added to favorites!")
                        
# --- Favorites Display ---
                        # --- Show favorites on main page ---
if st.session_state.favorites:
    st.markdown("---")
    st.subheader("⭐ Your Saved Favorites")
    
    for fav in st.session_state.favorites:
        st.markdown(f"✅ {fav}")
