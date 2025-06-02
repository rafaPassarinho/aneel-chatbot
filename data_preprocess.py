from bs4 import BeautifulSoup
import re

def clean_html(html_path: str) -> str:
    """
    Lê arquivo HTML, remove elementos com estilo line-through e retorna o texto limpo.
    :param html_path: Caminho para o arquivo HTML.
    :return: Texto limpo do HTML.
    """
    with open(html_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'lxml')
    
    for strike in soup.find_all(style=re.compile('line-through')):
        strike.decompose()
    
    # Extrai o texto limpo
    return soup.get_text(separator='\n', strip=True)