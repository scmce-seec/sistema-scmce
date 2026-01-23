import streamlit as st
import pandas as pd
from utils import carregar_df

# Configuração da página
st.set_page_config(page_title="Censo", layout="wide")
st.title("📊 Censo")

# --- CARREGAMENTO DE DADOS ---
planilha = st.secrets["planilha"]
aba = st.secrets["aba_censo"]

data = carregar_df(planilha, aba)

# --- 1. TRATAMENTO PRÉVIO DO ANO (Para o filtro funcionar) ---
if "NU_ANO_CENSO" in data.columns:
    # Remove o .0 se vier como float (ex: 2023.0 -> 2023)
    data["NU_ANO_CENSO"] = data["NU_ANO_CENSO"].astype(str).str.replace(r'\.0$', '', regex=True)

# Cria uma coluna com nome da escola e municipio
data['ESCOLA_MUNICIPIO'] = data['NO_ENTIDADE'] + ' - ' + data['NO_MUNICIPIO']

# Converter colunas para string
data["CO_ENTIDADE"] = data["CO_ENTIDADE"].astype(str)
data["CO_ORGAO_REGIONAL"] = data["CO_ORGAO_REGIONAL"].astype(str)
data["NU_TELEFONE"] = data["NU_TELEFONE"].astype('Int64')
data["CO_CEP"] = data["CO_CEP"].astype(str)
data["MATRICULAS_TOTAIS"] = data["MATRICULAS_TOTAIS"].astype('Int64')
data["MATRICULAS_FUND"] = data["MATRICULAS_FUND"].astype('Int64')
data["MATRICULAS_MED"] = data["MATRICULAS_MED"].astype('Int64')
data["MATRICULAS_PROF"] = data["MATRICULAS_PROF"].astype('Int64')
data["MATRICULAS_EJA"] = data["MATRICULAS_EJA"].astype('Int64')
data["SALAS"] = data["SALAS"].astype('Int64')
data["SALAS_CLIMATIZADAS"] = data["SALAS_CLIMATIZADAS"].astype('Int64')
data["SALAS_ACESSIVEIS"] = data["SALAS_ACESSIVEIS"].astype('Int64')
data["DOCENTES_TOTAIS"] = data["DOCENTES_TOTAIS"].astype('Int64')


# --- 2. FILTRO DE ANO (ADICIONADO AQUI) ---
st.sidebar.title("Filtros")

# Pega os anos únicos, ordena do maior para o menor
anos_disponiveis = sorted(data["NU_ANO_CENSO"].unique().tolist(), reverse=True)

# index=0 faz vir selecionado o primeiro da lista (o mais recente)
ano_selecionado = st.sidebar.selectbox(
    "Selecione o Ano do Censo:", 
    anos_disponiveis, 
    index=0
)

# Cria uma cópia dos dados filtrada pelo ano escolhido
# Todo o restante do código vai usar 'data_filtrada' em vez de 'data'
data_filtrada = data[data["NU_ANO_CENSO"] == ano_selecionado]


# --- A PARTIR DAQUI, SUA ESTRUTURA ORIGINAL (Usando data_filtrada) ---

# Usamos .unique() para não ter opções repetidas e sorted() para ordenar.
# Alterado para ler de data_filtrada
opcoes_formatadas = sorted(data_filtrada['ESCOLA_MUNICIPIO'].unique().tolist())


# Usamos a lista de opções formatadas.
escola_selecionada_formatada = st.selectbox(
    "Escolha uma escola para visualizar as informações:",
    opcoes_formatadas,
    index=None,
    placeholder="Digite o nome da escola ou selecione abaixo..."
)


