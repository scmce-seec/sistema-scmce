# Arquivo: utils.py
import streamlit as st
from streamlit_gsheets import GSheetsConnection

PASSWORD = st.secrets["pass"]

@st.cache_data(ttl=600)
def carregar_df(planilha, aba):
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Ajuste o worksheet conforme necessário se mudar
    data = conn.read(spreadsheet=planilha, worksheet=aba)
    return data


# --- NOVA FUNÇÃO DE LOGIN ---
def fazer_login():
    """
    Gerencia a autenticação do usuário.
    Retorna True se logado, False se não logado.
    """
    # 1. Verifica se já está logado na sessão
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if st.session_state.autenticado:
        return True

    # 2. Se não estiver logado, busca a senha no .env    
    if not PASSWORD:
        st.error("Erro de configuração: Senha não encontrada no .env")
        return False

    # 3. Mostra o formulário de login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 Acesso Restrito")
        st.write("Sistema SCMCE")
        
        senha_digitada = st.text_input("Digite sua senha", type="password")

        if st.button("Entrar"):
            if senha_digitada == PASSWORD:
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
    
    return False


def my_metric(label, value, bg_color, icon=""):
    fontsize = 20
    lnk = '<link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.12.1/css/all.css" crossorigin="anonymous">'

    bg_color_css = f'rgb({bg_color[0]}, {bg_color[1]}, {bg_color[2]}, 0.75)'

    htmlstr = f"""<p style='background-color: {bg_color_css}; 
                            font-size: {fontsize}px; 
                            border-radius: 7px; 
                            padding-left: 12px; 
                            padding-top: 18px; 
                            padding-bottom: 18px; 
                            line-height:25px;'>
                            <i class='{icon} fa-xs'></i> {value}
                            <BR>
                            <span style='font-size: 18px; margin-top: 0;'>
                                {label}
                            </span>
                  </p>"""

    st.markdown(lnk + htmlstr, unsafe_allow_html=True)

