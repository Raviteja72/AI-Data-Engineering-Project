
with stg_food as (
    select
        *
    from {{ ref('stg_food') }}
)

select f_id, food_name, veg_or_non_veg from stg_food