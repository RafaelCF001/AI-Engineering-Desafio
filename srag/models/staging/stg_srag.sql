{{ config(materialized="table") }}

select
  cast(DT_NOTIFIC as date) as dt_notific,
  SG_UF_NOT as uf,
  CO_MUN_NOT as municipio,
  EVOLUCAO,
  UTI,
  VACINA
from {{ source('srag', 'dados') }}
where DT_NOTIFIC is not null
