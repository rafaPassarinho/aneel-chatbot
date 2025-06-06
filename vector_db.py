import chromadb

client = None
collection = None
COLLECTION_NAME = "aneel_collection"

def initialize_vector_db(documents: list[str], persist_directory: str = "./chroma_db_data"):
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
        print(f"Coleção '{COLLECTION_NAME}' carregada com sucesso.")
    except:
        print(f"Coleção '{COLLECTION_NAME}' não encontrada. Criando uma nova coleção.")
        collection = client.create_collection(name=COLLECTION_NAME)
        print(f"Coleção '{COLLECTION_NAME}' criada com sucesso.")

        # Adiciona os documentos à coleção
        # cria IDs únicos para cada documento
        doc_ids = [f"doc_{i}" for i in range(len(documents))]
        collection.add(
            documents=documents,
            ids=doc_ids,
            embeddings=None,  # O embedding será feito automaticamente pelo ChromaDB
            metadatas=[{"source": f"document_{i}"} for i in range(len(documents))]
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
        print("Erro: Coleção não inicializada. Por favor, chame initialize_vector_db primeiro.")
        try:
            global client
            client = chromadb.PersistentClient(path="./chroma_db_data")
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
    return results['documents'][0] if results and results['documents'] else []