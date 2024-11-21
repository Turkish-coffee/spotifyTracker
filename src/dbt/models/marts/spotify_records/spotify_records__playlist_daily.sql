WITH
albums AS (
    SELECT * FROM {{ ref('stg_spotify_core__albums') }}
),

authors AS (
    SELECT * FROM {{ ref('stg_spotify_core__authors') }}
),

record_authors AS (
    SELECT * FROM {{ ref('stg_spotify_core__record_authors') }}
),

records AS (
    SELECT * FROM {{ ref('stg_spotify_core__records') }}
),

tracks AS (
    SELECT * FROM {{ ref('stg_spotify_core__tracks') }}
),

spotify_records AS (
    SELECT 
        al.album_image_url,
        al.album_title,
        al.album_release_year,
        re.record_id,
        re.record_batch_rank,
        re.created_at,
        re.created_by,
        re.album_id,
        re.track_id,
        tr.track_title,
        tr.track_popularity, 
        tr.track_uri,
        -- Aggregate all authors into a single column
        STRING_AGG(au.author_name, ', ') AS author_names  -- Combines author names with a comma separator
    FROM records re
    INNER JOIN tracks tr ON tr.track_id = re.track_id
    INNER JOIN record_authors reau ON re.record_id = reau.record_id
    INNER JOIN authors au ON reau.author_id = au.author_id
    INNER JOIN albums al ON al.album_id = re.album_id
    WHERE NOW() - re.created_at <= INTERVAL '1 day'
    GROUP BY 
        al.album_image_url,
        al.album_title,
        al.album_release_year,
        re.record_id,
        re.record_batch_rank,
        re.created_at,
        re.created_by,
        re.album_id,
        re.track_id,
        tr.track_title,
        tr.track_popularity, 
        tr.track_uri
)

SELECT * FROM spotify_records
