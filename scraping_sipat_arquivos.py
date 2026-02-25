import requests
import pandas as pd
import time

# --- CONFIGURAÇÕES ---
nome_arquivo_imoveis = "imoveis_seec_completo.csv"
nome_arquivo_saida = "arquivos_imoveis_seec.csv"

url_api_arquivos = "https://sgpapi.hml.sistemas.cotic.rn.gov.br/ObterArquivo"
url_base_download = "http://sistemas.searh.rn.gov.br/SGP/Arquivos/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}

# --- 1. LENDO OS IMÓVEIS ---
try:
    df_imoveis = pd.read_csv(nome_arquivo_imoveis, sep=';')
except FileNotFoundError:
    print(f"Erro: O arquivo '{nome_arquivo_imoveis}' não foi encontrado na pasta.")
    exit()

# Descobre automaticamente o nome da coluna de ID no seu CSV (pode vir como 'id', 'Id', 'ID', etc.)
coluna_id = next((col for col in df_imoveis.columns if col.lower() == 'id'), None)

if not coluna_id:
    print("Erro: Não encontrei uma coluna de ID no seu CSV de imóveis.")
    exit()

# Pega apenas os IDs únicos removendo valores nulos (caso existam)
ids_imoveis = df_imoveis[coluna_id].dropna().unique()
print(f"Iniciando a busca de arquivos para {len(ids_imoveis)} imóveis...")

# --- 2. BUSCANDO OS ARQUIVOS NA API ---
lista_arquivos_final = []

for imovel_id in ids_imoveis:
    # Como o ID pode vir como float (ex: 91.0), forçamos para inteiro e depois string
    imovel_id_str = str(int(imovel_id)) 
    print(f"Buscando arquivos do Imóvel ID: {imovel_id_str}...")
    
    try:
        # Faz um GET simples passando o ID na URL
        response = requests.get(f"{url_api_arquivos}?id={imovel_id_str}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            arquivos = response.json()
            
            # Se a API retornar uma lista de arquivos, processamos um por um
            if arquivos and isinstance(arquivos, list):
                for arq in arquivos:
                    # Monta o dicionário selecionando só o que você pediu e criando a URL
                    dados_arquivo = {
                        "id_arquivo": arq.get("id"),
                        "imovelId": arq.get("imovelId"),
                        "url_download": f"{url_base_download}{arq.get('nomeArquivo')}",
                        "dataCadastro": arq.get("dataCadastro"),
                        "categoria": arq.get("categoria"),
                        "nomeOriginal": arq.get("nomeOriginal"),
                        "usuarioCadastro": arq.get("usuarioCadastro")
                    }
                    lista_arquivos_final.append(dados_arquivo)
        else:
             print(f"  Aviso: Retorno {response.status_code} no imóvel {imovel_id_str}")
             
    except requests.exceptions.RequestException as e:
        print(f"  Falha de conexão ao buscar o imóvel {imovel_id_str}. Erro: {e}")
        
    # Pausa de meio segundo para não sobrecarregar a API
    time.sleep(0.5)

# --- 3. SALVANDO O RESULTADO ---
if lista_arquivos_final:
    df_arquivos = pd.DataFrame(lista_arquivos_final)
    df_arquivos.to_csv(nome_arquivo_saida, index=False, encoding='utf-8-sig', sep=';')
    print(f"\nPronto! {len(lista_arquivos_final)} links de arquivos foram salvos em '{nome_arquivo_saida}'")
else:
    print("\nNenhum arquivo foi encontrado para os imóveis pesquisados.")