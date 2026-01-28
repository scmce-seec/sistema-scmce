import streamlit as st
import pandas as pd
import plotly.express as px 
from utils import carregar_df, my_metric
#from mitosheet.streamlit.v1 import spreadsheet

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Empenhos", layout="wide")

# --- CARREGAMENTO DE DADOS (GLOBAL) ---
# Isso acontece antes das abas para os dados estarem disponíveis em ambas
planilha = st.secrets["planilha"] 
aba = st.secrets["aba_empenho"] 

data = carregar_df(planilha, aba)

# --- TRATAMENTO DE DADOS (LIMPEZA) ---
def limpar_moeda_empenho(valor):
    if isinstance(valor, str):
        limpo = valor.replace('R$', '').replace(' ', '').replace('.', '')
        limpo = limpo.replace(',', '.')
        try:
            return float(limpo)
        except ValueError:
            return 0.0
    return valor if isinstance(valor, (int, float)) else 0.0

if "VALOR" in data.columns:
    data["VALOR"] = data["VALOR"].apply(limpar_moeda_empenho)
    data = data.dropna(subset=['VALOR'])

if "DIREC" in data.columns:
    data["DIREC"] = pd.to_numeric(data["DIREC"], errors='coerce').fillna(0).astype(int)

st.title("📑 Banco de Dados - Empenhos")

# --- CRIAÇÃO DAS ABAS ---
tab1, tab2 = st.tabs(["Dashboard & Filtros", "Análise Avançada"]) 

# ==============================================================================
# ABA 1: DASHBOARD COM FILTROS LOCAIS
# ==============================================================================
with tab1:
    # --- ÁREA DE FILTROS (DENTRO DA ABA) ---
    with st.expander("🔍 Filtros da Visualização", expanded=True):
        # Mudei para st.columns(5) para caber o Tipo de NE
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
        
        # Cria uma cópia local para filtrar nesta aba
        df_filtrado = data.copy()
        
        with col_f1:
            # Filtro de Ano
            anos_lista = sorted(data["ANO"].unique().tolist())
            idx_padrao = anos_lista.index(anos_lista[-1]) if anos_lista else 0
            sel_ano = st.selectbox("Ano:", options=anos_lista, index=idx_padrao)
        
        with col_f2:
            # Busca por Empresa
            opcoes_empresas = sorted(data["EMPRESA"].dropna().unique().tolist())
            sel_empresa = st.selectbox("Empresa:", options=opcoes_empresas, index=None, placeholder="Todas")

        with col_f3:
             # Filtro de DIREC
            direc_opcoes = sorted(data["DIREC"].unique().tolist())
            direc_opcoes = [d for d in direc_opcoes if d != 0]
            sel_direc = st.multiselect("DIREC:", options=direc_opcoes, placeholder="Todas")
            
        with col_f4:
            # Busca por Empenho
            opcoes_empenhos = sorted(data["NE"].dropna().astype(str).unique().tolist())
            sel_empenho = st.selectbox("Empenho (NE):", options=opcoes_empenhos, index=None, placeholder="Todos")

        with col_f5:
            # Busca por Tipo (Adicionado aqui)
            opcoes_tipo = sorted(data["TIPO DE NE"].dropna().unique().tolist())
            sel_tipo = st.selectbox("Tipo de NE:", options=opcoes_tipo, index=None, placeholder="Todos")

    # --- APLICAÇÃO DOS FILTROS ---
    if sel_ano:
        df_filtrado = df_filtrado[df_filtrado["ANO"] == sel_ano]
    if sel_empresa:
        df_filtrado = df_filtrado[df_filtrado["EMPRESA"] == sel_empresa]
    if sel_direc:
        df_filtrado = df_filtrado[df_filtrado["DIREC"].isin(sel_direc)]
    if sel_empenho:
        df_filtrado = df_filtrado[df_filtrado["NE"].astype(str) == sel_empenho]
    if sel_tipo:
        df_filtrado = df_filtrado[df_filtrado["TIPO DE NE"].astype(str) == sel_tipo]


    # --- O RESTO DO SEU DASHBOARD (MÉTRICAS E GRÁFICOS) ---
    C_BLUE  = 'rgb(150, 173, 231)'
    C_GREEN = 'rgb(172, 231, 150)'
    t_red = (231, 150, 166)
    t_green = (172, 231, 150)

    def formatar_moeda_visual(valor):
        if pd.isna(valor): return "R$ 0,00"
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    st.write("")
    
    # KPIs
    col1, col2 = st.columns(2)
    with col1:
        my_metric("Quantidade de Empenhos", len(df_filtrado), t_red, "fas fa-file-signature")
    with col2:
        valor_total = df_filtrado["VALOR"].sum()
        my_metric("Valor Total Empenhado", formatar_moeda_visual(valor_total), t_green, "fas fa-coins")

    # Gráficos
    if not df_filtrado.empty:
        col3, col4 = st.columns(2)
        
        with col3:
            df_direc = df_filtrado.groupby("DIREC")["VALOR"].sum().reset_index().sort_values("DIREC")
    
            fig_line = px.bar(
                df_direc, x="DIREC", y="VALOR",
                title=f"Valor por DIREC ({sel_ano})",
                color_discrete_sequence=[C_BLUE]
            )
            
            fig_line.update_traces(
                textfont_color='white', textposition='inside', texttemplate='R$ %{y:.2s}',
                hovertemplate='<b>DIREC:</b> %{x}<br><b>Valor:</b> R$ %{y:,.2f}<extra></extra>'
            )
            
            fig_line.update_layout(
                yaxis_title=None, 
                xaxis_title=None, 
                separators=",.", 
                yaxis_tickformat="R$ .2s"
            )

            # --- ADICIONE ESTA LINHA ---
            fig_line.update_xaxes(type='category') 
            
            st.plotly_chart(fig_line, use_container_width=True)

        with col4:
            df_fonte = df_filtrado.groupby("FONTE")["VALOR"].sum().reset_index().sort_values("VALOR", ascending=True)
            max_valor = df_fonte["VALOR"].max()
            fig_bar = px.bar(
                df_fonte, x="VALOR", y="FONTE", orientation='h', 
                title="Valor Empenhado por Fonte", text_auto='.2s', color_discrete_sequence=[C_GREEN]
            )
            fig_bar.update_traces(
                textfont_color='black', textposition='outside', texttemplate='R$ %{x:.2s}',
                hovertemplate='<b>Fonte:</b> %{y}<br><b>Valor:</b> R$ %{x:,.2f}<extra></extra>', cliponaxis=False
            )
            fig_bar.update_layout(yaxis_title=None, xaxis_title=None, separators=",.", xaxis_range=[0, max_valor * 1.2])
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")

    # Tabela
    st.write("")
    st.subheader("Detalhamento dos Empenhos")
    with st.expander("Visualizar Tabela Completa", expanded=True):
        colunas = ["DATA", "ANO", "NE", "TIPO DE NE", "DIREC", "EMPRESA", "FONTE", "VALOR"]
        cols_to_show = [c for c in colunas if c in df_filtrado.columns]
        df_display = df_filtrado[cols_to_show].copy()
        
        if "VALOR" in df_display.columns:
            df_display["VALOR"] = df_display["VALOR"].apply(formatar_moeda_visual)

        def colorir_linhas(row):
            verde = 'background-color: #ace796; color: black'
            vermelho = 'background-color: #edb0bc; color: black'
            padrao = ''
            valor = row.get("TIPO DE NE", "")
            if valor == "Emissão": return [verde] * len(row)
            elif valor == "Anulação": return [vermelho] * len(row)
            else: return [padrao] * len(row)

        st.dataframe(df_display.style.apply(colorir_linhas, axis=1), hide_index=True, use_container_width=True)

