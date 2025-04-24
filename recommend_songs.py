import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from collections import defaultdict
import joblib
import os
import warnings
warnings.filterwarnings("ignore")
# Numerical features used for song recommendations
number_cols = ['valence', 'year', 'acousticness', 'danceability', 'duration_ms', 'energy', 'explicit',
               'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'popularity', 'speechiness', 'tempo']
        
# Note: The pipeline definition has been moved to the model training file
# The fitted scaler is now loaded from a saved file

def get_song_data(song, spotify_data):
    """
    Fetches song details from the provided dataset.
    
    Args:
        song (dict): Dictionary containing song name and year
        spotify_data (pd.DataFrame): DataFrame containing Spotify song data
        
    Returns:
        dict: Dictionary containing the following keys:
            - success (bool): True if operation succeeded, False otherwise
            - data (pd.Series or None): Song data if found
            - error_message (str or None): Error message if any
            - error_code (int or None): Error code for frontend handling
    """
    try:
        song_data = spotify_data[(spotify_data['name'] == song['name']) 
                               & (spotify_data['year'] == song['year'])].iloc[0]
        print(f"Fetching song information for '{song['name']}' from local dataset")
        return {
            'success': True,
            'data': song_data,
            'error_message': None,
            'error_code': None
        }
    except IndexError:
        error_message = f"Song '{song['name']}' from {song['year']} doesn't exist in dataset"
        print(error_message)
        return {
            'success': False,
            'data': None,
            'error_message': error_message,
            'error_code': 404  # Not found
        }
    except Exception as e:
        error_message = f"Error fetching song data: {str(e)}"
        print(error_message)
        return {
            'success': False,
            'data': None,
            'error_message': error_message,
            'error_code': 500  # General error
        }


def get_mean_vector(song_list, spotify_data):
    """
    Calculates the mean vector of numerical features for a list of songs.
    
    Args:
        song_list (list): List of dictionaries containing song information (name, year)
        spotify_data (pd.DataFrame): DataFrame containing Spotify data
        
    Returns:
        dict: Dictionary containing the following keys:
            - success (bool): True if operation succeeded, False otherwise
            - data (np.ndarray or None): Mean vector if calculated successfully
            - error_message (str or None): Error message if any
            - error_code (int or None): Error code for frontend handling
    """
    song_vectors = []
    missing_songs = []
    
    # Collect feature vectors for each song in the list
    for song in song_list:
        result = get_song_data(song, spotify_data)
        if not result['success']:
            missing_songs.append(song['name'])
            continue
            
        song_data = result['data']
        song_vector = song_data[number_cols].values
        song_vectors.append(song_vector)
    
    # Calculate mean vector if we have at least one valid song
    if len(song_vectors) >= 1:
        # Create matrix from all song vectors and calculate column-wise mean
        song_matrix = np.array(list(song_vectors))
        mean_vector = np.mean(song_matrix, axis=0)
        
        return {
            'success': True,
            'data': mean_vector,
            'error_message': None if not missing_songs else f"Some songs were not found: {', '.join(missing_songs)}",
            'error_code': None if not missing_songs else 206  # Partial content
        }
    else:
        return {
            'success': False,
            'data': None,
            'error_message': "None of the songs exist in the dataset",
            'error_code': 404  # Not found
        }


def flatten_dict_list(dict_list):
    """
    Flattens a list of dictionaries into a dictionary of lists.
    
    Args:
        dict_list (list): List of dictionaries with the same keys
        
    Returns:
        dict: Dictionary with keys from the original dictionaries and values as lists of values
    """
    flattened_dict = defaultdict(list)
    
    # Initialize the dictionary with empty lists for each key in the first dictionary
    for key in dict_list[0].keys():
        flattened_dict[key] = []
        
    # Append values from each dictionary to the corresponding list
    for dic in dict_list:
        for key, value in dic.items():
            flattened_dict[key].append(value)
            
    return flattened_dict


def recommend_songs(song_list, spotify_data, n_songs=10, scaler_path='models/standard_scaler.pkl', 
                   kmeans_path='models/kmeans_model.pkl', use_clusters=False):
    """
    Recommends songs based on the input song list using cosine similarity.
    
    Args:
        song_list (list): List of dictionaries containing song information (name, year)
        spotify_data (pd.DataFrame): DataFrame containing Spotify data
        n_songs (int, optional): Number of songs to recommend. Defaults to 10.
        scaler_path (str, optional): Path to the saved StandardScaler model. Defaults to 'models/standard_scaler.pkl'.
        kmeans_path (str, optional): Path to the saved KMeans model. Defaults to 'models/kmeans_model.pkl'.
        use_clusters (bool, optional): Whether to use KMeans clusters to filter recommendations. Defaults to False.
        
    Returns:
        dict: Dictionary containing the following keys:
            - success (bool): True if operation succeeded, False otherwise
            - data (list): List of recommended songs if successful
            - error_message (str or None): Error message if any
            - error_code (int or None): Error code for frontend handling
    """
    try:
        # Metadata columns to include in the recommendations
        metadata_cols = ['name', 'year', 'artists']
        
        # Flatten the song list for easier processing
        song_dict = flatten_dict_list(song_list)
        
        # Get the center point of the input songs in the feature space
        mean_vector_result = get_mean_vector(song_list, spotify_data)
        if not mean_vector_result['success']:
            return {
                'success': False,
                'data': [],
                'error_message': mean_vector_result['error_message'],
                'error_code': mean_vector_result['error_code']
            }
        
        song_center = mean_vector_result['data']
        
        # Load the pre-trained scaler from file
        try:
            scaler = joblib.load(scaler_path)
            print(f"Successfully loaded scaler from {scaler_path}")
        except Exception as e:
            error_message = f"Error loading scaler from {scaler_path}: {str(e)}"
            print(f"Warning: {error_message}")
            print("Falling back to a new StandardScaler (Note: this may affect recommendation quality)")
            scaler = StandardScaler()
            scaler.fit(spotify_data[number_cols])
        
        # Scale the data and song center
        scaled_data = scaler.transform(spotify_data[number_cols])
        scaled_song_center = scaler.transform(song_center.reshape(1, -1))
        
        # If using clusters for filtering recommendations
        if use_clusters:
            try:
                # Load the pre-trained KMeans model
                kmeans = joblib.load(kmeans_path)
                print(f"Successfully loaded KMeans from {kmeans_path}")
                
                # Predict cluster for the song center
                cluster = kmeans.predict(scaled_song_center)[0]
                print(f"Input songs belong to cluster {cluster}")
                
                # Get songs from the same cluster
                if 'cluster' not in spotify_data.columns:
                    # Predict clusters for all songs if not already present
                    clusters = kmeans.predict(scaled_data)
                    spotify_data_with_clusters = spotify_data.copy()
                    spotify_data_with_clusters['cluster'] = clusters
                else:
                    spotify_data_with_clusters = spotify_data
                
                # Filter songs from the same cluster
                cluster_songs = spotify_data_with_clusters[spotify_data_with_clusters['cluster'] == cluster]
                
                # If we found enough songs in the cluster
                if len(cluster_songs) >= n_songs:
                    # Calculate distances within the cluster
                    cluster_scaled_data = scaler.transform(cluster_songs[number_cols])
                    distances = cdist(scaled_song_center, cluster_scaled_data, 'cosine')
                    index = list(np.argsort(distances)[:, :n_songs][0])
                    
                    # Get recommendations from the cluster
                    rec_songs = cluster_songs.iloc[index]
                    rec_songs = rec_songs[~rec_songs['name'].isin(song_dict['name'])]
                    recommendations = rec_songs[metadata_cols].to_dict(orient='records')
                    
                    return {
                        'success': True,
                        'data': recommendations,
                        'error_message': None,
                        'error_code': None
                    }
                else:
                    print(f"Not enough songs in cluster {cluster}, falling back to regular recommendation")
            except Exception as e:
                print(f"Error using KMeans clustering: {str(e)}")
                print("Falling back to regular recommendation")
        
        # Regular recommendation approach using cosine similarity
        distances = cdist(scaled_song_center, scaled_data, 'cosine')
        index = list(np.argsort(distances)[:, :n_songs][0])
        
        # Get recommendations excluding songs in the input list
        rec_songs = spotify_data.iloc[index]
        rec_songs = rec_songs[~rec_songs['name'].isin(song_dict['name'])]
        recommendations = rec_songs[metadata_cols].to_dict(orient='records')
        
        return {
            'success': True,
            'data': recommendations,
            'error_message': None,
            'error_code': None
        }
        
    except Exception as e:
        error_message = f"Error generating recommendations: {str(e)}"
        print(error_message)
        return {
            'success': False,
            'data': [],
            'error_message': error_message,
            'error_code': 500  # General error
        }


if __name__ == "__main__":
    try:
        # Example song list for testing
        song_list = [
            {'name': 'Shape of You', 'year': 2017},
            {'name': 'Rolling in the Deep', 'year': 2011},
            {'name': 'Blinding Lights', 'year': 2020}
        ]
        
        # Load dataset
        spotify_data = pd.read_csv('data/data_with_cluster_labels.csv')
        
        # Get recommendations (default method without clustering)
        print("\n--- Standard Recommendations ---")
        recommendation_result = recommend_songs(song_list, spotify_data)
        
        if recommendation_result['success']:
            print("Recommended songs:")
            for i, song in enumerate(recommendation_result['data'], 1):
                print(f"{i}. {song['name']} ({song['year']}) by {song['artists']}")
        else:
            print(f"Error: {recommendation_result['error_message']}")
            
        # Try with clustering if models exist
        if os.path.exists('models/kmeans_model.pkl') and os.path.exists('models/standard_scaler.pkl'):
            print("\n--- Cluster-Based Recommendations ---")
            cluster_recommendations = recommend_songs(song_list, spotify_data, use_clusters=True)
            
            if cluster_recommendations['success']:
                print("Recommended songs (using clustering):")
                for i, song in enumerate(cluster_recommendations['data'], 1):
                    print(f"{i}. {song['name']} ({song['year']}) by {song['artists']}")
            else:
                print(f"Error with cluster recommendations: {cluster_recommendations['error_message']}")
            
    except Exception as e:
        print(f"Fatal error: {str(e)}")

