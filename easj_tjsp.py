import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


def search_and_collect(driver):
    """
    Realiza a busca e coleta informações organizadas das linhas 1 até 21 da tabela, salvando em JSON.
    """
    url = "https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do"
    results = [] 
    try:
        driver.get(url)
        time.sleep(2)

        search_input = driver.find_element(By.XPATH, '//*[@id="iddados.buscaInteiroTeor"]')
        search_input.send_keys("itau")
        search_input.send_keys(Keys.RETURN)  
        print("Busca realizada com sucesso.")
        
        time.sleep(5)

        i = 1
        while i <= 20:
            result_xpath = f'//*[@id="divDadosResultado-A"]/table/tbody/tr[{i}]'
            
            try:
                result_element = driver.find_element(By.XPATH, result_xpath)
                
                data = {                             
                    "numero": extract_text(result_element, f'//*[@id="divDadosResultado-A"]/table/tbody/tr[{i}]/td[2]/table/tbody/tr[1]/td/a[1]'),
                    "valorDaCausa": None,
                    "area_code": None,
                    "tribunal_code": None,
                    "vara_code": None,
                    "area": None,
                    "tribunal": "TJ-SP",
                    "comarca": remove_prefix(
                            extract_text(result_element, f'//*[@id="divDadosResultado-A"]/table/tbody/tr[{i}]/td[2]/table/tbody/tr[4]/td'), 
                            "Comarca: "
                        ),
                    "instancias": [{
                        "fonte_script": "Scrapper",
                        "fonte_sistema": "TJ-SP",
                        "fonte_tipo": "TRIBUNAL",
                        "fonte_url": "https://esaj.tjsp.jus.br/",

                        "grau": None,
                        "classe": None,
                        "orgaoJulgador": remove_prefix(
                            extract_text(result_element, f'//*[@id="divDadosResultado-A"]/table/tbody/tr[{i}]/td[2]/table/tbody/tr[5]/td'), 
                            "Órgão julgador: "
                        ),

                        "segredoJustica": None,
                        "justicaGratuita": None,

                        "assunto_principal": None,
                        "assuntos": remove_prefix(
                            extract_text(result_element, f'//*[@id="divDadosResultado-A"]/table/tbody/tr[{i}]/td[2]/table/tbody/tr[2]/td'), 
                            "Classe/Assunto: "
                        ),

                        "first_mov": None,
                        "last_mov": remove_prefix(extract_text(result_element, f'//*[@id="divDadosResultado-A"]/table/tbody/tr[2]/td[2]/table/tbody/tr[7]/td'),
                            "Data de publicação: "
                        ),
                         "envolvidos": [
                    {
                        "nome": None,
                        "tipo": "RECLAMANTE",
                        "polo": "ATIVO",
                        "id_sistema": {"login": None},
                        "documento": [],
                        "endereco": {},
                        "representantes": [
                            {
                                "nome": None,
                                "tipo": "ADVOGADO",
                                "polo": "ATIVO",
                                "id_sistema": {"login": None},
                                "documento": [{"CPF": None}],
                                "endereco": {
                                    "logradouro": None,
                                    "numero": None,
                                    "complemento": None,
                                    "bairro": None,
                                    "municipio": None,
                                    "estado": None,
                                    "cep": None,
                                }
                            }
                        ]
                    },
                    {
                        "nome": None,
                        "tipo": "RECLAMADO",
                        "polo": "PASSIVO",
                        "id_sistema": {"login": None},
                        "documento": [],
                        "endereco": {},
                        "representantes": [
                            {
                                "nome": None,
                                "tipo": "ADVOGADO",
                                "polo": "PASSIVO",
                                "id_sistema": {"login": None},
                                "documento": [{"CPF": None}],
                                "endereco": {
                                    "logradouro": None,
                                    "numero": None,
                                    "complemento": None,
                                    "bairro": None,
                                    "municipio": None,
                                    "estado": None,
                                    "cep": None
                                }
                            }
                        ]
                    },
                    {
                        "nome": remove_prefix(
                            extract_text(result_element, f'//*[@id="divDadosResultado-A"]/table/tbody/tr[{i}]/td[2]/table/tbody/tr[3]/td'), 
                            "Relator(a): "
                        ),
                        "tipo": "RELATOR(A)",
                        "polo": "OUTROS",
                        "id_sistema": {"login": None},
                        "documento": [],
                        "endereco": {},
                        "representantes": []
                    }
                ],

                "movimentacoes": [
                    {
                        "titulo": "Data de publicação",
                        "tipoConteudo": "HTML",
                        "data": remove_prefix(extract_text(result_element, f'//*[@id="divDadosResultado-A"]/table/tbody/tr[2]/td[2]/table/tbody/tr[7]/td'),
                            "Data de publicação: "
                        ),
                        "ativo": None,
                        "documento":None,
                        "mostrarHeaderData": None,
                        "usuarioCriador": None
                    },
                    {
                        "titulo": None,
                        "tipoConteudo": None,
                        "data": None,
                        "ativo": None,
                        "documento": None,
                        "usuarioCriador": None
                    },
                    {
                        "id": None,
                        "idUnicoDocumento": None,
                        "titulo": "Ata da Audieancia",
                        "tipo": "Ata da Audieancia",
                        "tipoConteudo": "PDF",
                        "data": remove_prefix(extract_text(result_element, f'//*[@id="divDadosResultado-A"]/table/tbody/tr[2]/td[2]/table/tbody/tr[7]/td'),
                            "Data de publicação: "
                        ),
                        "ativo": None,
                        "documentoSigiloso": None,
                        "usuarioPerito": None,
                        "publico": None,
                        "usuarioJuntada": None,
                        "usuarioCriador": None,
                        "instancia": None
                    }
                ]
            }
        ]
    }
 
                results.append(data)

                print(f"Linha {i} processada com sucesso.")
            except Exception as e:
                print(f"Erro ao acessar o resultado {i}: {e}")
            
            i += 1

        with open("resultados.json", "w", encoding="utf-8") as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=4)
        
        print("Dados salvos no arquivo 'resultados.json'.")

    except Exception as e:
        print(f"Erro durante a busca ou coleta de informações: {e}")


def extract_text(parent_element, relative_xpath):
    """
    Extrai o texto de um elemento relativo ao elemento pai.
    """
    try:
        element = parent_element.find_element(By.XPATH, relative_xpath)
        return element.text.strip()
    except Exception:
        return None
  

def remove_prefix(text, prefix):
    """Remove o prefixo especificado do texto, se presente."""
    if text and text.startswith(prefix):
        return text.replace(prefix, "").strip()
    return text


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(chrome_options)  

    try:
        search_and_collect(driver)
    finally:
        driver.quit()