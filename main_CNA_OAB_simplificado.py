import os
import json
import requests
from datetime import datetime
import subprocess

BASE_URL = 'https://cna.oab.org.br/'
PASTAS = {
    'OAB': 'output_CNA_OAB',
    'Detalhes': 'resultados_CNA_detalhes',
    'Saida': 'detalhes_CNA_processados',
    'SaidaImg': 'imgs_CNA_OAB'
}

for pasta in PASTAS.values():
    os.makedirs(pasta, exist_ok=True)

def salvar_em_arquivo(pasta, nome_arquivo, conteudo):
    """Salva conteúdo em arquivo JSON."""
    try:
        with open(os.path.join(pasta, nome_arquivo), 'w', encoding='utf-8') as arquivo:
            json.dump(conteudo, arquivo, ensure_ascii=False, indent=4)
        print(f"Arquivo salvo em: {pasta}/{nome_arquivo}")
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")

def baixar_imagem(url, nome_arquivo):
    """Baixa imagem da URL e salva localmente."""
    try:
        resposta = requests.get(url, stream=True)
        if resposta.status_code == 200:
            with open(os.path.join(PASTAS['SaidaImg'], f"{nome_arquivo}.png"), 'wb') as arquivo:
                for chunk in resposta.iter_content(1024):
                    arquivo.write(chunk)
            print(f"Imagem salva: {nome_arquivo}")
        else:
            print(f"Erro ao baixar imagem: {resposta.status_code}")
    except Exception as e:
        print(f"Erro ao salvar imagem: {e}")

class SessaoCNA:
    """Classe para interagir com o sistema CNA."""
    def __init__(self, nome_advo):
        self.sessao = requests.Session()
        self.nome_advo = nome_advo

    def enviar_requisicao(self):
        """Realiza a requisição e salva os dados do advogado."""
        payload = {"NomeAdvo": self.nome_advo, "IsMobile": "false"}
        try:
            resposta = self.sessao.post(BASE_URL + 'Home/Search', json=payload, headers={'Content-Type': 'application/json'})
            if resposta.status_code == 200:
                dados = resposta.json()
                if dados:
                    timestamp = datetime.now().strftime("%d-%m-%Y")
                    salvar_em_arquivo(PASTAS['OAB'], f"Advogado_{self.nome_advo.replace(' ', '_')}_data_{timestamp}.json", dados)
                    print(f"Dados do advogado {self.nome_advo} obtidos com sucesso.")
                else:
                    print(f"Nenhum dado encontrado para {self.nome_advo}")
            else:
                print(f"Erro na requisição: {resposta.status_code}")
        except Exception as e:
            print(f"Erro ao realizar requisição: {e}")

class DetalhesCNA:
    """Classe para buscar e salvar detalhes adicionais."""
    def __init__(self):
        self.sessao = requests.Session()

    def processar_arquivos(self):
        """Processa arquivos e coleta detalhes adicionais."""
        arquivos = [f for f in os.listdir(PASTAS['OAB']) if f.endswith('.json')]
        if arquivos:
            for arquivo in arquivos:
                with open(os.path.join(PASTAS['OAB'], arquivo), 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                for item in dados.get('Data', []):
                    if 'DetailUrl' in item:
                        self.buscar_detalhes(BASE_URL + item['DetailUrl'], item.get('Nome', 'desconhecido'))
        else:
            print(f"Nenhum arquivo encontrado em {PASTAS['OAB']}")

    def buscar_detalhes(self, url, nome_advogado):
        """Busca e salva detalhes adicionais do advogado."""
        try:
            resposta = self.sessao.post(url, headers={'Content-Type': 'application/json'})
            if resposta.status_code == 200:
                detalhes = resposta.json()
                timestamp = datetime.now().strftime("%d-%m-%Y")
                salvar_em_arquivo(PASTAS['Detalhes'], f"{nome_advogado}_data_{timestamp}.json", detalhes)
                print(f"Detalhes salvos: {url}")
            else:
                print(f"Erro ao acessar detalhes: {resposta.status_code}")
        except Exception as e:
            print(f"Erro ao buscar detalhes: {e}")

def processar_arquivo_json(caminho_arquivo):
    """Processa arquivo JSON e extrai informações relevantes."""
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    sociedades = dados.get("Data", {}).get("Sociedades", [])
    sociedade = sociedades[0] if sociedades else {}
    
    detail_url = dados.get("Data", {}).get("DetailUrl")
    insc = sociedade.get("Inscricao")
    url_completa = BASE_URL + detail_url if detail_url else None
    
    if url_completa:
        nome_imagem = os.path.splitext(os.path.basename(caminho_arquivo))[0]
        baixar_imagem(url_completa, nome_imagem)
    
    return {"Inscricao": insc, "DetailUrl": detail_url, "URL": url_completa}


def atualizar_arquivo_json():
    """Atualiza arquivos JSON com os dados processados."""
    arquivos = [f for f in os.listdir(PASTAS['Saida']) if f.endswith('.json')]
    if arquivos:
        for arquivo in arquivos:
            caminho_arquivo_processado = os.path.join(PASTAS['Saida'], arquivo)
            caminho_arquivo_resultado = os.path.join(PASTAS['Detalhes'], arquivo)
            if os.path.exists(caminho_arquivo_resultado):
                with open(caminho_arquivo_processado, 'r', encoding='utf-8') as arq_processado, open(caminho_arquivo_resultado, 'r', encoding='utf-8') as arq_resultado:
                    dados_processados = json.load(arq_processado)
                    dados_resultado = json.load(arq_resultado)
                if dados_processados.get("URL"):
                    dados_resultado["Data"]["URL"] = dados_processados["URL"]
                if dados_processados.get("Inscricao"):
                    dados_resultado["Data"]["Inscricao"] = dados_processados["Inscricao"]
                salvar_em_arquivo(PASTAS['Detalhes'], arquivo, dados_resultado)
                print(f"Arquivo {arquivo} atualizado com sucesso.")
    else:
        print(f"Nenhum arquivo encontrado na pasta {PASTAS['Saida']}")

def executar_script(script_nome):
    """Executa um script Python."""
    try:
        subprocess.run(['python', script_nome], check=True)
        print(f"Script '{script_nome}' executado com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar {script_nome}: {e}")
    except FileNotFoundError:
        print(f"O script '{script_nome}' não foi encontrado.")

def main():
    caminho_lista_nomes = "lista_nomes.txt"  # Nome do arquivo com a lista de nomes
    if not os.path.exists(caminho_lista_nomes):
        print(f"Arquivo {caminho_lista_nomes} não encontrado!")
        return

    with open(caminho_lista_nomes, 'r', encoding='utf-8') as arquivo:
        nomes = [linha.strip() for linha in arquivo.readlines() if linha.strip()]

    if not nomes:
        print("Nenhum nome encontrado na lista.")
        return

    for nome in nomes:
        print(f"Processando nome: {nome}")
        sessao_cna = SessaoCNA(nome)
        sessao_cna.enviar_requisicao()

    detalhes_cna = DetalhesCNA()
    detalhes_cna.processar_arquivos()
    for nome_arquivo in os.listdir(PASTAS['Detalhes']):
        if nome_arquivo.endswith(".json"):
            novo_dado = processar_arquivo_json(os.path.join(PASTAS['Detalhes'], nome_arquivo))
            salvar_em_arquivo(PASTAS['Saida'], nome_arquivo, novo_dado)
            print(f"Processamento de {nome_arquivo} concluído.")
    atualizar_arquivo_json()
    executar_script('corte_img.py')
    executar_script('separador.py')

if __name__ == "__main__":
    main()
