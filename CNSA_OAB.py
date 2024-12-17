import os
import json
import requests

PASTA_ENTRADA = "resultados_CNA_detalhes"
PASTA_SAIDA = "resultados_CNSA_detalhes"
PASTA_SAIDA_FINAL = "resultados_Preview"  # Nova pasta para salvar as informações de Preview

if not os.path.exists(PASTA_SAIDA_FINAL):
    os.makedirs(PASTA_SAIDA_FINAL)

def processar_arquivos():
    """Processa arquivos, faz o POST para URLs extraídas e salva os dados de Preview."""
    
    for arquivo in os.listdir(PASTA_SAIDA):
        if arquivo.endswith(".json"):
            caminho_arquivo = os.path.join(PASTA_SAIDA, arquivo)
            
            # Abre o arquivo e lê os dados
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)

            # A URL foi extraída anteriormente e salva no campo "url"
            url_completa = dados.get("url", None)

            if url_completa:
                print(f"Fazendo POST na URL: {url_completa}")
                
                try:
                    # Faz o POST para a URL extraída
                    response = requests.post(url_completa)

                    if response.status_code == 200:
                        try:
                            # Extrai os dados JSON da resposta
                            resposta_json = response.json()

                            # Coleta as informações do campo Preview
                            preview = resposta_json.get("Preview", None)

                            if preview:  # Se o campo Preview estiver presente
                                # Cria o caminho para salvar o novo arquivo de saída
                                caminho_saida = os.path.join(PASTA_SAIDA_FINAL, f"preview_{arquivo}")

                                # Salva os dados de Preview em um novo arquivo
                                with open(caminho_saida, 'w', encoding='utf-8') as f_out:
                                    json.dump(preview, f_out, ensure_ascii=False, indent=4)

                                print(f"Informações de Preview salvas em: {caminho_saida}")
                            else:
                                print(f"Preview não encontrado na resposta de: {url_completa}")
                        except json.JSONDecodeError:
                            print(f"Resposta inválida (não JSON) para: {url_completa}")
                    else:
                        print(f"Erro HTTP {response.status_code} ao acessar: {url_completa}")

                except requests.exceptions.RequestException as e:
                    print(f"Erro durante a requisição POST: {e}")
            else:
                print(f"URL não encontrada no arquivo: {arquivo}")

if __name__ == "__main__":
    processar_arquivos()
