from pydantic import BaseModel, Field

class RelatorioSRAG(BaseModel):
    comentario_mortalidade: str = Field(..., description="Comentário sobre a taxa de mortalidade")
    comentario_crescimento: str = Field(..., description="Comentário sobre a taxa de crescimento de casos")
    comentario_ocupacao_uti: str = Field(..., description="Comentário sobre a taxa de ocupação de UTI")
    comentario_vacinacao: str = Field(..., description="Comentário sobre a taxa de vacinação")
    comentario_noticia: str = Field(..., description="Comentário geral baseado nas notícias recentes")

