# Music Recommendation System

A web application that recommends music based on a user's favorite songs using Spotify data. The system offers two recommendation methods: a quick method based on song similarities and an advanced method using K-means clustering.

## Features

- Enter multiple songs with their release years
- Choose between quick recommendations, advanced recommendations, or both
- Beautiful, responsive UI with sleek gradients

## Web Demo

[![Web Demo Youtube Thumbnail](https://img.youtube.com/vi/JEWI0CfUQIg/maxres3.jpg)](https://youtu.be/JEWI0CfUQIg)

## Project Structure

```
├── app.py                     # Flask server application
├── recommend_songs.py         # Recommendation algorithm
├── models/                    # Directory for saved ML models
│   ├── standard_scaler.pkl    # Saved StandardScaler model
│   └── kmeans_model.pkl       # Saved K-means model
├── data/                      # Directory for data files
│   └── data_with_cluster_labels.csv  # Spotify dataset
├── static/                    # Static assets
│   ├── css/
│   │   └── style.css          # Styles for the application
│   └── js/
│       └── script.js          # JavaScript for interactivity
├── templates/                 # HTML templates
│   └── index.html             # Main page template
└── model_training.py          # Notebook that contains EDA and code to train and save ML model
```

## Prerequisites

- Python 3.7+
- Flask
- Pandas
- NumPy
- Scikit-learn
- SciPy
- Joblib

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd CodeAlpha_Music_Recommendation
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate     # For Windows
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. This is an optional step
   Train the models yourself. For this you need to download the raw dataset from [here](https://www.kaggle.com/datasets/vatsalmavani/spotify-dataset?resource=download) and place the csv file in the data/raw/ folder. Then run the following command:
   ```
   python model_training.py
   ```

## Running the Application

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open a web browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## How to Use

1. Enter the names and release years of songs you like
2. Use the "Add Another Song" button to add more songs
3. Select the recommendation type using the slider (Quick, Advanced, or Both)
4. Click "Get Recommendations" to see the results
5. The recommendations will appear below, showing song names, artists, and years

## Dataset

The application uses a [Spotify dataset](https://www.kaggle.com/datasets/vatsalmavani/spotify-dataset?resource=download) containing song features like:
- Acousticness
- Danceability
- Energy
- Instrumentalness
- Tempo
- Valence
- And more...

Ensure the dataset is placed in the `data/processed/` directory as `data_with_cluster_labels.csv`.

## License

MIT License. Read the license file for detailed information.
