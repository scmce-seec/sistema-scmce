import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from utils import carregar_df

# Configuração da página
st.set_page_config(page_title="Censo", layout="wide")
st.title("📊 Censo 2025")

# --- CARREGAMENTO DE DADOS ---
planilha = st.secrets["planilha"]
planilha_censo = st.secrets["planilha_censo"]
aba_censo_25 = st.secrets["aba_censo_25"]
aba_censo_25_matriculas = st.secrets["aba_censo_25_matriculas"]

# Carrega as duas tabelas
df_escolas = carregar_df(planilha, aba_censo_25)
df_matriculas = carregar_df(planilha_censo, aba_censo_25_matriculas)

# --- MERGE (UNIÃO) ---
data = pd.merge(df_escolas, df_matriculas, on="CO_ENTIDADE", how="left")

# --- TRATAMENTO DOS DADOS ---
data['ESCOLA_MUNICIPIO'] = data['NO_ENTIDADE'] + ' - ' + data['NO_MUNICIPIO']

# 1. TRATAMENTO ESPECÍFICO PARA COORDENADAS (Importante para o mapa)
for col in ["LATITUDE_C", "LONGITUDE_C"]:
    if col in data.columns:
        # Remove espaços, converte para string e troca vírgula por ponto
        data[col] = data[col].astype(str).str.strip().str.replace(',', '.')
        # Converte para numérico (float)
        data[col] = pd.to_numeric(data[col], errors='coerce')

# 2. CONVERSÃO DE INTEIROS (Para evitar o .0)
cols_to_fix = [
    "NU_TELEFONE", "MATRICULAS TOTAIS", "MATRICULAS FUND", "MATRICULAS MED",
    "MATRICULAS PROF", "MATRICULAS EJA", "SALAS", "SALAS_CLIMATIZADAS",
    "SALAS_ACESSIVEIS", "DOCENTES_TOTAIS"
]

for col in cols_to_fix:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce').astype('Int64')

# --- INTERFACE DE SELEÇÃO ---
opcoes_formatadas = sorted(data['ESCOLA_MUNICIPIO'].unique().tolist())

escola_selecionada_formatada = st.selectbox(
    "Escolha uma escola para visualizar as informações:",
    opcoes_formatadas,
    index=None,
    placeholder="Digite o nome da escola ou selecione abaixo..."
)

