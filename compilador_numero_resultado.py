import os
import json

PASTA_ENTRADA = "resultados_CNSA_detalhes"
ARQUIVO_SAIDA_INTERMEDIARIO = "resultado_sociedade_CNSA.json"
ARQUIVO_TELEFONES = "numero_telefone_1.json"
ARQUIVO_SAIDA_FINAL = "resultado_combinado.json"

def load_json(filename):
    """Carrega um arquivo JSON."""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(filename, data):
    """Salva dados em um arquivo JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def juntar_arquivos_json():
    """Combina todos os arquivos JSON da pasta em um único arquivo."""
    resultado_final = []
    if not os.path.exists(PASTA_ENTRADA):
        print(f"Pasta {PASTA_ENTRADA} não encontrada.")
        return []
    for arquivo in os.listdir(PASTA_ENTRADA):
        if arquivo.endswith('.json'):
            caminho_arquivo = os.path.join(PASTA_ENTRADA, arquivo)
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    conteudo = json.load(f)
                    conteudo["nome"] = arquivo
                    resultado_final.append(conteudo)
            except json.JSONDecodeError:
                print(f"Erro ao ler o JSON do arquivo: {arquivo}")
            except Exception as e:
                print(f"Erro inesperado ao processar '{arquivo}': {e}")

    save_json(ARQUIVO_SAIDA_INTERMEDIARIO, resultado_final)
    print(f"Todos os arquivos foram combinados e salvos em '{ARQUIVO_SAIDA_INTERMEDIARIO}'.")
    return resultado_final

def combinar_dados_telefone(data_file, phone_file):
    """Combina os dados de telefone ao JSON intermediário."""
    data = load_json(data_file)
    phones = load_json(phone_file)

    if isinstance(data, list):
        combined_data = []
        for entry in data:
            nome_escritorio = entry.get("nome", "").split("_data")[0]
            telefone_info = phones.get(f"{nome_escritorio}_data_18-12-2024.png", [])

            entry['telefones'] = [phone['resultado'] for phone in telefone_info if phone['resultado']]
            combined_data.append(entry)
    else:
        nome_escritorio = data.get("nome", "").split("_data")[0]
        telefone_info = phones.get(f"{nome_escritorio}_data_18-12-2024.png", [])

        data['telefones'] = [phone['resultado'] for phone in telefone_info if phone['resultado']]
        combined_data = data

    save_json(ARQUIVO_SAIDA_FINAL, combined_data)
    print(f"Dados combinados salvos em '{ARQUIVO_SAIDA_FINAL}'.")

def main():
    """Executa o fluxo completo."""
    if not os.path.exists(PASTA_ENTRADA):
        print(f"A pasta de entrada '{PASTA_ENTRADA}' não foi encontrada. Encerrando.")
        return

    juntar_arquivos_json()

    if not os.path.exists(ARQUIVO_SAIDA_INTERMEDIARIO) or not os.path.exists(ARQUIVO_TELEFONES):
        print("Um ou ambos os arquivos necessários para a combinação final não existem.")
        return

    combinar_dados_telefone(ARQUIVO_SAIDA_INTERMEDIARIO, ARQUIVO_TELEFONES)

if __name__ == "__main__":
    main()
