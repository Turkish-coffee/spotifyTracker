CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- HERE WILL BE DEFINED FACT TABLE TO LOAD THE SPOTIFY PLAYLIST RECORDS
CREATE TABLE spotify_records(
    record_id UUID PRIMARY KEY,
    record_batch_tank INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    album_image_url VARCHAR(255),
    album_title VARCHAR(255) NOT NULL,
    album_release_date DATE,
    track_id VARCHAR(50) NOT NULL,
    track_title VARCHAR(255) NOT NULL,
    track_popularity INTEGER, 
    track_uri VARCHAR(255)
);

CREATE TABLE authors (
    author_id VARCHAR(255) PRIMARY KEY,
    author_name VARCHAR(255) NOT NULL
);

CREATE TABLE spotifyRecordsAuthors(
    id SERIAL PRIMARY KEY,
    record_id UUID REFERENCES spotify_records(record_id),
    author_id VARCHAR(255) REFERENCES authors(author_id)
);