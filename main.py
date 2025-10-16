import os
from langchain_core.messages import HumanMessage
from orchestrator import graph
from dotenv import load_dotenv

def run_report():
    initial_prompt = (
        "Analise o SRAG sobre o dia 20/03/2025"
        
    )
    app = graph()
    inputs = {"messages": [{"role": "user","content":initial_prompt}]}
    for step in app.stream(inputs, stream_mode="values"):
        print()

    print("\n\n=============================================")
    print("--- RELATÓRIO FINAL GERADO PELO AGENTE ---")
    print("=============================================\n")

   
if __name__ == "__main__":
    load_dotenv()
    run_report()