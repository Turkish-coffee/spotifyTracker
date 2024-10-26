from spotifyTrackerDAGs.resources.db_conn import PgConnectionRessource
from dotenv import load_dotenv
from dagster import asset
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
def preprocess_data(get_raw_playlist_data, pg_res: PgConnectionRessource) -> bytes:
    conn = pg_res.connect_db()
    cursor = conn.cursor()
    
    res = []
    for index, track in enumerate(get_raw_playlist_data['items']):
        # Check if the track already exists and is unchanged
        cursor.execute("""
            SELECT 1 FROM spotify_records 
            WHERE track_id = %s AND created_at = %s
        """, (track['track']['id'], track['added_at']))
        
        # Skip if the record is unchanged
        if cursor.fetchone():
            continue

        # Process new or updated record
        processed_data = {
            "record_id": str(uuid.uuid4()),
            "batch_rank": int(index),
            "created_at": track['added_at'],
            "created_by": track['added_by']['id'],
            "album_id" : track['track']['album']['id'],
            "album_image_url": track['track']['album']['images'][0]['url'],
            "album_title": track['track']['album']['name'],
            "album_release_year": int(track['track']['album']['release_date'].split('-')[0]),
            "artists": [artist["name"] for artist in track['track']['artists']],
            "artists_id": [artist["id"] for artist in track['track']['artists']],
            "track_id": track['track']['id'],
            "track_title": track['track']['name'],
            "track_popularity": track['track'].get('popularity'),
            "track_uri": track['track']['uri']
        }
        
        res.append(processed_data)
    
    cursor.close()
    conn.close()
    
    return json.dumps(res, indent=1, ensure_ascii=False).encode('utf-8')



# since there is many to many realtionships (authors feats), we need to
# handle the flow with a fact table an authors table and a junction table
# to keep the warehouse consistant. 
@asset(
    compute_kind="python",
    description="loads the data into postgres database",
    group_name="extract_load_v1"
)
def load_spotify_records_batch(pg_res: PgConnectionRessource, preprocess_data: bytes) -> None:
    processed_data = json.loads(preprocess_data.decode('utf-8')) 
    conn = pg_res.connect_db()
    cursor = conn.cursor()

    for record in processed_data:

        # Upstert album table albums
        cursor.execute(
            """
            INSERT INTO albums (album_id, album_image_url, album_title, album_release_year) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (album_id) DO NOTHING
            """,
            ( 
                record['album_id'],
                record['album_image_url'],
                record['album_title'],
                record['album_release_year'],
            )
        )

        # Upstert track table tracks
        cursor.execute(
            """
            INSERT INTO tracks (track_id, track_title, track_popularity, track_uri) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (track_id) DO NOTHING
            """,
            ( 
                record['track_id'],
                record['track_title'],
                record['track_popularity'],
                record['track_uri'],
            )
        )

        # Insert or update records in spotify_records
        cursor.execute(
            """
            INSERT INTO spotify_records 
            (record_id, record_batch_rank, created_at, created_by, album_id, track_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            #ON CONFLICT (track_id) DO UPDATE 
            #SET track_title = EXCLUDED.track_title, track_popularity = EXCLUDED.track_popularity
            #""",
            (
                record['record_id'],
                record['batch_rank'],
                record['created_at'],
                record['created_by'],
                record['album_id'],
                record['track_id']
            )
        )

        # Upsert authors and junction table records
        for artist_name, artist_id in zip(record["artists"], record["artists_id"]):
            cursor.execute(
                """
                INSERT INTO authors (author_id, author_name) 
                VALUES (%s, %s)
                ON CONFLICT (author_id) DO NOTHING
                """,
                (artist_id, artist_name)
            )

            cursor.execute(
                """
                INSERT INTO spotifyRecordsAuthors (record_id, author_id) 
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING
                """,
                (record['record_id'], artist_id)
            )

    conn.commit()
    cursor.close()
    conn.close()
