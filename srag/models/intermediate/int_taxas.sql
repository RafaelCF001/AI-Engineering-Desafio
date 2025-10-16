{{ config(materialized="table") }}

with base as (
  select
    dt_notific,
    count(*) as total_casos,
    sum(case when EVOLUCAO = 2 then 1 else 0 end) as obitos,
    sum(case when UTI = 1 then 1 else 0 end) as internacoes_uti,
    sum(case when VACINA = 1 then 1 else 0 end) as vacinados
  from {{ ref('stg_srag') }}
  group by dt_notific
),

crescimento as (
  select
    dt_notific,
    total_casos,
    obitos,
    internacoes_uti,
    vacinados,
    lag(total_casos) over (order by dt_notific) as casos_ontem
  from base
)

select
  dt_notific,
  total_casos,
  obitos,
  internacoes_uti,
  vacinados,
  case when total_casos > 0 then obitos * 1.0 / total_casos end as taxa_mortalidade,
  case when casos_ontem > 0 then (total_casos - casos_ontem) * 1.0 / casos_ontem end as taxa_crescimento,
  case when total_casos > 0 then internacoes_uti * 1.0 / total_casos end as taxa_ocupacao_uti,
  case when total_casos > 0 then vacinados * 1.0 / total_casos end as taxa_vacinacao
from crescimento
order by dt_notific
