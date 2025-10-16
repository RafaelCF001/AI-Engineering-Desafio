
# Desafio: Relatórios Automatizados de SRAG com IA Generativa

## Visão Geral

Este projeto implementa uma solução de geração automatizada de relatórios epidemiológicos sobre SRAG (Síndrome Respiratória Aguda Grave) utilizando IA generativa, dbt para modelagem de dados, e integração com ferramentas de busca de notícias em tempo real via API Tavily. O sistema é modular, auditável e transparente, com arquitetura baseada em LangChain e LangGraph.

## Objetivo

Automatizar a análise de dados e a geração de relatórios técnicos sobre SRAG, combinando dados estruturados, gráficos e notícias recentes, com validação automática de conteúdo sensível.

## Arquitetura

- **dbt**: Utilizado para modelagem, transformação e documentação dos dados epidemiológicos. Os modelos SQL (staging, intermediate, marts) garantem dados limpos e métricas confiáveis.
- **DuckDB**: Banco analítico em memória para consultas rápidas sobre os dados modelados pelo dbt.
- **LangChain & LangGraph**: Orquestram o fluxo entre agentes, integração com LLMs e ferramentas customizadas.
- **Agentes**:
   - **Planner Agent**: Planeja a coleta de métricas, busca notícias via Tavily API, gera comentários detalhados e aciona a geração de gráficos.
   - **Synthesizer Agent**: Compila métricas, gráficos e notícias em um relatório técnico em Markdown, pronto para revisão.
- **Ferramentas**:
   - **data_analysis.py**: Consulta métricas chave e gera gráficos diários/mensais de casos.
   - **srag_news.py**: Realiza busca de notícias em tempo real usando a API Tavily.
- **Governança**: Todo o estado do pipeline (decisões, métricas, resultados, comentários, notícias) é registrado e auditável no langsmith.
- **Validação de Conteúdo**: O relatório final é revisado automaticamente por um agente para garantir ausência de conteúdo sensível.

## Fluxo de Execução

1. **Planejamento**: O agente planner coleta métricas do banco dbt/DuckDB, busca notícias via Tavily, gera comentários e aciona a geração de gráficos.
2. **Síntese**: O agente synthesizer compila todos os dados e gera o relatório final em Markdown, referenciando os gráficos gerados.
3. **Revisão Final**: O relatório é revisado automaticamente para garantir que não há conteúdo sensível ou inadequado.

## Detalhamento do Pipeline dbt

- **Staging**: Limpeza e padronização dos dados brutos (ex: datas, evolução, UTI, vacinação).
- **Intermediate**: Cálculo de métricas chave (taxa de mortalidade, crescimento, ocupação de UTI, vacinação) e agregações temporais.
- **Marts**: Visões analíticas para gráficos e relatórios (casos diários, mensais, séries temporais).
- **Seeds**: População por UF/município para cálculo de taxas.

## Busca de Notícias em Tempo Real

- Utiliza a API Tavily para buscar, filtrar e sumarizar notícias relevantes sobre SRAG, garantindo contexto atualizado e confiável para o relatório.

## Geração de Gráficos

- Gráficos de casos diários e mensais são gerados automaticamente e referenciados no relatório final.

## Validação e Governança

- Todo o pipeline é auditável, com registro do estado global, decisões dos agentes e resultados intermediários no langsmith.
- O relatório final passa por revisão automática para garantir conformidade e segurança.


1. **Pré-requisitos**:
   - Python 3.10+
   - Instalar dependências: `pip install -r requirements.txt`
   - Arquivo de dados Parquet em `data/srag_limpo.parquet`
   - Configurar variáveis de ambiente (ex: chave da OpenAI) em `.env`

2. **Execução**:
   - Execute o arquivo principal (`main.py` ou `teste.py`) para iniciar o fluxo.
   - O sistema irá processar a solicitação do usuário, consultar os dados, gerar gráficos e produzir o relatório final em `relatorio_final.md`.

## Estrutura dos Principais Arquivos

- `main.py`: Inicialização do fluxo e definição do grafo de agentes.
- `nodes/`: Implementação dos agentes (nós) do fluxo.
- `tools/`: Ferramentas customizadas para análise de dados, geração de gráficos e busca de notícias.
- `models/`: Definição dos modelos de dados e estado global.
- `data/`: Dados de entrada em formato Parquet.
- `graficos/`: Gráficos gerados automaticamente.


## Governança, Transparência e Auditoria

- Toda a orquestração e rastreabilidade do pipeline é realizada via LangSmith, que registra logs detalhados de cada agente, suas decisões, entradas e saídas, permitindo auditoria completa do fluxo.
- O estado global (`AgentState`) mantém o histórico de decisões, queries executadas e resultados intermediários, promovendo transparência e rastreabilidade.


## Guardrails e Tratamento de Dados Sensíveis

- Todas as queries SQL são validadas para impedir execução de comandos DDL/DML destrutivos (DROP, DELETE, UPDATE, INSERT, ALTER, CREATE), restringindo o sistema a operações de leitura (SELECT).
- O relatório final é submetido a uma etapa de avaliação automática por LLM (AI as a Judge), que verifica a presença de conteúdo sensível, inadequado ou vazamento de dados, bloqueando a publicação caso qualquer violação seja detectada.
- Todos os erros e exceções são capturados e registrados, garantindo robustez e rastreabilidade para auditoria posterior.
