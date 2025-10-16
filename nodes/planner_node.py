from models.models import RelatorioSRAG
from typing import Dict
from tools.data_analysis import get_srag_key_metrics, generate_daily_cases_plot, generate_monthly_cases_plot
from tools.srag_news import search_srag_news
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import PydanticOutputParser
import json 
from models.state import AgentState

class SragAgent:
    def __init__(self) -> None: 
        self.system_promt = """
        You are a Severe Acute Respiratory Syndrome specialist. 
        Your task is to gather information about SARS for a report generation. 
        Steps: 
        1 - Use the tool get_srag_key_metrics to gather the data about ocupation rate in ICU, SARS increase rate , population vaccinate rate, and mortality rate. The date should be in the format YYYY-MM-DD.

        Step 2 - Perform 3 search about SARS in Brazil (SRAG in portuguese) about the current situation, new cases, driving factors, etc... Use the tool search_srag_news
        - Each search must target one topic per call 
        - Gather all the rates informations before performing any search.
        Step 3 - Create a 100 word summary, it should be short and quick
        Execution rules: 
        Call
        """
        self.llm = ChatOpenAI(model="gpt-5", temperature=0)
        self.tools = [get_srag_key_metrics, search_srag_news ]
    
    def execute(self, state: AgentState) -> AgentState:
        print("--- 🧠 EXECUTANDO O PLANEJADOR ---")
        taxa_mortalidade = 0
        taxa_crescimento = 0
        taxa_ocupacao_uti = 0
        taxa_vacinacao = 0
        news = []

        agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self.system_promt,
            name="srag_agent"
        )

        result = agent.invoke(state)

        for message in result['messages']:
            if message.name == 'get_srag_key_metrics':
                taxa_mortalidade, taxa_crescimento, taxa_ocupacao_uti, taxa_vacinacao = self._parse_metrics(message.content)
            if message.name == 'search_srag_news':
                news.append(self._parse_news_content(message.content))

        noticias = "\n".join(news)

        generate_daily_cases_plot()
        generate_monthly_cases_plot()
        
        commentary = self.create_commentary(
            taxa_mortalidade, taxa_crescimento, taxa_ocupacao_uti, taxa_vacinacao, noticias
        )
        return {
            "messages": result.get("messages", []),
            "results": {"commentary": commentary},
            "taxas": [taxa_mortalidade, taxa_crescimento, taxa_ocupacao_uti, taxa_vacinacao],
        }
    
    def _parse_metrics(self, data):
        try:
            json_data = json.loads(data)
            taxa_mortalidade = json_data["metricas"].get("taxa_mortalidade")
            taxa_crescimento = json_data["metricas"].get("taxa_crescimento")
            taxa_ocupacao_uti = json_data["metricas"].get("taxa_ocupacao_uti")
            taxa_vacinacao = json_data["metricas"].get("taxa_vacinacao")
            return taxa_mortalidade, taxa_crescimento, taxa_ocupacao_uti, taxa_vacinacao
        except Exception as e:
             print(e)
        

    def _parse_news_content(self, news):
        news = json.loads(news)
        news = [item["content"] for item in news.get("results", []) if item.get("content")]
        return "\n".join(news)
    
    def create_commentary(self, taxa_mortalidade, taxa_crescimento, taxa_ocupacao_uti, taxa_vacinacao, noticias):
        prompt = f"""Você é um analista de saúde pública. Comente os dados de SRAG abaixo,
        criando um relatório com insights claros e objetivos.

        Dados:
        - Taxa de mortalidade: {taxa_mortalidade}
        - Taxa de crescimento de casos: {taxa_crescimento}
        - Taxa de ocupação de UTI: {taxa_ocupacao_uti}
        - Taxa de vacinação: {taxa_vacinacao}
        - Notícia relevante: {noticias}

        Gere os comentários em formato estruturado para cada tópico, respeitando o seguinte formato Pydantic:
        class RelatorioSRAG(BaseModel):
            comentario_mortalidade: str
            comentario_crescimento: str
            comentario_ocupacao_uti: str
            comentario_vacinacao: str
            comentario_noticia: str
        """

        print("--- Commentary prompt --- ")

        agent = create_react_agent(model=self.llm, tools=[])
        result = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
        ai_messages = [msg for msg in result.get("messages", []) if isinstance(msg, AIMessage)]
        if not ai_messages:
            return ""

        parser = PydanticOutputParser(pydantic_object=RelatorioSRAG)
        try:
            parsed = parser.parse(ai_messages[-1].content)
            return parsed
        except Exception as e:
            print(f"Erro ao parsear o comentário gerado: {e}")
            return ai_messages[-1].content
            




        