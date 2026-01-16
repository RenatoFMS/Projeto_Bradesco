-- Estrutura da tabela de consórcios
CREATE TABLE IF NOT EXISTS grupos_consorcio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT NOT NULL,       -- Ex: Veículo, Imóvel, Moto
    nome_bem TEXT NOT NULL,        -- Nome do modelo ou tipo de bem
    valor_credito REAL NOT NULL,   -- Valor total da carta de crédito
    taxa_adm REAL NOT NULL,        -- Taxa de administração (ex: 15.0)
    prazo_meses INTEGER NOT NULL,  -- Quantidade de parcelas
    modalidade TEXT NOT NULL       -- Ex: Sorteio, Lance Livre, Lance Fixo
);

-- Índices para busca rápida (Otimização para os 2.000 itens)
CREATE INDEX IF NOT EXISTS idx_categoria ON grupos_consorcio (categoria);
CREATE INDEX IF NOT EXISTS idx_valor ON grupos_consorcio (valor_credito);
