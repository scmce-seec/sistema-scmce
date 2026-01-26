import streamlit as st
import pandas as pd
import plotly.express as px
from utils import carregar_df, my_metric

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Pague Predial", layout="wide")

# --- CARREGAMENTO DE DADOS ---
planilha = st.secrets["planilha"]
aba = st.secrets["aba_pague"] 

data = carregar_df(planilha, aba)

# --- TRATAMENTO DE DADOS (CONSOLIDAÇÃO) ---
def consolidar_colunas(row, colunas_alvo):
    """Junta valores de várias colunas em uma só, ignorando vazios."""
    valores = [str(row[c]) for c in colunas_alvo if c in row and pd.notna(row[c]) and str(row[c]).strip() != ""]
    return " | ".join(valores) if valores else "-"

# 1. Consolidar ÁREA DE AÇÃO
cols_area = ["Área de Ação (Baixa)", "Área de Ação (Média)"]
data["Área Unificada"] = data.apply(consolidar_colunas, axis=1, colunas_alvo=cols_area)

# 2. Consolidar DESCRIÇÃO
cols_descricao = [
    "Descrição do Serviço (Baixa - Hidráulica)",
    "Descrição do Serviço (Baixa - Elétrica)",
    "Descrição do Serviço (Baixa - Alvenaria/Marcenaria)",
    "Descrição do Serviço (Baixa - Limpeza de Vegetação)",
    "Descrição do Serviço (Baixa - Manutenção de Ar Condicionado)",
    "Relato Problema Estrutural (Média)",
    "Dúvida (Alta)"
]
data["Descrição Unificada"] = data.apply(consolidar_colunas, axis=1, colunas_alvo=cols_descricao)

# 3. Consolidar DOCUMENTOS/PROPOSTAS
cols_docs = [
    "Proposta de Preço (Baixa)",
    "Proposta de Preço (Média)",
    "Ofício de Solicitação DIREC (Alta)"
]
data["Documentos Unificados"] = data.apply(consolidar_colunas, axis=1, colunas_alvo=cols_docs)

# 4. Ajuste de Data e Criação de Coluna ANO
if "Data" in data.columns:
    data["Data"] = pd.to_datetime(data["Data"], dayfirst=True, errors='coerce')
    data["ANO"] = data["Data"].dt.year # Cria coluna auxiliar de ano para o filtro
    data["Data"] = data["Data"].dt.date # Remove a hora para visualização

# Cria cópia para filtrar
df_filtrado = data.copy()

st.title("🏫 Pague Predial - Solicitações de Manutenção")

# --- SIDEBAR (FILTROS) ---
st.sidebar.title("Filtros")

# 1. Filtro de Escola
busca_escola = st.sidebar.text_input("Buscar Escola (Nome):")

st.sidebar.markdown("---")

# 2. Filtro de Município
if "Município" in data.columns:
    opcoes_mun = ["Todos"] + sorted(data["Município"].dropna().unique().tolist())
    sel_municipio = st.sidebar.selectbox("Selecione o Município:", options=opcoes_mun)
else:
    sel_municipio = "Todos"

# 3. Filtro de Situação Estrutural
if "Situação Estrutural" in data.columns:
    opcoes_sit = ["Todas"] + sorted(data["Situação Estrutural"].dropna().unique().tolist())
    sel_situacao = st.sidebar.selectbox("Situação Estrutural:", options=opcoes_sit)
else:
    sel_situacao = "Todas"

# 4. Filtro Condicional (Área de Ação)
sel_area = [] 
if sel_situacao == "Baixa complexidade":
    if "Área de Ação (Baixa)" in data.columns:
        opcoes_area_baixa = sorted(data["Área de Ação (Baixa)"].dropna().unique().tolist())
        sel_area = st.sidebar.multiselect("Área de Ação (Baixa):", options=opcoes_area_baixa, placeholder="Todos")

elif sel_situacao == "Média complexidade":
    if "Área de Ação (Média)" in data.columns:
        opcoes_area_media = sorted(data["Área de Ação (Média)"].dropna().unique().tolist())
        sel_area = st.sidebar.multiselect("Área de Ação (Média):", options=opcoes_area_media, placeholder="Todos")

# 5. Filtro de Ano (ATUALIZADO)
sel_ano = []
if "ANO" in data.columns:
    # Ordenei reverso para o ano mais atual aparecer primeiro na lista
    ano_opcoes = sorted(data["ANO"].dropna().astype(int).unique().tolist(), reverse=True)
    sel_ano = st.sidebar.multiselect("Selecione o ano:", options=ano_opcoes, placeholder="Todos")

