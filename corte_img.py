import os
import pytesseract
import json
from PIL import Image
from PIL import ImageFilter


if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def cortar_e_salvar_img(image_path, coordenadas, novo_nome):
    """Corta e salva uma parte da imagem."""
    image = Image.open(image_path)
    cropped_imagem = image.crop(coordenadas)
    
    sharpened_imagem = cropped_imagem.filter(ImageFilter.SHARPEN)
    
    sharpened_imagem.save(novo_nome)
    print(f"Imagem salva como: {novo_nome}")

def obter_proximo_nome_arquivo(base_nome, extensao):
    """Obtém o próximo nome de arquivo com contagem incremental."""
    contador = 1
    while os.path.exists(f"{base_nome}_{contador}{extensao}"):
        contador += 1
    return f"{base_nome}_{contador}{extensao}"

def processar_varias_imagens_e_cortes(diretorio):
    """Processa imagens de um diretório com cortes e salva os resultados em JSON."""
    os.makedirs("cortes", exist_ok=True)

    imagens_info = []

    for filename in os.listdir(diretorio):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(diretorio, filename)
            coordenadas_lista = [
                (0, 255, 100, 275),  # exemplo de coordenadas (esquerda, cima, direita, baixo)
                (0, 275, 100, 300)
            ]
            imagens_info.append({
                "image_path": image_path,
                "coordenadas_lista": coordenadas_lista
            })

    resultados = {}

    for info in imagens_info:
        image_path = info['image_path']
        coordenadas_lista = info['coordenadas_lista']

        for i, coordenadas in enumerate(coordenadas_lista):
            novo_nome = f"cortes/{os.path.splitext(os.path.basename(image_path))[0]}_crop_{i+1}.png"
            cortar_e_salvar_img(image_path, coordenadas, novo_nome)

            image = Image.open(novo_nome)
            ocr_config = '--psm 11 --oem 3 -c tessedit_char_whitelist=1234567890()-'
            result = pytesseract.image_to_string(image, config=ocr_config)
            result = result.strip().replace(chr(32), "").replace("\n", "")

            resultados[os.path.basename(image_path)] = resultados.get(os.path.basename(image_path), [])
            resultados[os.path.basename(image_path)].append({
                "telefone": i + 1,
                "resultado": result
            })

    nome_arquivo_json = obter_proximo_nome_arquivo("numero_telefone", ".json")
    with open(nome_arquivo_json, "w", encoding="utf-8") as json_file:
        json.dump(resultados, json_file, indent=4, ensure_ascii=False)
    print(f"Resultados salvos em {nome_arquivo_json}")

diretorio_imagens = "imgs_CNA_OAB"
processar_varias_imagens_e_cortes(diretorio_imagens)
