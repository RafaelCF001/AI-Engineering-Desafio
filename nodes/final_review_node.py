
from models.state import AgentState
from typing import Dict
from langchain_openai import ChatOpenAI
import json


def final_review_node(state: AgentState) -> Dict:
    print("---REVISANDO O RELATÓRIO FINAL---")
    report = state.get('report', '')
    if not report:
        return {"results": {"review": "true"}}

    prompt = (
        "Você é um revisor de conteúdo sensível. Analise o texto abaixo e responda apenas com 'True' se NÃO houver conteúdo sensível (como dados pessoais, informações confidenciais, discurso de ódio, fake news, etc). "
        "Responda 'False' se houver qualquer conteúdo sensível.\n\nTexto:\n" + report
    )
    llm = ChatOpenAI(model="gpt-5", temperature=0)
    response = llm.invoke(prompt)
    # Interpreta resposta do modelo
    result = str(response.content).strip().lower()
    if 'false' in result:
        return {"results": {"review": "false"}}
    return {"results": {"review": "true"}}