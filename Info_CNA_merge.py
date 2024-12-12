import os
import json

BASE_URL = 'https://cna.oab.org.br/'
PASTA_RESULTADOS = 'resultados_CNA_detalhes'
PASTA_SAIDA = 'detalhes_CNA_processados'

os.makedirs(PASTA_SAIDA, exist_ok=True)

def processar_arquivo_json(caminho_arquivo):
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
        insc = None
        detail_url = None
        
        if dados.get("Data") and dados["Data"].get("Sociedades"):
            sociedade = dados["Data"]["Sociedades"][0]
            insc = sociedade.get("Insc")

        if dados.get("Data") and dados["Data"].get("DetailUrl"):
            detail_url = dados["Data"]["DetailUrl"]

        if detail_url:
            url_completa = BASE_URL + detail_url
        else:
            url_completa = None
        
        novo_json = {
            "Inscricao": insc,
            "DetailUrl": detail_url,
            "URL": url_completa
        }
        return novo_json
    
def salvar_novo_arquivo(nome_arquivo, dados):
    caminho_novo_arquivo = os.path.join(PASTA_SAIDA, nome_arquivo)
    with open(caminho_novo_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    
for nome_arquivo in os.listdir(PASTA_RESULTADOS):
    if nome_arquivo.endswith('.json'):
        caminho_arquivo = os.path.join(PASTA_RESULTADOS, nome_arquivo)
        novo_dado = processar_arquivo_json(caminho_arquivo)
        salvar_novo_arquivo(nome_arquivo, novo_dado)
    print(f"Processamento de {nome_arquivo} concluído")