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
       You are a programmatic research agent.
Your task is to gather information about SARS for a report, following instructions precisely.

Steps: 
1 - Use the tool get_srag_key_metrics to gather the data about ocupation rate in ICU, SARS increase rate , population vaccinate rate, and mortality rate. The date should be in the format YYYY-MM-DD.

2 - Use the tool search_srag_news with the query: "Situação atual do SRAG no Brasil"

3 - Use the tool search_srag_news with the query: "Novos casos de SRAG no Brasil"

4 - Use the tool search_srag_news with the query: "Fatores que influenciam a SRAG no Brasil"

5 - After you have all metrics and the results from all 3 searches, create a 100-word summary of all the information gathered.

Execution rules: 
- You MUST follow the steps in order, one by one.
- Do NOT move to the next step until the current one is complete.
- Do NOT add any conversational text or comments in your responses when you are calling tools. 
- When you are calling tools, your response must ONLY contain tool calls and an empty "content" field.
        """
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
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
        date = None
        news = []
        taxa_mortalidade, taxa_crescimento, taxa_ocupacao_uti, taxa_vacinacao = (None,) * 4

        messages = result.get("messages", [])

        for message in messages:
            
            if isinstance(message, AIMessage) and message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call['name'] == 'get_srag_key_metrics' and date is None:
                        try:
                            args = tool_call.get('args', {})
                            if 'date' in args:
                                date = args['date']
                                print(f"--- Data extraída do tool call: {date} ---")
                                break 
                        except Exception as e:
                            print(f"Erro ao processar 'date' dos argumentos do tool call: {e}")
            message_name = getattr(message, 'name', None)
            
            if message_name == 'get_srag_key_metrics':
                taxa_mortalidade, taxa_crescimento, taxa_ocupacao_uti, taxa_vacinacao = self._parse_metrics(message.content)
            
            elif message_name == 'search_srag_news':
                news.append(self._parse_news_content(message.content))

        noticias = "\n".join(news)

        generate_daily_cases_plot(date)
        generate_monthly_cases_plot(date)
        
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

        Gere os comentários em formato estruturado para cada tópico, respeitando o seguinte formato json:
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
            




        