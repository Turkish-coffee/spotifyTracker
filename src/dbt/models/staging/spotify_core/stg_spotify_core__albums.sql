with

source as (

    select * from {{ source('spotify_core','albums') }}

),

customers as (

    select
        album_id,
        album_image_url,
        album_title,
        album_release_year

    from source

)

select * from customers


