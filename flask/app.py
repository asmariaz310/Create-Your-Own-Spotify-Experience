from flask import Flask, render_template
import os

app = Flask(__name__)

# Path to the folder containing the MP3 files
folder_path = '/home/asmariaz/Downloads/flask/sample_audio_data'

def get_song_files(folder_path):
    """Get a list of MP3 files from the specified folder."""
    songs = [f for f in os.listdir(folder_path) if f.endswith('.mp3')]
    return songs[:5]  # Get at least 5 songs (or fewer if there are less than 5)

def get_recommendations(song_name):
    """Generate dummy recommendations for a given song."""
    recommendations = [f"Recommendation {i+1} for {song_name}" for i in range(5)]
    return recommendations

@app.route('/')
def index():
    """Render the index page with the list of songs."""
    songs = get_song_files(folder_path)
    return render_template('index.html', songs=songs)

@app.route('/recommendations/<song_name>')
def recommendations(song_name):
    """Render the recommendations page for a given song."""
    recommendations = get_recommendations(song_name)
    return render_template('recommendations.html', song_name=song_name, recommendations=recommendations)

if __name__ == "__main__":
    app.run(debug=True)

