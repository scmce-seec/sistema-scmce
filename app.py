import streamlit as st
from utils import fazer_login

st.set_page_config(page_title="Sistema SCMCE 📝", layout="wide")


if not fazer_login():
    st.stop()

pages = {
    "Home": [
        st.Page("home.py", title="Página Inicial", icon=":material/home:"),
    ],
    "Ferramentas": [
        st.Page("censo.py", title="Censo", icon=":material/monitoring:"),
        st.Page("bd.py", title="Banco de Dados - Obras", icon=":material/database_search:"),
        st.Page("bd-medicoes.py", title="Banco de Dados - Medições", icon=":material/money:"),
        st.Page("bd-empenhos.py", title="Banco de Dados - Empenhos", icon=":material/paid:"),
        st.Page("soli_acessibilidade.py", title="Solicitações de Acessibilidade", icon=":material/balance:"),
        st.Page("proj_eletrico.py", title="Projetos Elétricos", icon=":material/electric_bolt:"),
        st.Page("bd-pague.py", title="Pague Predial", icon=":material/build:")
    ],
}


pg = st.navigation(pages, position="top")
pg.run()