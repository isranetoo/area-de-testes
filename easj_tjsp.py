import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

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
        while i <= 10:
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

                        "first_mov": "2024-09-26T11:43:42.215",
                        "last_mov": "2024-12-26T11:43:41.894",

                        "envolvidos": [
                            {
                                "nome": "J. M. R. I.",
                                "tipo": "RECLAMANTE",
                                "polo": "ATIVO",
                                "id_sistema": {"login": "03411657430"},
                                "documento": [],
                                "endereco": {},
                                "representantes": [
                                    {
                                        "nome": "RENE GOMES DA VEIGA PESSOA JUNIOR",
                                        "tipo": "ADVOGADO",
                                        "polo": "ATIVO",
                                        "id_sistema": {"login": "03867168466"},
                                        "documento": [{"CPF": "038.671.684-66"}],
                                        "endereco": {
                                            "logradouro": "CARACOL",
                                            "numero": "00",
                                            "complemento": "BL 02 AP 302",
                                            "bairro": "CANDEIAS",
                                            "municipio": "JABOATAO DOS GUARARAPES",
                                            "estado": "PE",
                                            "cep": "54430-180"
                                        }
                                    }
                                ]
                            }
                        ]
                    }],
                    "Relator(a)": remove_prefix(
                        extract_text(result_element, f'//*[@id="divDadosResultado-A"]/table/tbody/tr[{i}]/td[2]/table/tbody/tr[3]/td'), 
                        "Relator(a): "
                    ),
                    "Comarca": extract_text(result_element, f'//*[@id="divDadosResultado-A"]/table/tbody/tr[{i}]/td[2]/table/tbody/tr[4]/td'),
                    "Data do julgamento": extract_text(result_element, f'//*[@id="divDadosResultado-A"]/table/tbody/tr[{i}]/td[2]/table/tbody/tr[6]/td'),
                    "Data de publicação": extract_text(result_element, f'//*[@id="divDadosResultado-A"]/table/tbody/tr[2]/td[2]/table/tbody/tr[7]/td'),
                    "Ementa": extract_text(result_element, f'//*[@id="divDadosResultado-A"]/table/tbody/tr[2]/td[2]/table/tbody/tr[8]/td/div[1]')
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
    """
    Remove o prefixo especificado do texto, se presente.
    
    Args:
        text (str): O texto a ser processado.
        prefix (str): O prefixo a ser removido.
    
    Returns:
        str: O texto sem o prefixo, ou o texto original se o prefixo não for encontrado.
    """
    if text and text.startswith(prefix):
        return text.replace(prefix, "").strip()
    return text

if __name__ == "__main__":
    driver = webdriver.Chrome()  

    try:
        search_and_collect(driver)
    finally:
        driver.quit()
