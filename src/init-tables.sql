-- Create custom schema
CREATE SCHEMA IF NOT EXISTS spotify_core;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE spotify_core.albums (
    album_id VARCHAR(255) PRIMARY KEY,
    album_image_url VARCHAR(255),
    album_title VARCHAR(255) NOT NULL,
    album_release_year INTEGER
);

CREATE TABLE spotify_core.tracks(
    track_id VARCHAR(50) PRIMARY KEY,
    track_title VARCHAR(255) NOT NULL,
    track_popularity INTEGER, 
    track_uri VARCHAR(255)
);

-- Define fact table with schema-qualified references
CREATE TABLE spotify_core.records(
    record_id UUID PRIMARY KEY,
    record_batch_rank INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    created_by VARCHAR(50) NOT NULL,
    album_id VARCHAR(255) REFERENCES spotify_core.albums(album_id),
    track_id VARCHAR(50) REFERENCES spotify_core.tracks(track_id)
);

CREATE TABLE spotify_core.authors (
    author_id VARCHAR(255) PRIMARY KEY,
    author_name VARCHAR(255) NOT NULL
);

CREATE TABLE spotify_core.record_authors(
    id SERIAL PRIMARY KEY,
    record_id UUID REFERENCES spotify_core.records(record_id),
    author_id VARCHAR(255) REFERENCES spotify_core.authors(author_id)
);
