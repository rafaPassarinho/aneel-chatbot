import chromadb
import streamlit as st
from chromadb.utils import embedding_functions

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
    O embedding de documentos é feito usando o modelo 'multilingual-e5-base'.
    :param documents: Lista de documentos a serem armazenados no banco de dados.
    :param persist_directory: Diretório onde os dados do banco de dados serão persistidos.
    :return: Coleção do banco de dados vetorial.
    Se a coleção já existir, ela será carregada; caso contrário, uma nova coleção será criada.
    """
    global client, collection
    
    # cria a função de embedding com multilingual-e5-base
    multilingual_e5 = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="intfloat/multilingual-e5-base"
    )

    client = chromadb.PersistentClient(path=persist_directory)

    try:
        collection = client.get_collection(name=COLLECTION_NAME)
        print(f"Coleção '{COLLECTION_NAME}' já existe. Removendo para recriar...")
        client.delete_collection(name=COLLECTION_NAME)
    except:
        pass  # Collection doesn't exist, which is fine

    print(f"Criando nova coleção '{COLLECTION_NAME}' com modelo 'multilingual-e5-base'...")
    collection = client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=multilingual_e5
    )

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

    print(f"Banco de dados vetorial inicializado com {len(documents)} documentos usando o modelo 'multilingual-e5-base'.")
    return collection

def query_vector_db(query_text: str, n_results: int = 5, use_reranking: bool = True, rerank_top_k: int = None) -> list[str]:
    """
    Consulta o banco de dados vetorial ChromaDB com uma string de consulta.
    Opcionalmente, aplica reranking.
    
    :param query_text: Texto da consulta a ser pesquisada no banco de dados.
    :param n_results: Número de resultados iniciais a serem recuperados (antes do reranking).
    :param use_reranking: Se deve aplicar reranking aos resultados.
    :param rerank_top_k: Número final de resultados após reranking (se None, usa n_results).
    :return: Lista de documentos correspondentes à consulta.
    """
    global collection
    if not collection:
        print("Erro: Coleção não inicializada.")
        try:
            global client
            multilingual_e5 = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="intfloat/multilingual-e5-base"
            )

            client = chromadb.PersistentClient(path=r"./chroma_db_data")
            collection = client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=multilingual_e5
            )
            print(f"Coleção '{COLLECTION_NAME}' carregada com sucesso usando intfloat/multilingual-e5-base.")
        except Exception as e:
            print(f"Erro ao carregar a coleção: {e}")
            return []
    
    if not query_text:
        return []
    
    # Get more results initially if using reranking
    initial_results = max(n_results * 2, 10) if use_reranking else n_results
    
    results = collection.query(
        query_texts=[query_text],
        n_results=initial_results
    )
    
    documents = results.get('documents', [[]])[0]
    metadatas = results.get('metadatas', [[]])[0]
    
    if not documents:
        return []
    
    if use_reranking and len(documents) > 1:
        try:
            from reranker import rerank_documents
            final_top_k = rerank_top_k or n_results
            
            print(f"Aplicando reranking aos {len(documents)} documentos recuperados...")
            reranked_docs, reranked_metas = rerank_documents(
                query_text, 
                documents, 
                metadatas, 
                top_k=final_top_k
            )
            
            # Update results with reranked data
            results['documents'] = [reranked_docs]
            results['metadatas'] = [reranked_metas]
            documents = reranked_docs
            
            print(f"Reranking concluído. Retornando {len(documents)} documentos.")
            
        except ImportError:
            print("Módulo reranker não disponível. Usando resultados sem reranking.")
        except Exception as e:
            print(f"Erro durante reranking: {e}. Usando resultados sem reranking.")
    
    # Store results in Streamlit session
    try:
        import streamlit as st
        st.session_state.last_query_results = results
    except:
        pass
    
    return documents