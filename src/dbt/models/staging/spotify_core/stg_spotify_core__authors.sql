with

source as (

    select * from {{ source('spotify_core','authors') }}

),

customers as (

    select
       author_id,
       author_name

    from source

)

select * from customers