# --- APLICAÇÃO DOS FILTROS ---
if busca_escola:
    df_filtrado = df_filtrado[df_filtrado["Escola"].str.contains(busca_escola, case=False, na=False)]

if sel_municipio != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Município"] == sel_municipio]

if sel_situacao != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Situação Estrutural"] == sel_situacao]

if sel_area:
    if sel_situacao == "Baixa complexidade":
        df_filtrado = df_filtrado[df_filtrado["Área de Ação (Baixa)"].isin(sel_area)]
    elif sel_situacao == "Média complexidade":
        df_filtrado = df_filtrado[df_filtrado["Área de Ação (Média)"].isin(sel_area)]

if sel_ano:
    df_filtrado = df_filtrado[df_filtrado["ANO"].isin(sel_ano)]

# ORDENAÇÃO POR DATA (Mais recente primeiro)
if "Data" in df_filtrado.columns:
    df_filtrado = df_filtrado.sort_values(by="Data", ascending=False)


# --- 1. BLOCO DE MÉTRICAS E GRÁFICOS ---
# Definição de cores
t_blue = (150, 173, 231)   # Total
t_red = (231, 150, 166)    # Alta
t_orange = (255, 204, 102) # Média
t_green = (172, 231, 150)  # Baixa

# Cores para gráficos Plotly
C_GREEN = 'rgb(172, 231, 150)'
C_RED   = 'rgb(231, 150, 166)'
C_BLUE  = 'rgb(150, 173, 231)'
C_ORANGE = 'rgb(255, 204, 102)'

st.write("")

# Linha 1: KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    my_metric("Total Solicitações", len(df_filtrado), t_blue, "fas fa-clipboard-list")

with col2:
    qtd_alta = len(df_filtrado[df_filtrado["Situação Estrutural"] == "Alta complexidade"])
    my_metric("Alta Complexidade", qtd_alta, t_red, "fas fa-exclamation-triangle")

with col3:
    qtd_media = len(df_filtrado[df_filtrado["Situação Estrutural"] == "Média complexidade"])
    my_metric("Média Complexidade", qtd_media, t_orange, "fas fa-exclamation-circle")

with col4:
    qtd_baixa = len(df_filtrado[df_filtrado["Situação Estrutural"] == "Baixa complexidade"])
    my_metric("Baixa Complexidade", qtd_baixa, t_green, "fas fa-tools")


# Linha 2: Gráficos
if not df_filtrado.empty:
    col4, col5 = st.columns(2)
    
    with col4:
        # GRÁFICO 1: Distribuição por Complexidade
        df_sit = df_filtrado["Situação Estrutural"].value_counts().reset_index()
        df_sit.columns = ["Situação", "Quantidade"]
        
        fig_pie = px.pie(
            df_sit, values="Quantidade", names="Situação",
            title="Distribuição por Complexidade",
            color_discrete_sequence=[C_GREEN, C_RED, C_ORANGE, C_BLUE]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col5:
        # GRÁFICO 2: Top 10 DIREC
        df_direc = df_filtrado["DIREC"].value_counts().head(10).reset_index()
        df_direc.columns = ["DIREC", "Quantidade"]
        
        fig_bar = px.bar(
            df_direc, x="DIREC", y="Quantidade",
            title="Top 10 DIREC com mais solicitações",
            text_auto=True,
            color_discrete_sequence=[C_BLUE]
        )
        fig_bar.update_layout(yaxis_title=None, xaxis_title=None)
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")


# --- 2. TABELA DE DADOS (CONSOLIDADA) ---
st.write("")
st.subheader("Detalhamento das Solicitações")

with st.expander("Visualizar Tabela Completa", expanded=True):
    colunas_finais = [
        "Data", 
        "DIREC", 
        "Município", 
        "Escola", 
        "Situação Estrutural", 
        "Área Unificada",       
        "Descrição Unificada",  
        "Processo SEI (Alta)", 
        "Documentos Unificados" 
    ]

    cols_to_show = [c for c in colunas_finais if c in df_filtrado.columns]
    
    df_display = df_filtrado[cols_to_show].copy()

    # Formatação de Data para String (Dia/Mês/Ano)
    if "Data" in df_display.columns:
        # Garante que é datetime antes de formatar
        df_display["Data"] = pd.to_datetime(df_display["Data"]).dt.strftime('%d/%m/%Y')

    st.dataframe(df_display, hide_index=True, use_container_width=True)
    st.caption(f"Total de registros exibidos: {len(df_display)}")