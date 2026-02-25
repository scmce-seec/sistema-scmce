import requests
import pandas as pd
import time

# 1. Configurações da Requisição
url = "https://sgpapi.hml.sistemas.cotic.rn.gov.br/ObterImoveis"

headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://www.sipat.rn.gov.br",
    "Referer": "https://www.sipat.rn.gov.br/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

todos_imoveis = []
pagina_atual = 1

print("Iniciando a extração dos dados da SEEC...")

# 2. Laço de repetição para varrer todas as páginas
while True:
    print(f"Buscando página {pagina_atual}...")
    
    # O payload (corpo da requisição) igual ao que você achou no curl, variando apenas a página
    payload = {
        "DominioId": 31,
        "SituacaoId": 0,
        "NumeroRegistro": "",
        "Cidade": "",
        "Logradouro": "",
        "Bairro": "",
        "Numero": "",
        "pagina": pagina_atual
    }
    
    # Fazendo a requisição POST
    response = requests.post(url, json=payload, headers=headers)
    
    # Verifica se a requisição deu erro (ex: 404, 500)
    if response.status_code != 200:
        print(f"Erro ao acessar a página {pagina_atual}. Status Code: {response.status_code}")
        break
        
    dados_json = response.json()
    
    # 3. Lógica para extrair a lista de imóveis do JSON
    registros = []
    
    # APIs costumam retornar a lista direto ou dentro de um dicionário (ex: {"itens": [...]})
    if isinstance(dados_json, list):
        registros = dados_json
    elif isinstance(dados_json, dict):
        # Procura dinamicamente pela chave que contém a lista de dados
        registros = next((v for v in dados_json.values() if isinstance(v, list)), [])
        
    # Se a lista vier vazia, significa que as páginas acabaram
    if not registros:
        print(f"Página {pagina_atual} vazia. Extração concluída!")
        break
        
    # Adiciona os registros desta página na nossa lista mestre
    todos_imoveis.extend(registros)
    
    pagina_atual += 1
    
    # Pausa de 1 segundo entre os pedidos para não derrubar/sobrecarregar o servidor do Estado
    time.sleep(1)

# 4. Transformação e Salvamento
if todos_imoveis:
    print(f"\nTotal de imóveis extraídos: {len(todos_imoveis)}")
    
    # Converte a lista de dicionários para um DataFrame do Pandas
    df = pd.DataFrame(todos_imoveis)
    
    # Salva em CSV
    nome_arquivo = "imoveis_seec_completo.csv"
    df.to_csv(nome_arquivo, index=False, encoding='utf-8-sig', sep=';')
    print(f"Arquivo salvo com sucesso: {nome_arquivo}")
else:
    print("Nenhum dado foi retornado pela API.")