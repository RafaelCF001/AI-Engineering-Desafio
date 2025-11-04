from langchain_tavily import TavilySearch

# Counter for tool calls
search_srag_news_calls = 0

def search_srag_news(query: str = "últimas notícias sobre Síndrome Respiratória Aguda Grave no Brasil") :
    """
    Realiza uma busca na web usando TavilySearch.
    Retorna um dicionário com os resultados.
    """
    global search_srag_news_calls
    search_srag_news_calls += 1
    print(f"search_srag_news called {search_srag_news_calls} times.")

    tool = TavilySearch(max_results=2,
                        include_answer=False,
                        include_raw_content=False,
                        include_images=False)
    
    resp = tool.invoke({"query": query})
    return resp