# --- EXIBIÇÃO ---
if escola_selecionada_formatada:
    escola_filtrada = data[data['ESCOLA_MUNICIPIO'] == escola_selecionada_formatada]
    
    if not escola_filtrada.empty:
        escola = escola_filtrada.iloc[0]

        # Informações principais
        st.markdown(f"""
        ### 🏫 {escola["NO_ENTIDADE"]}
        - 📫 **Endereço:** {escola.get("ENDEREÇO", "Não informado")}
        - 📍 **Município:** {escola["NO_MUNICIPIO"]}
        - 🏢 **DIREC:** {escola["CO_ORGAO_REGIONAL"]}
        - 🔢 **INEP:** {escola["CO_ENTIDADE"]}
        - ☎️ **Telefone:** {escola["NU_TELEFONE"] if pd.notna(escola["NU_TELEFONE"]) else "Não informado"}
        - 🌍 **Localização:** {escola["LOCALIZAÇÃO"] if pd.notna(escola["LOCALIZAÇÃO"]) else "N/A"}
        - 🏫 **Etapas de Ensino:** {escola["ETAPAS"] if pd.notna(escola["ETAPAS"]) else "N/A"}
        - 📚 **Modalidade:** {escola["MODALIDADE"] if pd.notna(escola["MODALIDADE"]) else "N/A"}
        - 🕒 **Integralização:** {escola["INTEGRALIZAÇÃO"] if pd.notna(escola["INTEGRALIZAÇÃO"]) else "Não"}
        - ✅ **Situação da Escola:** {escola["SITUAÇÃO DA ESCOLA"] if pd.notna(escola["SITUAÇÃO DA ESCOLA"]) else "N/A"}
        """)

        st.markdown(f"🔢 **Matrículas Totais (Ensino Regular):** {escola['MATRICULAS TOTAIS'] if pd.notna(escola['MATRICULAS TOTAIS']) else 'N/A'}")
        
        with st.expander("Clique para ver as matrículas detalhadas"):
            st.markdown(f"""
            - 📊 **Matrículas Ensino Fundamental:** {escola["MATRICULAS FUND"] if pd.notna(escola["MATRICULAS FUND"]) else "N/A"}
            - 📊 **Matrículas Ensino Médio:** {escola["MATRICULAS MED"] if pd.notna(escola["MATRICULAS MED"]) else "N/A"}
            - 👩‍🏫 **Matrículas Profissionais:** {escola["MATRICULAS PROF"] if pd.notna(escola["MATRICULAS PROF"]) else "N/A"}
            - 🧑‍🎓 **Matrículas EJA:** {escola["MATRICULAS EJA"] if pd.notna(escola["MATRICULAS EJA"]) else "N/A"}
            """)

        st.markdown(f"🏫 **Acessibilidade Geral:** {escola['ACESSIBILIDADE'] if pd.notna(escola['ACESSIBILIDADE']) else 'N/A'}")

        with st.expander("Clique para ver detalhes de acessibilidade"):
            st.markdown(f"""
            - 🚪 **Corrimão:** {escola["ACESS_CORRIMAO"] if pd.notna(escola["ACESS_CORRIMAO"]) else "N/A"}
            - 🛗 **Elevador:** {escola["ACESS_ELEVADOR"] if pd.notna(escola["ACESS_ELEVADOR"]) else "N/A"}
            - 🏢 **Pisos Táteis:** {escola["ACESS_PISOS"] if pd.notna(escola["ACESS_PISOS"]) else "N/A"}
            - 🚶‍♂️ **Vão Livre:** {escola["ACESS_VAO"] if pd.notna(escola["ACESS_VAO"]) else "N/A"}
            - ♿ **Rampas:** {escola["ACESS_RAMPAS"] if pd.notna(escola["ACESS_RAMPAS"]) else "N/A"}
            - 🔊 **Sinal Sonoro:** {escola["ACESS_SINAL_SONORO"] if pd.notna(escola["ACESS_SINAL_SONORO"]) else "N/A"}
            - 📝 **Sinal Tátil:** {escola["ACESS_SINAL_TATIL"] if pd.notna(escola["ACESS_SINAL_TATIL"]) else "N/A"}
            - 🖼️ **Sinal Visual:** {escola["ACESS_SINAL_VISUAL"] if pd.notna(escola["ACESS_SINAL_VISUAL"]) else "N/A"}
            - 📑 **Sinalização:** {escola["ACESS_SINALIZAÇÃO"] if pd.notna(escola["ACESS_SINALIZAÇÃO"]) else "N/A"}
            """)

        st.markdown(f"🏢 **Salas Totais:** {escola['SALAS'] if pd.notna(escola['SALAS']) else 'N/A'}")

        with st.expander("Clique para ver detalhes das salas"):
            st.markdown(f"""
            - ❄️ **Salas Climatizadas:** {escola["SALAS_CLIMATIZADAS"] if pd.notna(escola["SALAS_CLIMATIZADAS"]) else "N/A"}
            - ♿ **Salas Acessíveis:** {escola["SALAS_ACESSIVEIS"] if pd.notna(escola["SALAS_ACESSIVEIS"]) else "N/A"}
            """)

        st.markdown(f"**🛠️ Infraestutura**")

        with st.expander("Clique para ver detalhes da infraestrutura"):
            st.markdown(f"""
            - 🏀 **Quadra:** {escola["QUADRA"] if pd.notna(escola["QUADRA"]) else "N/A"}
            - 🏊‍♂️ **Piscina:** {escola["PISCINA"] if pd.notna(escola["PISCINA"]) else "N/A"}
            """)

        # --- EXIBIÇÃO DO MAPA ---
        st.markdown("---")
        st.subheader("📍 Localização no Mapa")

        try:
            lat = float(escola.get("LATITUDE_C"))
            lon = float(escola.get("LONGITUDE_C"))
            if pd.isna(lat) or pd.isna(lon):
                raise ValueError("Coordenada nula")

            m = folium.Map(
                location=[lat, lon],
                zoom_start=17,
                tiles="Esri.WorldImagery"
            )

            # Marcador com o nome da escola
            folium.Marker(
                location=[lat, lon],
                tooltip=escola["NO_ENTIDADE"],
                popup=escola["NO_ENTIDADE"],
                icon=folium.Icon(color="red", icon="graduation-cap", prefix="fa")
            ).add_to(m)

            st_folium(m, use_container_width=True, height=450)

            # Link para abrir no Google Maps
            st.markdown(f"[🗺️ Abrir no Google Maps](https://www.google.com/maps?q={lat},{lon})", unsafe_allow_html=True)

        except (ValueError, TypeError):
            st.info("ℹ️ As coordenadas geográficas desta unidade não estão cadastradas ou estão em formato inválido na planilha.")