# Primeiro, verificamos se o usuário de fato selecionou uma opção.
if escola_selecionada_formatada:
    # Filtramos o DataFrame (AGORA O FILTRADO) pela coluna combinada
    escola_filtrada = data_filtrada[data_filtrada['ESCOLA_MUNICIPIO'] == escola_selecionada_formatada]

    # Agora usamos a sua lógica de verificação.
    if escola_filtrada.empty:
        st.warning("Ocorreu um erro. Nenhuma escola encontrada com os dados selecionados.")
    else:
        # Extraímos a primeira (e única) linha do DataFrame filtrado.
        escola = escola_filtrada.iloc[0]

    # Exibindo informações principais da escola
    st.markdown(f"""
    ### 🏫 {escola["NO_ENTIDADE"]}
    - 📅 **Ano Censo:** {escola["NU_ANO_CENSO"]}
    - 📫 **Endereço:** {escola["ENDEREÇO"]}
    - 📍 **Município:** {escola["NO_MUNICIPIO"]}
    - 🏢 **DIREC:** {escola["CO_ORGAO_REGIONAL"]}
    - 🔢 **INEP:** {escola["CO_ENTIDADE"]}
    - ☎️ **Telefone:** {escola["NU_TELEFONE"] if pd.notna(escola["NU_TELEFONE"]) else "Não informado"}
    - 🌍 **Localização:** {escola["LOCALIZAÇÃO"]}
    - 🏫 **Etapas de Ensino:** {escola["ETAPAS"]}
    - 📚 **Modalidade:** {escola["MODALIDADE"]}
    - 🕒 **Integralização:** {escola["INTEGRALIZAÇÃO"]}
    """)

    # Exibindo número total de docentes
    st.markdown(f"👩‍🏫 **Docentes Totais:** {escola['DOCENTES_TOTAIS']}")

    # Exibindo Matrículas Totais (logo acima, sem expander)
    st.markdown(f"🔢 **Matrículas Totais:** {escola['MATRICULAS_TOTAIS']}")

    # Expansor para detalhes das Matrículas
    with st.expander("Clique para ver as matrículas detalhadas"):
        st.markdown(f"""
        - 📊 **Matrículas Ensino Fundamental:** {escola["MATRICULAS_FUND"]}
        - 📊 **Matrículas Ensino Médio:** {escola["MATRICULAS_MED"]}
        - 👩‍🏫 **Matrículas Profissionais:** {escola["MATRICULAS_PROF"]}
        - 🧑‍🎓 **Matrículas EJA:** {escola["MATRICULAS_EJA"]}
        """)

    
    # Exibindo Acessibilidade (logo acima, sem expander)
    st.markdown(f"🏫 **Acessibilidade Geral:** {escola['ACESSIBILIDADE']}")


    # Expansor para Acessibilidade
    with st.expander("Clique para ver detalhes de acessibilidade"):
        st.markdown(f"""
        - 🚪 **Corrimão:** {'Sim' if escola["ACESS_CORRIMAO"] == "Sim" else 'Não'}
        - 🛗 **Elevador:** {'Sim' if escola["ACESS_ELEVADOR"] == "Sim" else 'Não'}
        - 🏢 **Pisos Táteis:** {'Sim' if escola["ACESS_PISOS"] == "Sim" else 'Não'}
        - 🚶‍♂️ **Vão Livre:** {'Sim' if escola["ACESS_VAO"] == "Sim" else 'Não'}
        - ♿ **Rampas:** {'Sim' if escola["ACESS_RAMPAS"] == "Sim" else 'Não'}
        - 🔊 **Sinal Sonoro:** {'Sim' if escola["ACESS_SINAL_SONORO"] == "Sim" else 'Não'}
        - 📝 **Sinal Tátil:** {'Sim' if escola["ACESS_SINAL_TATIL"] == "Sim" else 'Não'}
        - 🖼️ **Sinal Visual:** {'Sim' if escola["ACESS_SINAL_VISUAL"] == "Sim" else 'Não'}
        - 📑 **Sinalização:** {'Sim' if escola["ACESS_SINALIZAÇÃO"] == "Sim" else 'Não'}
        """)

    # Exibindo Salas (Total logo acima, sem expander)
    st.markdown(f"🏢 **Salas Totais:** {escola['SALAS']}")

    # Expansor para detalhes das Salas
    with st.expander("Clique para ver detalhes das salas"):
        st.markdown(f"""
        - ❄️ **Salas Climatizadas:** {escola["SALAS_CLIMATIZADAS"]}
        - ♿ **Salas Acessíveis:** {escola["SALAS_ACESSIVEIS"]}
        """)

    st.markdown(f"**🛠️ Infraestutura**")

    # Expansor para Infraestrutura
    with st.expander("Clique para ver detalhes da infraestrutura"):
        st.markdown(f"""
        - 🏀 **Quadra:** {escola["QUADRA"]}
        - 🏊‍♂️ **Piscina:** {escola["PISCINA"]}
        """)