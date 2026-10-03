import warnings 
warnings.filterwarnings("ignore")

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter
import math
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

#----BEFORE EVEN RUNNING THE WRAPPED WE WANT TO ENSURE THAT SPOTIPY AND MATPLOTLIB ARE INSTALLED-----

try:
    import spotipy 
    import matplotlib
    print("✅ Spotipy and Matplotlib detected correctly, you're good to go with your wrapped!!")

except ImportError as e:
    print("❌ Dependencies need to be installed")
    print("\n Copy and paste in your terminal:")
    print("  sudo apt update  ")
    print("  sudo apt install python3-spotipy python3-matplotlib")
    print("\n Restart the script after. ")
    input(" Press enter when finished...")
    exit()
print("\n Spotify monthly wrapped ready!!")

# --- 1. SETUP & AUTHENTICATION ---
auth_manager = SpotifyOAuth(
    client_id="9596a0d823e543d1bc6d5c044e247c61",
    client_secret="a155a691228546fa989387e368e18860",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-library-read user-read-playback-state playlist-read-private user-top-read",
    open_browser=True
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# --- 2. NEW MOOD ANALYSIS (NO 403 ERRORS) ---
def analyze_mood_via_genres(items):
    """Uses artist metadata to determine mood since audio-features is restricted."""
    all_genres = []
    total_popularity = 0
    valid_count = 0

    for item in items:
        if item['track'] and item['track']['artists']:
            # We get the full artist object for genres
            artist_id = item['track']['artists'][0]['id']
            artist = sp.artist(artist_id)
            all_genres.extend(artist['genres'])
            total_popularity += artist['popularity']
            valid_count += 1

    if not all_genres:
        print("\n--- 🎭 Mood Analysis ---")
        print("Mood: Data not available for these artists.")
        return

    # Analyze Data
    genre_counts = Counter(all_genres)
    top_genre = genre_counts.most_common(1)[0][0]
    avg_popularity = total_popularity / valid_count

    print(f"\n--- 🎭 AI Mood Analysis (Genre-Based) ---")
    print(f"Primary Genre Influence: {top_genre.title()}")
    print(f"Mainstream Score: {avg_popularity:.1f}/100")

    # Mood Mapping Logic
    tg = top_genre.lower()
    if any(x in tg for x in ['rap', 'hip hop', 'trap']):
        mood = "Energetic & Confident (Hype Vibe ⚡)"
    elif any(x in tg for x in ['pop', 'dance']):
        mood = "Upbeat & Catchy (Mainstream Vibe ✨)"
    elif any(x in tg for x in ['indie', 'sad', 'lo-fi', 'emo']):
        mood = "Emotional & Melancholy (Deep Vibe 🌧️)"
    elif any(x in tg for x in ['rock', 'metal', 'punk']):
        mood = "Raw & Intense (Rebel Vibe 🎸)"
    elif any(x in tg for x in ['r&b', 'soul', 'jazz']):
        mood = "Smooth & Chill (Late Night Vibe 🌙)"
    else:
        mood = "Balanced & Eclectic (Varied Vibe 🎶)"
    
    print(f"Detected Playlist Vibe: {mood}")

# --- 3. THE FULL EXECUTION ---

# A. Saved Tracks
print("\n--- 📥 Your Saved Tracks (Recent 20) ---")
results = sp.current_user_saved_tracks(limit=20)
for item in results["items"]:
    print(f"{item['track']['name']} - {item['track']['artists'][0]['name']}")

# B. Your Playlist List
print("\n--- 📂 Your Playlists ---")
playlists = sp.current_user_playlists(limit=20)
for p in playlists["items"]:
    print(f"{p['name']} (ID: {p['id']})")

# C. Specific Playlist Input & Mood
playlist_link = input("\nPaste a playlist link or ID to analyze: ")
p_id = playlist_link.split("playlist/")[1].split("?")[0] if "playlist/" in playlist_link else playlist_link

try:
    p_results = sp.playlist_items(p_id)
    p_items = p_results["items"]
    print(f"\n--- 🎶 Tracks in this Playlist ---")
    for t in p_items:
        if t['track']: print(f"- {t['track']['name']} by {t['track']['artists'][0]['name']}")
    
    # Run the NEW Mood analysis here
    analyze_mood_via_genres(p_items)

except Exception as e:
    print(f"Error fetching playlist details: {e}")

# D. Top 10 Artists
print("\n--- 🌟 Your Top 10 Artists ---")
top_art = sp.current_user_top_artists(limit=10, time_range='medium_term')
for i, artist in enumerate(top_art['items']):
    print(f"{i+1}. {artist['name']}")

# E. Top 10 Tracks
print("\n--- 🏆 Your Top 10 Tracks ---")
top_tr = sp.current_user_top_tracks(limit=10, time_range='medium_term')
for i, item in enumerate(top_tr['items']):
    print(f"{i+1}. {item['name']} - {item['artists'][0]['name']}")

# F. Top 5 Genres
print("\n--- 🎸 Your Top 5 Genres ---")
all_top_art = sp.current_user_top_artists(limit=50, time_range='medium_term')
genre_list = [g for a in all_top_art['items'] for g in a['genres']]
for i, (genre, count) in enumerate(Counter(genre_list).most_common(5)):
    print(f"{i+1}. {genre} ({count} artists)")

import math

def calculate_ai_taste_match(playlist_items, user_top_genres):
    """
    AI Prediction: Anticipates how well this playlist matches the user's 
    long-term taste using Cosine Similarity logic.
    """
    # 1. Get Playlist Genre Vector
    playlist_genres = []
    for item in playlist_items:
        if item['track'] and item['track']['artists']:
            artist = sp.artist(item['track']['artists'][0]['id'])
            playlist_genres.extend(artist['genres'])
    
    p_counts = Counter(playlist_genres)
    u_counts = Counter(user_top_genres)
    
    # 2. Vector Math (Cosine Similarity)
    # We anticipate the match by seeing how the genre sets overlap
    all_unique_genres = set(p_counts.keys()).union(set(u_counts.keys()))
    
    dot_product = 0
    p_magnitude = 0
    u_magnitude = 0
    
    for g in all_unique_genres:
        p_val = p_counts.get(g, 0)
        u_val = u_counts.get(g, 0)
        dot_product += p_val * u_val
        p_magnitude += p_val**2
        u_magnitude += u_val**2
    
    magnitude = math.sqrt(p_magnitude) * math.sqrt(u_magnitude)
    
    if not magnitude:
        return 0
    
    similarity = (dot_product / magnitude) * 100
    return similarity

# --- HOW TO ADD THIS TO YOUR MAIN EXECUTION ---
# 1. Before you ask for the playlist, grab the user's taste profile:
all_top_art = sp.current_user_top_artists(limit=50, time_range='long_term')
user_genres = [g for a in all_top_art['items'] for g in a['genres']]

# 2. After analyze_mood_via_genres(p_items), call the prediction:
match_score = calculate_ai_taste_match(p_items, user_genres)

print(f"\n--- 🧠 AI Prediction: Taste Match ---")
print(f"Prediction: This playlist is a {match_score:.1f}% match for your soul.")

if match_score > 70:
    print("Result: High Likelihood - You will probably loop this for weeks.")
elif match_score > 40:
    print("Result: Moderate Likelihood - Good for a change of pace.")
else:
    print("Result: Low Likelihood - This feels like someone else's music.")

def predict_future_trends():
    """Predicts next month's vibe by comparing Short-Term vs Long-Term shifts."""
    print("\n--- 🚀 AI Future Trend Forecast ---")
    
    # 1. Get Long-Term (Baseline) and Short-Term (Current) Taste
    lt_art = sp.current_user_top_artists(limit=50, time_range='long_term')
    st_art = sp.current_user_top_artists(limit=50, time_range='short_term')

    lt_genres = Counter([g for a in lt_art['items'] for g in a['genres']])
    st_genres = Counter([g for a in st_art['items'] for g in a['genres']])

    # 2. Calculate Genre Velocity (Growth)
    trends = {}
    all_genres = set(lt_genres.keys()) | set(st_genres.keys())
    
    for g in all_genres:
        # Growth = (Current Frequency) - (Baseline Frequency)
        growth = st_genres.get(g, 0) - lt_genres.get(g, 0)
        trends[g] = growth

    # 3. Identify the "Rising Star"
    top_rising = sorted(trends.items(), key=lambda x: x[1], reverse=True)[:3]
    
    print("Top Rising Genres (Predicted for Next Month):")
    for i, (genre, velocity) in enumerate(top_rising):
        status = "🔥 Surging" if velocity > 5 else "📈 Rising"
        print(f"{i+1}. {genre.title()} ({status})")

    # 4. Predict the "Next Month Vibe"
    primary_trend = top_rising[0][0]
    print(f"\n🔮 PROJECTION: Your February is looking very '{primary_trend.title()}'.")
    print("Recommendation: You'll likely start moving away from your baseline and deep-diving into this new sound.")
predict_future_trends()

def plot_genre_comparison(user_genres, playlist_items):
    """Generates a visual bar chart comparing User Taste vs. Playlist Genres."""
    # Process Playlist Genres
    p_genres = []
    for item in playlist_items:
        if item['track'] and item['track']['artists']:
            try:
                artist = sp.artist(item['track']['artists'][0]['id'])
                p_genres.extend(artist['genres'])
            except: continue
            
    # Get top 5 of each for comparison
    u_top = dict(Counter(user_genres).most_common(5))
    p_top = dict(Counter(p_genres).most_common(5))

    # Combine all unique labels
    all_labels = list(set(u_top.keys()) | set(p_top.keys()))
    user_vals = [u_top.get(l, 0) for l in all_labels]
    playlist_vals = [p_top.get(l, 0) for l in all_labels]

    # Create the Plot
    x = range(len(all_labels))
    plt.figure(figsize=(10, 6))
    plt.bar(x, user_vals, width=0.4, label='Your Taste', align='center', color='forestgreen')
    plt.bar(x, playlist_vals, width=0.4, label='Playlist Vibe', align='edge', color='skyblue')
    
    plt.xticks(x, all_labels, rotation=45, ha='right')
    plt.ylabel('Frequency (Number of Artists)')
    plt.title('AI Analysis: User Taste vs. Playlist Composition')
    plt.legend()
    plt.tight_layout()
    plt.show()

print("\n[Generating Visualization Chart...]")
plot_genre_comparison(user_genres, p_items)