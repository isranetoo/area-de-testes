import os
import json
from datetime import datetime

PASTA_OAB = 'output_CNA_OAB'
PASTA_SAIDA = 'detalhes_CNA_separados'
os.makedirs(PASTA_SAIDA, exist_ok=True)

def salvar_em_arquivo(pasta, nome_arquivo, conteudo):
    """Salva o conteúdo em um arquivo JSON na pasta especificada."""
    caminho = os.path.join(pasta, nome_arquivo)
    try:
        with open(caminho, 'w', encoding='utf-8') as arquivo:
            json.dump(conteudo, arquivo, ensure_ascii=False, indent=4)
        print(f"Arquivo salvo em: {caminho}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")

def processar_arquivo_json():
    """Processa os arquivos JSON na pasta 'output_CNA_OAB' e separa os itens conforme necessário."""
    try:
        arquivos = [f for f in os.listdir(PASTA_OAB) if f.endswith('.json')]
        if not arquivos:
            print(f"Nenhum arquivo JSON encontrado na pasta {PASTA_OAB}")
            return
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(PASTA_OAB, arquivo)
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
            
            for item in dados.get('Data', []):
                nome = item.get('Nome')
                if nome:
                    timestamp = datetime.now().strftime("%d-%m-%Y")
                    nome_arquivo = f"{nome.replace(' ', '_')}_data_{timestamp}.json"
                    
                    salvar_em_arquivo(PASTA_SAIDA, nome_arquivo, item)
    
    except Exception as e:
        print(f"Erro ao processar os arquivos JSON: {e}")

def main():
    """Função principal para processar os arquivos."""
    processar_arquivo_json()

if __name__ == "__main__":
    main()
