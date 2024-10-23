from spotifyTrackerDAGs.resources.db_conn import PgConnectionRessource
from dotenv import load_dotenv
from dagster import asset, op, job
from datetime import datetime
import uuid
import spotipy
import json
import os

@asset(
        compute_kind="python",
        description="fetch a specific playlist data from spotify api",
        group_name="extract_load_v1"
    )
def get_raw_playlist_data():
    # Load environment variables from .env file
    load_dotenv(dotenv_path='../../../.env')
    # Step 1: Set up Spotify OAuth
    sp_oauth = spotipy.oauth2.SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope="playlist-read-private,playlist-read-collaborative",
        open_browser=False
    )  
    sp_oauth.refresh_access_token(os.getenv('SPOTIFY_REFRESH_TOKEN'))
    res = sp_oauth.get_cached_token()
    sp = spotipy.Spotify(auth=res['access_token'])

    #playlist i am interessted in
    raw_data = sp.playlist_items(playlist_id='37i9dQZF1EJw3nsz0uuPqC')

    return raw_data


@asset(
        compute_kind="python",
        description="basic parsing of the returned request",
        group_name="extract_load_v1"
    )
def preprocess_data(get_raw_playlist_data) -> bytes:
    res = []
    for index, track in enumerate(get_raw_playlist_data['items']):
        processed_data = {}
        processed_data["record_id"] = str(uuid.uuid4())
        processed_data['batch_rank'] = int(index)
        processed_data['created_at'] = track['added_at'] #datetime.fromisoformat(track['added_at'].replace('Z', '+00:00'))
        processed_data['created_by'] = track['added_by']['id']
        processed_data['album_image_url'] = track['track']['album']['images'][0]['url']
        processed_data['album_title'] = track['track']['album']['name']
        processed_data['album_release_date'] = track['track']['album']['release_date']

        # Handle cases where album_release_date is just a year
        if processed_data['album_release_date']:
            if len(processed_data['album_release_date']) != 10:  # Year only (like "2014")
                processed_data['album_release_date'] = f"{processed_data['album_release_date']}-01-01"  # Default to January 1st of that year

        processed_data['artists'] = [artist["name"] for artist in track['track']['artists']]
        processed_data['artists_id'] = [artist["id"] for artist in track['track']['artists']]
        processed_data['track_id'] = track['track']['id']
        processed_data['track_title'] = track['track']['name']
        processed_data['track_popularity'] = track['track'].get('popularity')
        processed_data['track_uri'] = track['track']['uri']
        res.append(processed_data)
    return json.dumps(res, indent=1, ensure_ascii=False).encode('utf-8')


# since there is many to many realtionships (authors feats), we need to
# handle the flow with a fact table an authors table and a junction table
# to keep the warehouse consistant. 
@asset(
    compute_kind="python",
    description="loads the data into postgres database",
    group_name="extract_load_v1"
    )
def load_spotify_records_batch(pg_res : PgConnectionRessource, preprocess_data : bytes) -> None:
    processed_data = json.loads(preprocess_data.decode('utf-8')) 
    conn = pg_res.connect_db()
    cursor = conn.cursor()

    for record in processed_data: 
        
        # increment the fact table: spotify_records
        cursor.execute(
            """
            INSERT INTO spotify_records 
            (record_id ,record_batch_tank, created_at, created_by, album_image_url, album_title, 
            album_release_date, track_id, track_title, 
            track_popularity, track_uri) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                record['record_id'],
                record['batch_rank'],
                record['created_at'],
                record['created_by'],
                record['album_image_url'],
                record['album_title'],
                record['album_release_date'],
                record['track_id'],
                record['track_title'],
                record['track_popularity'],
                record['track_uri']
            )
        )
        for artist_name, artist_id in zip(record["artists"], record["artists_id"]):
            # Insert artist into authors table if the artist is not already present
            cursor.execute(
                """
                INSERT INTO authors (author_id, author_name) 
                SELECT %s, %s
                WHERE NOT EXISTS (SELECT 1 FROM authors WHERE author_id = %s)
                """,
                (artist_id, artist_name, artist_id)  # Use both artist_id and artist_name
            )

            # Insert into spotifyRecordsAuthors junction table
            cursor.execute(
                """
                INSERT INTO spotifyRecordsAuthors (record_id, author_id) 
                VALUES (%s, %s)
                """,
                (record['record_id'], artist_id)
            )

    # Commit the transaction after all inserts
    conn.commit()
    cursor.close()