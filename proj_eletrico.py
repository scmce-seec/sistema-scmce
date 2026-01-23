import streamlit as st
import plotly.express as px
from utils import carregar_df, my_metric

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Projetos Elétricos", layout="wide")


# --- CARREGAMENTO DE DADOS ---
planilha = st.secrets["planilha"]
aba = st.secrets["aba_eletrico"]

data = carregar_df(planilha, aba)

# --- TRATAMENTO DE DADOS (LIMPEZA/PREPARAÇÃO) ---
# Garante que colunas de texto não tenham espaços extras
cols_texto = ["Projetista", "Orçamento", "Projeto", "Tipo de Projeto"]
for col in cols_texto:
    if col in data.columns:
        data[col] = data[col].astype(str).str.strip()

# Cria cópia para filtrar
df_filtrado = data.copy()

st.title("💡 Projetos Elétricos")

# --- SIDEBAR (FILTROS) ---
st.sidebar.title("Filtros")

# 1. Filtro de Escola (Texto)
busca_escola = st.sidebar.text_input("Buscar Escola (Nome):")

st.sidebar.markdown("---")

# 2. Filtro de Projetista (Lista/Multiselect)
if "Projetista" in data.columns:
    opcoes_projetista = sorted(data["Projetista"].unique().tolist())
    # Remove valores vazios ou 'nan'
    opcoes_projetista = [x for x in opcoes_projetista if str(x).lower() != 'nan' and str(x) != '']
    sel_projetista = st.sidebar.multiselect("Projetista:", options=opcoes_projetista, placeholder="Todos")
else:
    sel_projetista = []

# 3. Filtro de Projeto (NOVO)
if "Projeto" in data.columns:
    opcoes_projeto = sorted(data["Projeto"].unique().tolist())
    # Remove valores vazios ou 'nan'
    opcoes_projeto = [x for x in opcoes_projeto if str(x).lower() != 'nan' and str(x) != '']
    sel_projeto = st.sidebar.multiselect("Situação do Projeto:", options=opcoes_projeto, placeholder="Todos")
else:
    sel_projeto = []

# 4. Filtro de Orçamento (Lista/Multiselect)
if "Orçamento" in data.columns:
    opcoes_orcamento = sorted(data["Orçamento"].unique().tolist())
    opcoes_orcamento = [x for x in opcoes_orcamento if str(x).lower() != 'nan' and str(x) != '']
    sel_orcamento = st.sidebar.multiselect("Orçamento (Status):", options=opcoes_orcamento, placeholder="Todos")
else:
    sel_orcamento = []

# --- APLICAÇÃO DOS FILTROS ---
if busca_escola:
    df_filtrado = df_filtrado[df_filtrado["Nome da Escola Estadual"].str.contains(busca_escola, case=False, na=False)]

if sel_projetista:
    df_filtrado = df_filtrado[df_filtrado["Projetista"].isin(sel_projetista)]

if sel_projeto: # Aplicação do novo filtro
    df_filtrado = df_filtrado[df_filtrado["Projeto"].isin(sel_projeto)]

if sel_orcamento:
    df_filtrado = df_filtrado[df_filtrado["Orçamento"].isin(sel_orcamento)]


# --- 1. BLOCO DE MÉTRICAS E GRÁFICOS ---
# Definição de cores (Pastel)
C_BLUE  = 'rgb(150, 173, 231)'
C_GREEN = 'rgb(172, 231, 150)'
C_RED   = 'rgb(231, 150, 166)'

# Cores em Tupla para my_metric
t_blue = (150, 173, 231)
t_green = (172, 231, 150)
t_red = (231, 150, 166)

st.write("")

# Linha 1: KPIs
col1, col2, col3 = st.columns(3)

with col1:
    my_metric("Quantidade", len(df_filtrado), t_blue, "fas fa-folder")

with col2:
    # Conta quantos estão com status "Pronto" na coluna Projeto
    qtd_prontos = len(df_filtrado[df_filtrado["Projeto"].str.lower() == "pronto"])
    my_metric("Prontos", qtd_prontos, t_green, "fas fa-check")

with col3:
    # Tenta contar quantos estão em execução (se a coluna existir e tiver dados)
    if "Execução de Obra" in df_filtrado.columns:
        qtd_exec = len(df_filtrado[df_filtrado["Execução de Obra"].str.contains("execução", case=False, na=False)])
    else:
        qtd_exec = 0
    my_metric("Em Execução", qtd_exec, t_red, "fas fa-hard-hat")


# Linha 2: Gráficos
if not df_filtrado.empty:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # GRÁFICO 1: Projetos por Projetista
        df_proj = df_filtrado["Projetista"].value_counts().reset_index()
        df_proj.columns = ["Projetista", "Quantidade"]
        
        fig_bar = px.bar(
            df_proj, x="Projetista", y="Quantidade",
            title="Projetos por Projetista",
            text_auto=True,
            color_discrete_sequence=[C_BLUE]
        )
        fig_bar.update_layout(yaxis_title=None, xaxis_title=None)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_g2:
        # GRÁFICO 2: Status do Projeto (Pizza)
        if "Projeto" in df_filtrado.columns:
            df_status = df_filtrado["Projeto"].value_counts().reset_index()
            df_status.columns = ["Status", "Quantidade"]
            
            fig_pie = px.pie(
                df_status, values="Quantidade", names="Status",
                title="Status dos Projetos",
                color_discrete_sequence=[C_GREEN, C_RED, C_BLUE]
            )
            st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")


# --- 2. TABELA DE DADOS (FUNDO) ---
st.write("")
st.subheader("Detalhamento dos Projetos")

with st.expander("Visualizar Tabela Completa", expanded=True):
    colunas_desejadas = ["DIREC", "Nome da Escola Estadual", "Munícipio", 
                         "Projeto", "Tipo de Projeto", "Projetista", "Observações", 
                         "Orçamento", "Execução de Obra", "Nada Consta"]
    
    # Filtra colunas existentes para evitar erro
    cols_to_show = [c for c in colunas_desejadas if c in df_filtrado.columns]
    
    df_display = df_filtrado[cols_to_show].copy()

    # Função de Estilo (Original sua)
    def pintar_linha(linha):
        # Verifica se 'Projeto' existe na linha e se é 'Pronto' (case insensitive para segurança)
        val = str(linha.get('Projeto', '')).strip().lower()
        if val == 'pronto':
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