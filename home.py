import streamlit as st
import pandas as pd
# Removidas as importações do dashboard que não serão usadas
# from utils import connect_gsheets, get_worksheet 
# import re

# --- Configuração da Página ---
# st.set_page_config(page_title="Página Inicial", layout="wide") # O app.py já faz isso

# --- Conteúdo da Página ---
st.title("🏠 Página Inicial")
#st.write(f"### Olá, **{st.session_state.user_nome}**!")
st.write(f"### Olá, Seja Bem-Vindo(a)!")

st.divider()

st.header("O que você encontra neste sistema?")
st.write("""
O **Sistema SCMCE** foi desenvolvido para centralizar, agilizar e dar transparência aos processos de
Controle e Manutenção de Contratos. Aqui, você pode acessar de forma rápida e intuitiva
diversas ferramentas essenciais para a gestão do dia-a-dia.
""")

st.subheader("Ferramentas Disponíveis:")

st.markdown("""
- 📄 **Censo:** Acesso aos dados do censo.
- 🗃️ **Bancos de Dados:** Consultas rápidas aos principais bancos de dados.
- ♿ **Solicitações de Acessibilidade:** Acompanhamento e gestão das demandas relacionadas à acessibilidade.
- 💡 **Projetos Elétricos:** Consulta, acompanhamento de status e informações dos projetos elétricos em execução.
- 🏫 **Pague Predial:** Consulta e acompanhamento dos pedidos de manutenção escolar.
""")

st.caption("Utilize o menu de navegação na parte superior para acessar a ferramenta desejada.")

st.info("""
Este sistema é atualizado com base no dia a dia da equipe.  
Dúvidas, erros ou sugestões? Fale com a gente!
""")