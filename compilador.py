import os
import json

PASTA_ENTRADA = "resultados_CNSA_detalhes"
ARQUIVO_SAIDA = "resultado_final.json"

def juntar_arquivos_json():
    resultado_final = []  

    for arquivo in os.listdir(PASTA_ENTRADA):
        if arquivo.endswith(".json"):
            caminho_arquivo = os.path.join(PASTA_ENTRADA, arquivo)
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                nome_arquivo = os.path.splitext(arquivo)[0]
                dados["nome"] = nome_arquivo 
                
                resultado_final.append(dados)
            except Exception as e:
                print(f"Erro ao processar o arquivo {arquivo}: {e}")
    
    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f_out:
        json.dump(resultado_final, f_out, ensure_ascii=False, indent=4)
    
    print(f"Arquivo combinado salvo em: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    juntar_arquivos_json()
