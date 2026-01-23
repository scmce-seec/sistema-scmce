import streamlit as st
from utils import carregar_df, my_metric

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Solicitações MP/PGE", layout="wide")

# --- CARREGAMENTO DE DADOS ---
planilha = st.secrets["planilha"]
aba = st.secrets["aba_acessibilidade"]

data = carregar_df(planilha, aba)

# --- TRATAMENTO DE DADOS (LIMPEZA) ---
# Garante que colunas de texto não tenham espaços extras
cols_texto = ["ESCOLA", "CIDADE", "SITUAÇÃO", "CRITICIDADE POR TEMPO DE PROCESSO"]
for col in cols_texto:
    if col in data.columns:
        data[col] = data[col].astype(str).str.strip()

# Cria cópia para filtrar
df_filtrado = data.copy()

st.title("⚖️ Solicitações MP, PGE e PJe - Acessibilidade")

# --- SIDEBAR (FILTROS) ---
st.sidebar.title("Filtros")

# 1. Filtro de Escola (Texto)
busca_escola = st.sidebar.text_input("Buscar Escola (Nome):")

st.sidebar.markdown("---")

# 2. Filtro de Cidade (Selectbox)
if "CIDADE" in data.columns:
    cidades = sorted(data['CIDADE'].dropna().unique().tolist())
    # Remove vazios
    cidades = [x for x in cidades if x != '' and x.lower() != 'nan']
    sel_cidade = st.sidebar.selectbox("Cidade:", options=["Todas"] + cidades)
else:
    sel_cidade = "Todas"

# 3. Filtro de Criticidade (Multiselect)
if "CRITICIDADE POR TEMPO DE PROCESSO" in data.columns:
    opcoes_crit = sorted(data["CRITICIDADE POR TEMPO DE PROCESSO"].dropna().unique().tolist())
    opcoes_crit = [x for x in opcoes_crit if x != '' and x.lower() != 'nan']
    sel_crit = st.sidebar.multiselect("Criticidade:", options=opcoes_crit, placeholder="Todas")
else:
    sel_crit = []

# 4. Filtro de Situação (Opcional, mas útil já que pintamos os 'PRONTO')
if "SITUAÇÃO" in data.columns:
    opcoes_situacao = sorted(data["SITUAÇÃO"].unique().tolist())
    opcoes_situacao = [x for x in opcoes_situacao if x != '' and x.lower() != 'nan']
    sel_situacao = st.sidebar.multiselect("Situação:", options=opcoes_situacao, placeholder="Todas")
else:
    sel_situacao = []

# --- APLICAÇÃO DOS FILTROS ---
if busca_escola:
    df_filtrado = df_filtrado[df_filtrado["ESCOLA"].str.contains(busca_escola, case=False, na=False)]

if sel_cidade != "Todas":
    df_filtrado = df_filtrado[df_filtrado["CIDADE"] == sel_cidade]

if sel_crit:
    df_filtrado = df_filtrado[df_filtrado["CRITICIDADE POR TEMPO DE PROCESSO"].isin(sel_crit)]

if sel_situacao:
    df_filtrado = df_filtrado[df_filtrado["SITUAÇÃO"].isin(sel_situacao)]


# --- 1. BLOCO DE MÉTRICAS E GRÁFICOS ---
# Definição de cores (Pastel)
C_BLUE  = 'rgb(150, 173, 231)'
C_GREEN = 'rgb(172, 231, 150)'
C_RED   = 'rgb(231, 150, 166)'

t_blue = (150, 173, 231)
t_green = (172, 231, 150)
t_red = (231, 150, 166)

st.write("")

# Linha 1: KPIs
col1, col2, col3 = st.columns(3)

with col1:
    my_metric("Quantidade", len(df_filtrado), t_blue, "fas fa-gavel")

with col2:
    # Conta quantos estão 'PRONTO'
    if "SITUAÇÃO" in df_filtrado.columns:
        qtd_prontos = len(df_filtrado[df_filtrado["SITUAÇÃO"].str.upper() == "PRONTO"])
    else:
        qtd_prontos = 0
    my_metric("Prontos", qtd_prontos, t_green, "fas fa-check-double")

with col3:
    # Conta quantos tem a palavra 'URGENTE' na criticidade (exemplo) ou apenas total filtrado
    # Ajuste a lógica conforme seus dados reais de criticidade
    qtd_critico = len(df_filtrado) - qtd_prontos # Exemplo genérico: Pendentes
    my_metric("Pendentes / Em Análise", qtd_critico, t_red, "fas fa-clock")


# --- 2. TABELA DE DADOS (FUNDO) ---
st.write("")
st.subheader("Detalhamento dos Processos")

with st.expander("Visualizar Tabela Completa", expanded=True):
    # Colunas principais para exibir (ajuste conforme o nome real na planilha se precisar)
    # Se quiser mostrar tudo, basta usar df_filtrado diretamente
    
    df_display = df_filtrado.copy()

    # Função de Estilo
    def pintar_linha(linha):
        val = str(linha.get('SITUAÇÃO', '')).strip().upper()
        if val == 'PRONTO':
            return ['background-color: lightgreen; color: black'] * len(linha)
        else:
            return [''] * len(linha)

    # Aplica o estilo e exibe
    st.dataframe(
        df_display.style.apply(pintar_linha, axis=1), 
        hide_index=True, 
        use_container_width=True
    )
    
    st.caption(f"Total de registros exibidos: {len(df_display)}")