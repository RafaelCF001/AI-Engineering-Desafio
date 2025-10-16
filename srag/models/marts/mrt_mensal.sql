{{ config(materialized="view") }}

select
  date_trunc('month', dt_notific) as mes,
  sum(total_casos) as casos_mensais
from {{ ref('int_taxas') }}
where dt_notific >= date_trunc('month', current_date) - interval '12 month'
group by 1
order by 1
