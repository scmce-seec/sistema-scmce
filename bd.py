import streamlit as st
import pandas as pd
import plotly.express as px 
from utils import carregar_df, my_metric
from mitosheet.streamlit.v1 import spreadsheet # Import do Mito

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Obras", layout="wide")

# --- CARREGAMENTO DE DADOS (GLOBAL) ---
planilha = st.secrets["planilha"]
aba = st.secrets["aba_bd"]

data = carregar_df(planilha, aba)


# --- TRATAMENTO DE DADOS (LIMPEZA) ---
# Tratamento básico de string
data["MUNICÍPIO"] = data["MUNICÍPIO"].astype(str).str.strip()

data_analise = data.copy()

def limpar_moeda(valor):
    if isinstance(valor, str):
        # Remove R$, espaços e pontos de milhar, troca vírgula por ponto
        limpo = valor.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        try:
            return float(limpo)
        except ValueError:
            return 0.0
    return valor if isinstance(valor, (int, float)) else 0.0

# Aplica a limpeza se a coluna existir
if "VALOR" in data.columns:
    data["VALOR"] = data["VALOR"].apply(limpar_moeda)

st.title("📝 Banco de Dados - Obras")

# --- CRIAÇÃO DAS ABAS ---
tab1, tab2 = st.tabs(["Dashboard & Filtros", "Análise Avançada"])

