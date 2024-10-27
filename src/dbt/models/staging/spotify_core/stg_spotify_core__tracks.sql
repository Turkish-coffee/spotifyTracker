with

source as (

    select * from {{ source('spotify_core','tracks') }}

),

customers as (

    select
    track_id,
    track_title,
    track_popularity, 
    track_uri
    from source

)

select * from customers