with

source as (

    select * from {{ source('spotify_core','record_authors') }}

),

customers as (

    select
        id,
        record_id,
        author_id

    from source

)

select * from customers