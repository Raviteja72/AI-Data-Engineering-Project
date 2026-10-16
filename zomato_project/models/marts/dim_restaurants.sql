with stg_restaurants as (
    select
        *
    from {{ ref('stg_restaurants') }}
)

select *
from stg_restaurants