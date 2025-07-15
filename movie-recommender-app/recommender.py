# recommender.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Step 1: Load the movie dataset (must have 'title' and 'genres' columns)
movies = pd.read_csv("movies.csv")

# Step 2: Fill NaN values in 'genres'
movies['genres'] = movies['genres'].fillna('')

# Step 3: Convert genres into TF-IDF vectors
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['genres'])

# Step 4: Compute cosine similarity between all movies
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Step 5: Create reverse mapping (movie title → index)
movie_indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()

# Step 6: Define the recommendation function
def get_similar_movies(title, n=5):
    # Check if title exists in dataset
    if title not in movie_indices:
        return f"❌ Movie '{title}' not found in dataset."
    
    idx = movie_indices[title]
    
    # Get similarity scores for all movies with respect to the input movie
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort movies based on similarity score
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get the indices of the top-n most similar movies (excluding itself at index 0)
    top_indices = [i[0] for i in sim_scores[1:n+1]]
    
    # Return the movie titles
    return movies['title'].iloc[top_indices].tolist()

# Step 7: Test the function
if __name__ == "__main__":
    movie_name = "Toy Story (1995)"  # change as per your dataset
    recommendations = get_similar_movies(movie_name, n=5)
    print(f"Top 5 recommendations for '{movie_name}':")
    for i, rec in enumerate(recommendations, start=1):
        print(f"{i}. {rec}")
