CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE albums (
    album_id VARCHAR(255) PRIMARY KEY,
    album_image_url VARCHAR(255),
    album_title VARCHAR(255) NOT NULL,
    album_release_year INTEGER
);

CREATE TABLE tracks(
    track_id VARCHAR(50) PRIMARY KEY,
    track_title VARCHAR(255) NOT NULL,
    track_popularity INTEGER, 
    track_uri VARCHAR(255)
);

-- HERE WILL BE DEFINED FACT TABLE TO LOAD THE SPOTIFY PLAYLIST RECORDS
CREATE TABLE spotify_records(
    record_id UUID PRIMARY KEY,
    record_batch_rank INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    album_id VARCHAR(255) REFERENCES albums(album_id),
    track_id VARCHAR(50) REFERENCES tracks(track_id)
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