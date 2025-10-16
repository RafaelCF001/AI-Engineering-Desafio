
from models.state import AgentState
from typing import Dict
from langchain_openai import ChatOpenAI

def synthesizer_node(state: AgentState) -> Dict:
    """Nó Sintetizador: Gera o relatório final com base em todos os dados coletados."""
    print("---SINTETIZANDO O RELATÓRIO FINAL ---")
    
    first_message = state["messages"][0]
    if isinstance(first_message, dict):
        user_request = first_message.get("content", "")
    else:
        user_request = getattr(first_message, "content", "")

    sql_llm = ChatOpenAI(model="gpt-5", temperature=0)



    results_dict = state.get('results').get("commentary", {})
    crescimento, mortalidade, uti, vacinacao = results_dict.comentario_crescimento, results_dict.comentario_mortalidade, results_dict.comentario_ocupacao_uti, results_dict.comentario_vacinacao
    collected_data_str = f"- Comentário sobre a taxa de crescimento de casos: {crescimento}\n- Comentário sobre a taxa de mortalidade: {mortalidade}\n- Comentário sobre a taxa de ocupação de UTI: {uti}\n- Comentário sobre a taxa de vacinação: {vacinacao}"

    taxas = state.get('taxas', [])
    taxas_labels = [
        "Taxa de mortalidade",
        "Taxa de crescimento de casos",
        "Taxa de ocupação de UTI",
        "Taxa de vacinação"
    ]
    taxas_str = "\n".join(
        f"- {label}: {taxa}" for label, taxa in zip(taxas_labels, taxas)
    )


    prompt = f"""Você é um especialista em epidemiologia. Sua tarefa é escrever um relatório técnico claro respondendo à solicitação original do usuário.\nSolicitação: \"{user_request}\"\n\nA seguir estão os dados :\n---\n{collected_data_str}\n---\n\nTaxas epidemiológicas relevantes:\n{taxas_str}\n\nCom base exclusivamente nos dados fornecidos, escreva um relatório coeso e bem estruturado em formato markdown.\nCrie os gráficos.\nInterprete os resultados, identifique padrões e forneça uma conclusão clara.\nOs gráficos estão disponíveis em /graficos/casos_diarios_30d.png e /graficos/casos_mensais_12m.png .\nA resposta deve estar obrigatoriamente em markdown válido, com títulos, listas e imagens se necessário. Não inclua uma sessão de limitações e conclusão."""

    print("Enviando prompt para o modelo...")

    response = sql_llm.invoke(prompt)

    print("Resposta recebida do modelo.")


    if hasattr(response, "content"):
        content = response.content
    else:
        content = str(response)

    with open("relatorio_final.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("Relatório salvo em relatorio_final.md")
    return {"report": content}
