from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from recommend_songs import recommend_songs

app = Flask(__name__)

# Load the Spotify dataset
spotify_data = pd.read_csv('data/processed/data_with_cluster_labels.csv')

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    """
    Endpoint to get song recommendations based on user input
    
    Expected JSON format:
    {
        "songs": [
            {"name": "Song Name 1", "year": 2020},
            {"name": "Song Name 2", "year": 2018},
            ...
        ],
        "recommendation_type": "quick" | "advanced" | "both"
    }
    """
    try:
        data = request.get_json()
        songs = data.get('songs', [])
        recommendation_type = data.get('recommendation_type', 'quick')
        
        # Validate input
        if not songs:
            return jsonify({
                'success': False,
                'error': 'No songs provided',
                'error_code': 400
            }), 400
            
        # Convert year strings to integers
        for song in songs:
            if 'year' in song and isinstance(song['year'], str):
                try:
                    song['year'] = int(song['year'])
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': f"Invalid year format for song: {song['name']}",
                        'error_code': 400
                    }), 400
        
        result = {}
        
        # Get quick recommendations (no clustering)
        if recommendation_type in ['quick', 'both']:
            quick_recommendations = recommend_songs(songs, spotify_data, use_clusters=False)
            result['quick'] = quick_recommendations
            
        # Get advanced recommendations (with clustering)
        if recommendation_type in ['advanced', 'both']:
            advanced_recommendations = recommend_songs(songs, spotify_data, use_clusters=True)
            result['advanced'] = advanced_recommendations
            
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_code': 500
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
