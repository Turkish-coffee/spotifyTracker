with

source as (

    select * from {{ source('spotify_core','records') }}

),

customers as (

    select
        record_id,
        record_batch_rank,
        created_at,
        created_by,
        album_id,
        track_id

    from source

)

select * from customers