# EchoForecast: Content-Based Music Trend Prediction

## Project Overview
EchoForecast is a Python-based analytical tool that connects to the Spotify Web API to forecast short-term music listening trends. By utilizing content-based vector analysis, the project evaluates a user's historical listening habits to predict future genre surges and calculate compatibility scores with new playlists.

## Core Features
*   **API Integration:** Securely authenticates and pulls user data via `spotipy` (Saved Tracks, Top Artists, Top Genres).
*   **Taste Match Algorithm:** Computes a Cosine Similarity metric between a user's long-term genre vector and a target playlist's genre vector to predict compatibility.
*   **Trend Forecasting:** Calculates "Genre Velocity" by comparing short-term and long-term listening frequencies to identify rising trends.
*   **Data Visualization:** Generates comparative bar charts using `matplotlib` to visualize User Taste vs. Playlist Composition.

## Requirements
To run this project locally, ensure you have the following dependencies installed:
`pip install spotipy matplotlib`
