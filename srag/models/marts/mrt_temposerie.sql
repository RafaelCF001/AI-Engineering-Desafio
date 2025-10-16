{{ config(materialized="view") }}

select
  dt_notific,
  total_casos
from {{ ref('int_taxas') }}
where dt_notific >= current_date - interval '30 day'
order by dt_notific
