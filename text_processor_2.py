import fitz
import re
import requests
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

PDF_URL = "https://www2.aneel.gov.br/cedoc/atren20211000.pdf"
LOCAL_PDF_PATH = r"../data/atren20211000.pdf"

# Document metadata
DOC_INFO_DEFAULTS = {
    "source_document_url": PDF_URL,
    "source_document_name": LOCAL_PDF_PATH,
    "document_type": "Resolução Normativa",
    "issuer": "ANEEL"
}

# Optimized patterns based on actual PDF structure
PATTERNS = {
    "titulo": re.compile(r"^\s*T[ÍI]TULO\s+([IVXLCDM]+)\s*$", re.IGNORECASE),
    "capitulo": re.compile(r"^\s*CAP[ÍI]TULO\s+([IVXLCDM]+)\s*$", re.IGNORECASE),
    "secao": re.compile(r"^\s*(?:SUB)?[Ss]e[çc][ãa]o\s+([IVXLCDM]+)\s*$", re.IGNORECASE),
    "artigo_start": re.compile(r"^\s*Art\.\s*(\d+(?:[A-Za-z])?º?)\s+(.*)", re.IGNORECASE),
    "paragrafo_start": re.compile(r"^\s*§\s*(\d+º?|único)\s+(.+)", re.IGNORECASE),
    "inciso_start": re.compile(r"^\s*([IVXLCDM]+(?:-[A-Z])?)\s*-\s*(.+)"),
    "alinea_start": re.compile(r"^\s*([a-z])\)\s*(.+)")
}

def clean_text_line(text: str) -> str:
    """Clean text by replacing special characters and normalizing whitespace."""
    replacements = {
        '\xa0': ' ',  # Non-breaking space
        '\xad': '',   # Soft hyphen
        '\u2013': '-', # En dash
        '\u2014': '-'  # Em dash
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.strip()

def download_pdf_if_not_exists(url: str, local_path: str) -> bool:
    """Download PDF if it doesn't exist locally."""
    if os.path.exists(local_path):
        print(f"Arquivo {local_path} já existe. Usando arquivo local.")
        return True
    
    print(f"Baixando PDF de {url} para {local_path}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"PDF baixado com sucesso: {local_path}")
        return True
    except requests.RequestException as e:
        print(f"Erro ao baixar o PDF: {e}")
        return False

def build_full_hierarchical_path(metadata_dict: dict) -> str:
    """Build complete hierarchical path from metadata dictionary."""
    components = [
        metadata_dict.get("titulo_text"),
        metadata_dict.get("capitulo_text"),
        metadata_dict.get("secao_text"),
        metadata_dict.get("artigo_number"),
    ]
    return " > ".join(filter(None, components))

def parse_aneel_pdf(
        pdf_path: str,
        max_chunk_size: int = 1500,
        chunk_overlap: int = 200
) -> list[dict]:
    """
    Comprehensive parsing that captures ALL content and properly tracks hierarchy.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")
    
    all_chunks = []
    current_hierarchy = {
        "titulo_text": None,
        "capitulo_text": None,
        "secao_text": None,
        "artigo_number": None
    }
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", "; ", " ", ""],
        strip_whitespace=True
    )

    try:
        doc = fitz.open(pdf_path)
        print(f"Processando PDF: {pdf_path} com {len(doc)} páginas.")

        # First pass: track hierarchy as we go through the document
        full_text_with_hierarchy = []
        
        for page_num, page in enumerate(doc, 1):
            page_text = page.get_text()
            if not page_text.strip():
                continue
                
            lines = page_text.split('\n')
            for line in lines:
                line_clean = clean_text_line(line).strip()
                if not line_clean:
                    continue
                
                # Check for hierarchy updates
                titulo_match = PATTERNS["titulo"].match(line_clean)
                capitulo_match = PATTERNS["capitulo"].match(line_clean)
                secao_match = PATTERNS["secao"].match(line_clean)
                artigo_match = PATTERNS["artigo_start"].match(line_clean)
                
                if titulo_match:
                    current_hierarchy.update({
                        "titulo_text": f"TÍTULO {titulo_match.group(1)}",
                        "capitulo_text": None,
                        "secao_text": None,
                        "artigo_number": None
                    })
                elif capitulo_match:
                    current_hierarchy.update({
                        "capitulo_text": f"CAPÍTULO {capitulo_match.group(1)}",
                        "secao_text": None,
                        "artigo_number": None
                    })
                elif secao_match:
                    current_hierarchy.update({
                        "secao_text": f"Seção {secao_match.group(1)}",
                        "artigo_number": None
                    })
                elif artigo_match:
                    current_hierarchy["artigo_number"] = f"Art. {artigo_match.group(1)}"
                
                # Store text with current hierarchy context
                full_text_with_hierarchy.append({
                    "text": line_clean,
                    "page": page_num,
                    "hierarchy": current_hierarchy.copy()  # Important: copy the dict
                })
        
        # Second pass: create chunks with proper hierarchy metadata
        all_text = "\n".join([item["text"] for item in full_text_with_hierarchy])
        text_chunks = text_splitter.split_text(all_text)
        
        for idx, chunk in enumerate(text_chunks):
            # Find the most relevant hierarchy for this chunk
            chunk_metadata = DOC_INFO_DEFAULTS.copy()
            
            # Look for hierarchy elements in the chunk text
            best_hierarchy = {"titulo_text": None, "capitulo_text": None, "secao_text": None, "artigo_number": None}
            
            # Search for hierarchy markers in the original text with hierarchy
            for item in full_text_with_hierarchy:
                if item["text"] in chunk:
                    # Update with the most specific hierarchy found
                    if item["hierarchy"]["artigo_number"]:
                        best_hierarchy = item["hierarchy"].copy()
                        break
                    elif item["hierarchy"]["secao_text"] and not best_hierarchy["secao_text"]:
                        best_hierarchy = item["hierarchy"].copy()
                    elif item["hierarchy"]["capitulo_text"] and not best_hierarchy["capitulo_text"]:
                        best_hierarchy = item["hierarchy"].copy()
                    elif item["hierarchy"]["titulo_text"] and not best_hierarchy["titulo_text"]:
                        best_hierarchy = item["hierarchy"].copy()
            
            # Update metadata with hierarchy
            chunk_metadata.update(best_hierarchy)
            
            chunk_metadata.update({
                "chunk_index": idx,
                "total_chunks": len(text_chunks),
                "full_hierarchical_path": build_full_hierarchical_path(chunk_metadata)
            })

            all_chunks.append({
                "page_content": chunk,
                "metadata": chunk_metadata
            })
            
    except Exception as e:
        print(f"Erro ao processar o PDF: {e}")
        raise
    finally:
        if 'doc' in locals():
            doc.close()
            
    print(f"Total de chunks processados: {len(all_chunks)}")
    return all_chunks

# Test the function
if download_pdf_if_not_exists(PDF_URL, LOCAL_PDF_PATH):
    print("\n=== Testing Comprehensive Parsing ===")
    chunks = parse_aneel_pdf(LOCAL_PDF_PATH)
    print(f"Total chunks extracted: {len(chunks)}")