# ==============================================================================
# ABA 2: ANÁLISE AVANÇADA (CORRIGIDA)
# ==============================================================================
with tab2:
    st.header("Análise - Fonte por Empresa")

    msg = '''OBS: **com OB** são medições com ordem bancária. Já **Ano Fiscal** são medições **com OB** e **sem OB**.'''
    st.markdown(msg)

    # 1. Carregamento de dados específicos desta aba
    aba_analise = st.secrets["aba_analise"]
    aba_saldo = st.secrets["aba_saldo"]

    data_analise = carregar_df(planilha, aba_analise)
    data_saldo = carregar_df(planilha, aba_saldo)

    # 2. TRATAMENTO DE DADOS (CRUCIAL PARA O FILTRO FUNCIONAR)
    # Convertemos a coluna 'ANO' das DUAS tabelas para número inteiro.
    # Isso evita erros se numa planilha estiver "2026" (texto) e na outra 2026 (número).
    for df in [data_analise, data_saldo]:
        if "ANO" in df.columns:
            # Converte para numérico, erros viram NaN, depois preenche com 0 e vira Inteiro
            df["ANO"] = pd.to_numeric(df["ANO"], errors='coerce').fillna(0).astype(int)

    # --- ÁREA DE FILTROS ---
    with st.expander("🔍 Filtros da Visualização", expanded=True):
        
        # Cria cópias locais para não alterar o original
        df_filtrado_analise = data_analise.copy()
        df_filtrado_saldo = data_saldo.copy()
        
        # 3. CRIAÇÃO INTELIGENTE DA LISTA DE ANOS
        # Pegamos os anos únicos da tabela de Análise E da tabela de Saldo
        anos1 = data_analise["ANO"].unique().tolist() if "ANO" in data_analise.columns else []
        anos2 = data_saldo["ANO"].unique().tolist() if "ANO" in data_saldo.columns else []
        
        # Juntamos as duas listas, usamos set() para remover duplicados e sorted() para ordenar
        # reverse=True garante que 2026 apareça antes de 2025
        todos_anos = sorted(list(set(anos1 + anos2)), reverse=True)
        
        # Removemos o 0 (caso tenha havido erro de conversão ou linha vazia)
        todos_anos = [ano for ano in todos_anos if ano != 0]

        # Define o padrão como o primeiro da lista (o mais recente)
        idx_padrao = 0 if todos_anos else None
        
        sel_ano = st.selectbox(
            "Ano:", 
            options=todos_anos, 
            index=idx_padrao, 
            key="ano_analise_combinado" 
        )

    # --- APLICAÇÃO DOS FILTROS ---
    if sel_ano:
        # Filtra a tabela 1
        if "ANO" in df_filtrado_analise.columns:
            df_filtrado_analise = df_filtrado_analise[df_filtrado_analise["ANO"] == sel_ano]
        
        # Filtra a tabela 2
        if "ANO" in df_filtrado_saldo.columns:
            df_filtrado_saldo = df_filtrado_saldo[df_filtrado_saldo["ANO"] == sel_ano]

    # --- TABELA 1: FONTE POR EMPRESA ---
    st.write("") 
    with st.expander("Visualizar Tabela Completa (Fonte por Empresa)", expanded=True):
        st.dataframe(df_filtrado_analise, hide_index=True, use_container_width=True)

    st.markdown("---")

    # --- TABELA 2: TOTAIS E SALDOS ---
    st.header("Totais e Saldos")

    st.write("")
    with st.expander("Visualizar Tabela Completa (Totais e Saldos)", expanded=True):
        st.dataframe(df_filtrado_saldo, hide_index=True, use_container_width=True)