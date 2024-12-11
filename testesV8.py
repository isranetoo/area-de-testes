import json
import os
import requests
from datetime import datetime
from captcha_local_solver import solve_captcha_local

URL_CAPTCHA = 'https://pje.trt2.jus.br/juris-backend/api/captcha'
URL_DOCUMENTOS = 'https://pje.trt2.jus.br/juris-backend/api/documentos'
PASTA_DOCUMENTOS = "documentos"
ARQUIVO_UNIFICADO = "processos_unificados.json"
ARQUIVO_INFORMACOES = "informacoes_processos.json"

class SessaoJurisprudencia:
    def __init__(self, assunto: str, procs_por_pagina: int, max_paginas: int = 10):
        """ Classe para pesquisa de jurisprudência no TRT 2. """
        self.assunto = assunto
        self.procs_por_pagina = int(procs_por_pagina)
        self.max_paginas = max_paginas
        self.sessao = requests.Session()
        self.token_desafio = None
        self.resposta_captcha = None
        self.url_post = None
        self.cookies = {}

    def fazer_requisicao_captcha(self):
        try:
            resposta = self.sessao.get(URL_CAPTCHA, headers={'Accept': 'application/json'})
            resposta.raise_for_status()
            dados = resposta.json()
            self.token_desafio = dados.get('tokenDesafio')
            self.resolver_captcha(dados.get('imagem'))
        except Exception as e:
            print(f"Erro ao obter o CAPTCHA: {e}")

    def resolver_captcha(self, base64_string):
        try:
            if base64_string:
                base64_string = base64_string.split(',')[1] if base64_string.startswith('data:image') else base64_string
                self.resposta_captcha = solve_captcha_local(base64_string)
                print(f"Resposta do CAPTCHA: \033[1;32m{self.resposta_captcha}\033[0m")
                self.url_post = f"{URL_DOCUMENTOS}?tokenDesafio={self.token_desafio}&resposta={self.resposta_captcha}"
                self.configurar_cookies()
        except Exception as e:
            print(f"Erro ao resolver o CAPTCHA: {e}")

    def configurar_cookies(self):
        self.cookies = {
            "_ga": "GA1.3.2135935613.1731417901",
            "respostaDesafio": self.resposta_captcha,
            "tokenDesafio": self.token_desafio,
        }
        self.sessao.cookies.update(self.cookies)
        self.salvar_em_arquivo("cookies", "cookies.json", self.cookies)

    def salvar_em_arquivo(self, pasta, nome_arquivo, conteudo):
        os.makedirs(pasta, exist_ok=True)
        caminho = os.path.join(pasta, nome_arquivo)
        try:
            with open(caminho, 'w', encoding='utf-8') as arquivo:
                json.dump(conteudo, arquivo, ensure_ascii=False, indent=4)
            print(f"Arquivo salvo em: {caminho}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")

    def enviar_documento(self, pagina):
        payload = {
            "resposta": self.resposta_captcha,
            "tokenDesafio": self.token_desafio,
            "name": "query parameters",
            "andField": [self.assunto],
            "paginationPosition": pagina,
            "paginationSize": self.procs_por_pagina,
            "fragmentSize": 512,
            "ordenarPor": "dataPublicacao",
        }
        try:
            resposta = self.sessao.post(self.url_post, json=payload, headers={'Content-Type': 'application/json'})
            timestamp = datetime.now().strftime("%d-%m-%Y")
            if resposta.status_code == 200:
                documentos = resposta.json()
                if documentos.get("mensagem") == "A resposta informada é incorreta":
                    print("\033[1;31mCAPTCHA incorreto.\033[0m Gerando novo...")
                    self.url_post = None
                else:
                    nome_arquivo = f"assunto_{self.assunto}_pagina_{pagina}_data_{timestamp}.json"
                    self.salvar_em_arquivo(PASTA_DOCUMENTOS, nome_arquivo, documentos)
                    return True
        except Exception as e:
            print(f"Erro ao processar a página {pagina}: {e}")
        return False

    def iniciar_sessao(self):
        print("\033[1;33m==== Iniciando a Sessão ====\033[0m")
        pagina, retries, max_retries = 1, 1, 5
        while pagina <= self.max_paginas:
            if not self.url_post:
                if retries > max_retries:
                    raise Exception("Falha em resolver o CAPTCHA repetidamente. Finalizando...")
                self.fazer_requisicao_captcha()

            if self.url_post and self.enviar_documento(pagina):
                print(f"Página {pagina} processada com sucesso!")
                pagina += 1
                retries = 1
            else:
                retries += 1

def coletar_documentos(pasta_origem, arquivo_saida):
    documentos_unificados = {"documents": []}
    arquivos_json = [f for f in os.listdir(pasta_origem) if f.endswith('.json')]
    for arquivo in arquivos_json:
        try:
            with open(os.path.join(pasta_origem, arquivo), 'r', encoding='utf-8') as f:
                conteudo = json.load(f)
                documentos_unificados["documents"].extend(conteudo.get("documents", []))
        except Exception as e:
            print(f"Erro ao processar o arquivo {arquivo}: {e}")

    with open(arquivo_saida, 'w', encoding='utf-8') as f:
        json.dump(documentos_unificados, f, ensure_ascii=False, indent=4)
    print(f"Documentos unificados salvos em: {arquivo_saida}")

def coletar_informacoes(arquivo_entrada, arquivo_saida):
    """
    Coleta as informações do processos_unificados.json e as filtra em outro arquivo informacoes_processos_completo.json
    com o formato fornecido e valores nulos para campos ausentes.
    """
    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as f:
            dados = json.load(f).get("documents", [])

        informacoes = {}
        for doc in dados:
            numero_processo = doc.get("processo", "desconhecido")
            informacoes[numero_processo] = {
                "sistema": doc.get("sistema", None),
                "numero": doc.get("processo", None),
                "classe": doc.get("classeJudicial", None),
                "current_instance": doc.get("instancia", None),
                "orgaoJulgador": doc.get("orgaoJulgador", None),
                "juizoDigital": doc.get("juizoDigital", None),
                "segredoJustica": doc.get("sigiloso", None),
                "justicaGratuita": doc.get("justicaGratuita", None),
                "distribuidoEm": doc.get("dataDistribuicao", None),
                "autuadoEm": doc.get("dataPublicacao", None),
                "valorDaCausa": doc.get("valorCausa", None),
                "envolvidos": doc.get("envolvidos", []),
                "assuntos": doc.get("assuntos", []),
                "movimentacoes": doc.get("movimentacoes", [])
            }
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump(informacoes, f, ensure_ascii=False, indent=4)
        print(f"Informações salvas em: \033[32m{arquivo_saida}\033[0m")

    except Exception as e:
        print(f"Erro ao processar informações: {e}")




if __name__ == "__main__":
    procs_por_pagina = input("Digite o número de processos por página: ")
    assunto = input("Digite o assunto de interesse: ")
    sessao = SessaoJurisprudencia(assunto, procs_por_pagina)
    sessao.iniciar_sessao()

    coletar_documentos(PASTA_DOCUMENTOS, ARQUIVO_UNIFICADO)
    campos = ["sigiloso", "anoProcesso", "tipoDocumento", "dataDistribuicao", "processo", "classeJudicial", "dataPublicacao"]
    coletar_informacoes(ARQUIVO_UNIFICADO, campos, ARQUIVO_INFORMACOES)
