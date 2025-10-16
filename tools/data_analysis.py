import pandas as pd
import duckdb
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
matplotlib.use('Agg')
conn = duckdb.connect("srag/data/meu_projeto.duckdb")
srag_calls = 0


get_srag_key_metrics_calls = 0

def get_srag_key_metrics(date: str) -> dict:
    """
    Calcula as métricas chave de SRAG a partir do banco de dados.
    Use esta ferramenta para obter os números principais como taxa de aumento,
    mortalidade, ocupação de UTI e vacinação.
    Retorna: Um dicionário com as métricas calculadas.
    """
    global get_srag_key_metrics_calls
    get_srag_key_metrics_calls += 1
    print(f"get_srag_key_metrics called {get_srag_key_metrics_calls} times.")
    metricas = {}
    print(date)
    query = f"""
SELECT * from int_taxas WHERE dt_notific = DATE '{date}';
"""
    df = conn.execute(query).df()

    taxa_mortalidade = df['taxa_mortalidade'].values[0]
    taxa_crescimento = df['taxa_crescimento'].values[0]
    taxa_ocupacao_uti = df['taxa_ocupacao_uti'].values[0]
    taxa_vacinacao = df['taxa_vacinacao'].values[0]

    metricas['taxa_mortalidade'] = taxa_mortalidade
    metricas['taxa_crescimento'] = taxa_crescimento
    metricas['taxa_ocupacao_uti'] = taxa_ocupacao_uti
    metricas['taxa_vacinacao'] = taxa_vacinacao

    return {"metricas": metricas}
def generate_daily_cases_plot() -> str:
    """
    Gera um gráfico de barras com o número de casos diários de SRAG nos últimos 30 dias.
    Esta ferramenta salva o gráfico como um arquivo PNG e retorna o caminho para o arquivo.
    """
    query_diario = """
    select
        dt_notific,
        total_casos
    from int_taxas
    where dt_notific >= current_date - interval '30 day'
    order by dt_notific;
    """

    df_diario = conn.execute(query_diario).df()
    plt.close('all')
    plt.clf()
    plt.cla()

    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(14, 7))
    
    ax.plot(df_diario["dt_notific"], df_diario["total_casos"], 
            marker="o", linestyle="-", linewidth=2.5, 
            color="#2E86AB", markersize=6, markerfacecolor="#A23B72",
            markeredgewidth=2, markeredgecolor="white", label="Casos diários")
    
    ax.fill_between(df_diario["dt_notific"], df_diario["total_casos"], 
                     alpha=0.3, color="#2E86AB")
    
    ax.set_title("Casos Diários de SRAG - Últimos 30 Dias", 
                 fontsize=18, fontweight='bold', pad=20, color="#2C3E50")
    ax.set_xlabel("Data de Notificação", fontsize=13, fontweight='bold', color="#34495E")
    ax.set_ylabel("Número de Casos", fontsize=13, fontweight='bold', color="#34495E")
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
    plt.xticks(rotation=45, ha='right')
    
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
    ax.set_axisbelow(True)
    
    step = max(1, len(df_diario) // 8)
    for i in range(0, len(df_diario), step):
        ax.annotate(f'{int(df_diario["total_casos"].iloc[i])}',
                   xy=(df_diario["dt_notific"].iloc[i], df_diario["total_casos"].iloc[i]),
                   xytext=(0, 10), textcoords='offset points',
                   ha='center', fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                            edgecolor='gray', alpha=0.8))
    
    ax.legend(loc='upper left', frameon=True, shadow=True, fontsize=11)
    
    plt.tight_layout()
    plt.savefig("graficos/casos_diarios_30d.png", dpi=150, 
                facecolor='white', edgecolor='none', bbox_inches='tight')
    plt.close(fig)
    plt.close('all')
    
    return f"Gráfico de casos diários salvo em: graficos/casos_diarios_30d.png"

def generate_monthly_cases_plot() -> str:
    """
    Gera um gráfico de barras com o número de casos mensais de SRAG nos últimos 12 meses.
    Esta ferramenta salva o gráfico como um arquivo PNG e retorna o caminho para o arquivo.
    """
        
    query_mensal = """
        select
            date_trunc('month', dt_notific) as mes,
            sum(total_casos) as casos_mensais
        from int_taxas
        where dt_notific >= date_trunc('month', current_date) - interval '12 month'
        group by 1
        order by 1;
    """

    df_mensal = conn.execute(query_mensal).df()

    plt.close('all')
    plt.clf()
    plt.cla()

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(14, 7))
    
    colors = plt.cm.viridis(range(len(df_mensal)))
    
    bars = ax.bar(range(len(df_mensal)), df_mensal["casos_mensais"], 
                   color=colors, edgecolor='white', linewidth=1.5, alpha=0.85)
    
    for i, (bar, valor) in enumerate(zip(bars, df_mensal["casos_mensais"])):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(valor):,}'.replace(',', '.'),
                ha='center', va='bottom', fontsize=10, 
                fontweight='bold', color="#2C3E50")
    
    ax.set_title("Casos Mensais de SRAG - Últimos 12 Meses", 
                 fontsize=18, fontweight='bold', pad=20, color="#2C3E50")
    ax.set_xlabel("Mês/Ano", fontsize=13, fontweight='bold', color="#34495E")
    ax.set_ylabel("Número de Casos", fontsize=13, fontweight='bold', color="#34495E")
    
    meses_labels = [mes.strftime("%b/%y") for mes in df_mensal["mes"]]
    ax.set_xticks(range(len(df_mensal)))
    ax.set_xticklabels(meses_labels, rotation=45, ha='right')
    
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7, axis='y')
    ax.set_axisbelow(True)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("graficos/casos_mensais_12m.png", dpi=150, 
                facecolor='white', edgecolor='none', bbox_inches='tight')
    plt.close(fig)
    plt.close('all')
    
    return f"Gráfico de casos mensais salvo em: graficos/casos_mensais_12m.png"