import os
import json

pasta_resultados = 'resultados_detalhes'
pasta_saida = 'resultados_processados'

os.makedirs(pasta_saida, exist_ok=True)

base_url = "https://cna.oab.org.br/"

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
        url_completa = base_url + detail_url
    else:
        url_completa = None

    novo_json = {
        "Insc": insc,
        "DetailUrl": detail_url,
        "URL": url_completa
    }

    return novo_json

def salvar_novo_arquivo(nome_arquivo, dados):
    caminho_novo_arquivo = os.path.join(pasta_saida, nome_arquivo)
    with open(caminho_novo_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

for nome_arquivo in os.listdir(pasta_resultados):
    if nome_arquivo.endswith('.json'):
        caminho_arquivo = os.path.join(pasta_resultados, nome_arquivo)
        
        novo_dados = processar_arquivo_json(caminho_arquivo)
        
        salvar_novo_arquivo(nome_arquivo, novo_dados)

print("Processamento concluído!")