# ==============================================================================
# ABA 1: DASHBOARD COM FILTROS LOCAIS
# ==============================================================================
with tab1:
    # --- ÁREA DE FILTROS (DENTRO DA ABA) ---
    with st.expander("🔍 Filtros da Visualização", expanded=True):
        # Organizando em colunas para ficar visualmente agradável como no exemplo
        col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
        
        # Cópia local para filtragem
        df_filtrado = data.copy()
        
        with col_f1:
            # Filtro de Programa
            opcoes_prog = ["Todos"] + sorted(data["PROGRAMA"].unique().tolist())
            sel_programa = st.selectbox("Programa:", options=opcoes_prog)

        with col_f2:
            # Busca por Escola
            busca_escola = st.text_input("Buscar Escola (Nome):")

        with col_f3:
            # Filtro de DIREC
            direc_opcoes = sorted(data["DIREC"].unique().tolist())
            sel_direc = st.multiselect("DIREC:", options=direc_opcoes, placeholder="Todas")
            
        with col_f4:
             # --- LÓGICA DE FILTRO ANINHADO (CASCATA) ---
             # Se houver DIREC selecionada, filtra os municípios. 
             # Se não, mostra todos.
            if sel_direc:
                # Filtra o dataframe original apenas para pegar os municípios das DIRECs selecionadas
                mun_disponiveis = data[data["DIREC"].isin(sel_direc)]["MUNICÍPIO"].unique().tolist()
            else:
                mun_disponiveis = data["MUNICÍPIO"].unique().tolist()

            municipios_opcoes = ["Todos"] + sorted(mun_disponiveis)
            sel_municipio = st.selectbox("Município:", options=municipios_opcoes)

        with col_f5:
             # Filtro de Ano
            ano_opcoes = sorted(data["ANO"].unique().tolist())
            sel_ano = st.multiselect("Ano:", options=ano_opcoes, placeholder="Todos")

        # Lógica Específica do "Pague Predial" (Toggles)
        # Colocamos abaixo das colunas se o programa for selecionado
        filtro_concluido = False
        filtro_execucao = False
        
        if sel_programa == "MANUTENÇÃO - PAGUE PREDIAL":
            st.markdown("---")
            col_t1, col_t2, col_blank = st.columns([1, 1, 3])
            with col_t1:
                filtro_concluido = st.toggle("Mostrar 'CONCLUÍDO'")
            with col_t2:
                filtro_execucao = st.toggle("Mostrar 'EM EXECUÇÃO'")

    # --- APLICAÇÃO DOS FILTROS ---
    
    # 1. Filtro Programa e Toggles Específicos
    if sel_programa != "Todos":
        df_filtrado = df_filtrado[df_filtrado["PROGRAMA"] == sel_programa]
        
        # Lógica específica Pague Predial
        if sel_programa == "MANUTENÇÃO - PAGUE PREDIAL":
            df_filtrado = df_filtrado[df_filtrado["OS"].notna()]
            condicoes = []
            if filtro_concluido:
                condicoes.append(df_filtrado['STATUS'].str.startswith('CONCLUÍDO'))
            if filtro_execucao:
                condicoes.append(df_filtrado['STATUS'].str.startswith('EM EXECUÇÃO'))
            
            if condicoes:
                filtro_final = condicoes[0]
                for condicao in condicoes[1:]:
                    filtro_final = filtro_final | condicao
                df_filtrado = df_filtrado[filtro_final]

    # 2. Outros Filtros
    if busca_escola:
        df_filtrado = df_filtrado[df_filtrado["ESCOLA"].str.contains(busca_escola, case=False, na=False)]
    if sel_direc:
        df_filtrado = df_filtrado[df_filtrado["DIREC"].isin(sel_direc)]
    if sel_municipio != "Todos":
        df_filtrado = df_filtrado[df_filtrado["MUNICÍPIO"] == sel_municipio]
    if sel_ano:
        df_filtrado = df_filtrado[df_filtrado["ANO"].isin(sel_ano)]

    # --- MÉTRICAS E GRÁFICOS ---
    blue = (150, 173, 231)
    green = (172, 231, 150)
    red = (231, 150, 166)
    yellow = (255, 253, 125)

    st.write("")

    def formatar_moeda_visual(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        my_metric("Total Geral", len(df_filtrado), red, "fas fa-clipboard-list")
    with col2:
        qtd_execucao = len(df_filtrado[df_filtrado["STATUS"].str.startswith("EM EXECUÇÃO", na=False)])
        my_metric("Em Execução", qtd_execucao, green, "fas fa-hammer")
    with col3:
        qtd_concluido = len(df_filtrado[df_filtrado["STATUS"].str.startswith("CONCLUÍDO", na=False)])
        my_metric("Concluído", qtd_concluido, blue, "fas fa-check-circle")
    with col4:
        total_fat = df_filtrado[df_filtrado["STATUS ÚNICO"] != "CANCELADO"]["VALOR"].sum()
        my_metric("Valor Total OS", formatar_moeda_visual(total_fat), yellow, "fas fa-file-invoice-dollar")

    # Gráficos
    if not df_filtrado.empty:
        col_graf1, col_graf2 = st.columns(2)

        with col_graf1:
            # GRÁFICO 1: OBRAS POR DIREC
            df_direc = df_filtrado['DIREC'].value_counts().reset_index()
            df_direc.columns = ['DIREC', 'Qtd Obras']
            
            df_direc['Ordem'] = pd.to_numeric(df_direc['DIREC'], errors='coerce')
            df_direc = df_direc.sort_values('Ordem', na_position='last')

            fig_direc = px.bar(
                df_direc, x='DIREC', y='Qtd Obras', text='Qtd Obras',
                title="Distribuição de Obras por DIREC",
                color_discrete_sequence=['#4c78a8']
            )
            fig_direc.update_traces(
                textposition='inside', textfont_color='white',
                hovertemplate='<b>DIREC:</b> %{x}<br><b>Quantidade:</b> %{y}<extra></extra>'
            )
            fig_direc.update_xaxes(type='category')
            fig_direc.update_layout(separators=",.")
            
            st.plotly_chart(fig_direc, use_container_width=True)

        with col_graf2:
            # GRÁFICO 2: FATURAMENTO POR DIREC
            df_fat = df_filtrado.groupby('DIREC')['VALOR'].sum().reset_index()
    
            # Ordenação Numérica (Mantemos isso para a ordem ficar correta: 1, 2, 3...)
            df_fat['Ordem'] = pd.to_numeric(df_fat['DIREC'], errors='coerce')
            df_fat = df_fat.sort_values('Ordem', na_position='last')

            fig_fat = px.bar(
                df_fat, x='DIREC', y='VALOR',
                title="Valor Investido por DIREC (R$)",
                text_auto='.2s',
                color_discrete_sequence=['rgb(172, 231, 150)']
            )
            
            fig_fat.update_traces(
                textposition='inside', textfont_color='black', texttemplate='R$ %{y:.2s}',
                hovertemplate='<b>DIREC:</b> %{x}<br><b>Valor:</b> R$ %{y:,.2f}<extra></extra>'
            )
            
            fig_fat.update_layout(yaxis_tickformat="R$ .2s", separators=",.")
            
            # --- A CORREÇÃO ESTÁ AQUI ---
            # Força o eixo X a mostrar todas as colunas como categorias discretas
            fig_fat.update_xaxes(type='category') 
            
            st.plotly_chart(fig_fat, use_container_width=True)

    # Tabela de Dados
    st.subheader("Detalhamento dos Dados")
    with st.expander("Visualizar Tabela Completa", expanded=True):
        colunas = ["PROCESSO", "OS", "PROGRAMA", "ESCOLA", "MUNICÍPIO", "DIREC", "DESCRIÇÃO", 
                   "ANO", "STATUS", "VALOR", "VALOR FATURADO", "SALDO CONTRATUAL", "PERCENTUAL EXECUTADO", 
                   "EMPRESA", "ASSINATURA SEEC"]
        
        cols_to_show = [c for c in colunas if c in df_filtrado.columns]
        df_display = df_filtrado[cols_to_show].copy()

        def formatar_tabela(valor):
            if pd.isna(valor) or valor == "": return "-"
            try:
                val_float = float(valor)
                return f"R$ {val_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except:
                return valor

        colunas_financeiras = ["VALOR", "VALOR FATURADO", "SALDO CONTRATUAL"]
        for col in colunas_financeiras:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(formatar_tabela)

        st.dataframe(df_display, hide_index=True, use_container_width=True)
        st.caption(f"Total de registros exibidos: {len(df_display)}")


# ==============================================================================
# ABA 2: ANÁLISE AVANÇADA (MITO)
# ==============================================================================
with tab2:
    st.header("Análise Avançada de Obras")
    st.markdown("Utilize a planilha abaixo para criar tabelas dinâmicas, filtrar e editar os dados originais.")

    # --- BLOCO DE TRATAMENTO DE DADOS ---
    
    # A. Limpeza de Colunas Financeiras (Loop para várias colunas)
    cols_financeiras = ["VALOR", "VALOR FATURADO", "SALDO CONTRATUAL"]
    
    for col in cols_financeiras:
        if col in data_analise.columns:
            data_analise[col] = data_analise[col].apply(limpar_moeda)

    # B. Tratamento de INEP (Numérico -> Inteiro -> String sem .00)
    if "INEP" in data_analise.columns:
        # 1. Garante que é número, transforma erros em NaN
        data_analise["INEP"] = pd.to_numeric(data_analise["INEP"], errors='coerce')
        # 2. Preenche vazios com 0
        data_analise["INEP"] = data_analise["INEP"].fillna(0)
        # 3. Converte para Inteiro (corta decimal) e depois para String
        data_analise["INEP"] = data_analise["INEP"].astype(int).astype(str)
        # 4. Limpeza visual: Se virou "0", volta a ser vazio ""
        data_analise["INEP"] = data_analise["INEP"].replace("0", "")

    # C. Tratamento de DIAS (Converter para Inteiro)
    if "DIAS" in data_analise.columns:
        data_analise["DIAS"] = pd.to_numeric(data_analise["DIAS"], errors='coerce').fillna(0).astype(int)

    # --- EXIBIÇÃO NO MITO ---
    # Agora passamos o dataframe 'data_analise' totalmente limpo e formatado
    dfs, code = spreadsheet(data_analise)