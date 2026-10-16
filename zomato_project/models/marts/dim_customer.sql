select
customer_id,
customer_name,
email,
age,
case when age < 18 then 'GEN Z'
        when age < 40 then 'MILLENNIALS'
        when age < 55 then 'GEN X'
        when age is null then 'UNKNOWN'
        else 'BOOMERS' end as age_segment,
gender,
marital_status,
occupation,
income_band,
education,
family_size
from {{ ref('stg_users') }}