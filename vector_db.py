import chromadb
import streamlit as st

client = None
collection = None
COLLECTION_NAME = "aneel_collection"

def clean_metadata(metadata: dict) -> dict:
    """
    Clean metadata by removing None values and ensuring all values are valid ChromaDB types.
    """
    cleaned = {}
    for key, value in metadata.items():
        if value is not None:
            # Convert to string if it's not already a basic type
            if isinstance(value, (str, int, float, bool)):
                cleaned[key] = value
            else:
                cleaned[key] = str(value)
    return cleaned

def initialize_vector_db(documents: list[str], metadatas: list[dict], persist_directory: str = r"./chroma_db_data"):
    """
    Inicializa o banco de dados vetorial ChromaDB com os documentos fornecidos.
    O embedding de documentos é feito usando o modelo 'all-MiniLM-L6-v2'.
    :param documents: Lista de documentos a serem armazenados no banco de dados.
    :param persist_directory: Diretório onde os dados do banco de dados serão persistidos.
    :return: Coleção do banco de dados vetorial.
    Se a coleção já existir, ela será carregada; caso contrário, uma nova coleção será criada.
    """
    global client, collection
    
    client = chromadb.PersistentClient(path=persist_directory)

    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"Coleção '{COLLECTION_NAME}' já existe. Removendo para recriar...")
        client.delete_collection(name=COLLECTION_NAME)
    except:
        pass  # Collection doesn't exist, which is fine

    print(f"Criando nova coleção '{COLLECTION_NAME}'...")
    collection = client.create_collection(name=COLLECTION_NAME)

    # Create document IDs
    doc_ids = [f"doc_{i}" for i in range(len(documents))]
    
    # Clean metadata to remove None values
    if metadatas is None:
        metadatas = [{"source": f"doc_{i}"} for i in range(len(documents))]
    else:
        # Clean each metadata dictionary
        metadatas = [clean_metadata(metadata) for metadata in metadatas]
    
    # Add documents with cleaned metadata
    collection.add(
        documents=documents,
        ids=doc_ids,
        metadatas=metadatas
    )
    
    print(f"Banco de dados vetorial inicializado com {len(documents)} documentos.")
    return collection

def query_vector_db(query_text: str, n_results: int = 5) -> list[str]:
    """
    Consulta o banco de dados vetorial ChromaDB com uma string de consulta.
    :param query_text: Texto da consulta a ser pesquisada no banco de dados.
    :param n_results: Número de resultados a serem retornados.
    :return: Lista de documentos correspondentes à consulta.
    """
    global collection
    if not collection:
        print("Erro: Coleção não inicializada.")
        try:
            global client
            client = chromadb.PersistentClient(path=r"./chroma_db_data")
            collection = client.get_collection(name=COLLECTION_NAME)
            print(f"Coleção '{COLLECTION_NAME}' carregada com sucesso.")
        except Exception as e:
            print(f"Erro ao carregar a coleção: {e}")
            return []
    
    if not query_text:
        return []
    
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    # Armazena os resultados na sessão do Streamlit, se estiver em execução
    if 'st' in globals():
        st.session_state.last_query_results = results
    
    return results['documents'][0] if results and results['documents'] else []