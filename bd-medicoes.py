import streamlit as st
import pandas as pd
import plotly.express as px # Importação necessária para os gráficos
from utils import carregar_df, my_metric

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Medições", layout="wide")

# --- CARREGAMENTO DE DADOS ---
planilha = st.secrets["planilha"]
aba = st.secrets["aba_medicoes"]

data = carregar_df(planilha, aba)

# --- TRATAMENTO DE DADOS (LIMPEZA) ---
def limpar_moeda(valor):
    if isinstance(valor, str):
        limpo = valor.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try:
            return float(limpo)
        except ValueError:
            return 0.0
    return valor if isinstance(valor, (int, float)) else 0.0

# 1. Limpeza de Valor
if "VALOR" in data.columns:
    data["VALOR"] = data["VALOR"].apply(limpar_moeda)

# 2. Limpeza de Data
if "DATA CADASTRO" in data.columns:
    data["DATA CADASTRO"] = pd.to_datetime(data["DATA CADASTRO"], dayfirst=True, errors='coerce')
    data["DATA CADASTRO"] = data["DATA CADASTRO"].dt.date

# Cria cópia para filtrar
df_filtrado = data.copy()

st.title("💵 Banco de Dados - Medições")

# --- SIDEBAR (FILTROS) ---
st.sidebar.title("Filtros")

# 1. Filtro de Programa
opcoes = ["Todos"] + sorted(data["PROGRAMA"].unique().tolist())
sel_programa = st.sidebar.selectbox("Selecione o programa:", options=opcoes)

if sel_programa != "Todos":
    df_filtrado = df_filtrado[df_filtrado["PROGRAMA"] == sel_programa]

st.sidebar.markdown("---")

# 2. Filtros de Localização e Escola (COM A LÓGICA ANINHADA)
busca_escola = st.sidebar.text_input("Buscar Escola (Nome):")

# Primeiro escolhemos a DIREC
direc_opcoes = sorted(data["DIREC"].unique().tolist())
sel_direc = st.sidebar.multiselect("Selecione a DIREC:", options=direc_opcoes, placeholder="Todas") 

# --- AQUI ESTÁ A MUDANÇA (FILTRO EM CASCATA) ---
if sel_direc:
    # Se tiver DIREC selecionada, mostramos apenas os municípios daquela DIREC
    # Filtramos o dataframe original 'data' para pegar os municípios corretos
    municipios_disponiveis = data[data['DIREC'].isin(sel_direc)]["MUNICÍPIO"].unique().tolist()
else:
    # Se não tiver DIREC selecionada, mostra todos os municípios
    municipios_disponiveis = data["MUNICÍPIO"].unique().tolist()

# Monta a lista e cria o selectbox
municipios_opcoes = ["Todos"] + sorted(municipios_disponiveis)
sel_municipio = st.sidebar.selectbox("Selecione o município:", options=municipios_opcoes)

# 3. Filtro de Ano
ano_opcoes = sorted(data["ANO FISCAL"].unique().tolist())
sel_ano = st.sidebar.multiselect("Selecione o ano:", options=ano_opcoes, placeholder="Todos")

# --- APLICAÇÃO DOS FILTROS ---
if busca_escola:
    df_filtrado = df_filtrado[df_filtrado["ESCOLA"].str.contains(busca_escola, case=False, na=False)]
if sel_direc:
    df_filtrado = df_filtrado[df_filtrado["DIREC"].isin(sel_direc)]
if sel_municipio != "Todos":
    df_filtrado = df_filtrado[df_filtrado["MUNICÍPIO"] == sel_municipio]
if sel_ano:
    df_filtrado = df_filtrado[df_filtrado["ANO FISCAL"].isin(sel_ano)]


# --- 1. BLOCO DE MÉTRICAS E GRÁFICOS ---
C_BLUE  = 'rgb(150, 173, 231)'
C_GREEN = 'rgb(172, 231, 150)'
C_RED   = 'rgb(231, 150, 166)'
t_red = (231, 150, 166)
t_green = (172, 231, 150)

def formatar_moeda_visual(valor):
    if pd.isna(valor): return "R$ 0,00"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.write("")

# Linha 1: KPIs
col1, col2 = st.columns(2)
with col1:
    my_metric("Quantidade", len(df_filtrado), t_red, "fas fa-clipboard-list")
with col2:
    valor_faturado = df_filtrado["VALOR"].sum()
    my_metric("Valor Faturado", formatar_moeda_visual(valor_faturado), t_green, "fas fa-file-invoice-dollar")

# Linha 2: Gráficos
if not df_filtrado.empty:
    col3, col4 = st.columns(2)
    
    with col3:
        # GRÁFICO DE LINHA
        df_line = df_filtrado["DATA CADASTRO"].value_counts().sort_index().reset_index()
        df_line.columns = ["Data", "Quantidade"]
        
        fig_line = px.line(
            df_line, x="Data", y="Quantidade",
            title="Evolução de Medições (Dia a Dia)",
            markers=True,
            color_discrete_sequence=[C_BLUE]
        )
        fig_line.update_layout(yaxis_title=None, xaxis_title=None)
        st.plotly_chart(fig_line, use_container_width=True)

    with col4:
        # GRÁFICO DE BARRAS
        df_fonte = df_filtrado.groupby("FONTE")["VALOR"].sum().reset_index()
        df_fonte = df_fonte.sort_values("VALOR", ascending=True) 
        max_valor = df_fonte["VALOR"].max()

        fig_bar = px.bar(
            df_fonte, x="VALOR", y="FONTE", 
            orientation='h', 
            title="Valor Gasto por Fonte",
            text_auto='.2s',
            color_discrete_sequence=[C_GREEN] 
        )
        fig_bar.update_traces(
            textfont_color='black', textposition='outside', texttemplate='R$ %{x:.2s}',
            hovertemplate='<b>Fonte:</b> %{y}<br><b>Valor:</b> R$ %{x:,.2f}<extra></extra>', cliponaxis=False
        )
        fig_bar.update_layout(
            yaxis_title=None, xaxis_title=None, separators=",.",
            xaxis_range=[0, max_valor * 1.2] 
        )
        st.plotly_chart(fig_bar, use_container_width=True)

else:
    st.warning("Nenhum dado encontrado para gerar os gráficos.")


# --- 2. TABELA DE DADOS ---
st.write("")
st.subheader("Detalhamento das Medições")

with st.expander("Visualizar Tabela Completa", expanded=True):
    colunas = ['PROCESSO', 'ESCOLA', 'MUNICÍPIO', 'DIREC', 'VALOR', 'MEDIÇÃO', 
               'DATA CADASTRO', 'PROGRAMA', 'FONTE', 'DATA NF', 'EMPENHO', 
               'DATA ORDEM BANCARIA', 'COMENTÁRIOS', 'ANO FISCAL']

    cols_to_show = [c for c in colunas if c in df_filtrado.columns]
    df_display = df_filtrado[cols_to_show].copy()

    if "VALOR" in df_display.columns:
        df_display["VALOR"] = df_display["VALOR"].apply(formatar_moeda_visual)

    st.dataframe(df_display, hide_index=True, use_container_width=True)
    st.caption(f"Total de registros exibidos: {len(df_display)}")