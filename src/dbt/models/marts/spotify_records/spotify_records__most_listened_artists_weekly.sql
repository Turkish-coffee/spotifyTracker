
WITH 
records AS (
    SELECT * FROM {{ ref('stg_spotify_core__records') }}
), 

authors AS (
    SELECT * FROM {{ ref('stg_spotify_core__authors') }}
),

record_authors AS (
    SELECT * FROM {{ ref('stg_spotify_core__record_authors') }}
),

most_listened_artists_weekly AS (
    SELECT
        au.author_name,
        re.created_by,
        COUNT(au.author_name) as total_author_occurences
    FROM records re
    INNER JOIN record_authors reau ON re.record_id = reau.record_id
    INNER JOIN authors au ON reau.author_id = au.author_id
    WHERE NOW() - re.created_at <= INTERVAL '7 day'
    GROUP BY 
        au.author_name,
        re.created_by
    ORDER BY total_author_occurences DESC


)

SELECT * FROM most_listened_artists_weekly