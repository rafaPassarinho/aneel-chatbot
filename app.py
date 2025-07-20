import streamlit as st
import os
os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'

import chromadb

from text_processor import parse_aneel_pdf, download_pdf_if_not_exists, PDF_URL, LOCAL_PDF_PATH
from vector_db import initialize_vector_db, query_vector_db, COLLECTION_NAME
from chatbot_logic import generate_response_with_gemini

# --- Configuração ---
CHROMA_PERSIST_DIR = r"./chroma_db_data"
DB_READY_FLAG = "db_initialized.flag"

# --- Função auxiliar para Checar/Construir o banco de dados ---
def ensure_db_is_ready():
    """
    Verifica se o banco de dados vetorial está pronto. Se não estiver, inicializa-o.
    """
    if not os.path.exists(DB_READY_FLAG):
        st.info("Base de dados vetorial não encontrada. Inicializando...")
        st.info("Baixando e processando o PDF da Resolução Normativa 1000 da ANEEL...")
        with st.spinner("Isso pode levar alguns minutos... ⏳"):
            # Download PDF if needed
            if download_pdf_if_not_exists(PDF_URL, LOCAL_PDF_PATH):
                # Parse PDF and extract chunks with hierarchy
                chunks_with_metadata = parse_aneel_pdf(LOCAL_PDF_PATH)
                
                # Extract just the text content for vector DB
                text_chunks = [chunk["page_content"] for chunk in chunks_with_metadata]
                
                # Extract metadata for vector DB
                metadatas = [chunk["metadata"] for chunk in chunks_with_metadata]
                
                # Initialize vector database with chunks and metadata
                initialize_vector_db(text_chunks, metadatas, persist_directory=CHROMA_PERSIST_DIR)
                
                # Create flag file
                with open(DB_READY_FLAG, 'w') as f:
                    f.write("Database initialized with PDF content")
            else:
                st.error("Erro ao baixar o PDF. Verifique sua conexão com a internet.")
                return
                
        st.success("Base de dados vetorial inicializada com sucesso! ✅")
    else:
        # Load existing collection
        try:
            client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
            collection = client.get_collection(name=COLLECTION_NAME)
            import vector_db
            vector_db.client = client
            vector_db.collection = collection
            st.sidebar.success(f"Base de dados vetorial '{COLLECTION_NAME}' carregada com sucesso! ✅")
        except Exception as e:
            st.sidebar.error(f"Erro ao carregar a base de dados vetorial: {e}. Tentando recriar...")
            if os.path.exists(DB_READY_FLAG):
                os.remove(DB_READY_FLAG)
            ensure_db_is_ready()

# --- Streamlit App ---
st.set_page_config(page_title="ANEEL Chatbot", page_icon=":robot_face:", layout="wide")
st.title("💬 Chatbot Inteligente de Leis da ANEEL (REN1000/2021)")
st.markdown("""
Bem-vindo(a)! Pergunte sobre a Resolução Normativa ANEEL nº 1000/2021.
Este chatbot utiliza a Google Generative AI para responder às suas perguntas com base nos textos da lei.
""")

# --- Sidebar para Chave de API do Gemini e Status do Banco de Dados ---
st.sidebar.header("Configurações")
api_key_input = st.sidebar.text_input(
    "Sua Chave de API Gemini (GOOGLE_API_KEY):",
    type="password",
    help="Obtenha sua chave em https://aistudio.google.com/app/apikey"
)

# Determina qual chave usar (entrada do usuário tem prioridade)
api_key = api_key_input or os.getenv("GOOGLE_API_KEY")

if api_key:
    # Configura a chave no ambiente se foi fornecida via input
    if api_key_input:
        os.environ["GOOGLE_API_KEY"] = api_key_input
    
    # Configura o cliente Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        if api_key_input:
            st.sidebar.success("Chave de API configurada com sucesso! ✅")
        else:
            st.sidebar.info("Chave de API já configurada no ambiente. ✅")
    except Exception as e:
        st.sidebar.error(f"Erro ao configurar a chave de API: {e}")
else:
    st.sidebar.warning("Por favor, insira sua chave de API Gemini para continuar.")
    st.stop()

# Add reranker configuration in sidebar
def add_reranker_settings():
    """Add reranker configuration to sidebar."""
    st.sidebar.subheader("⚙️ Configurações de Busca")
    
    use_reranking = st.sidebar.checkbox(
        "Usar Reranking", 
        value=True, 
        help="Aplica reranking com cross-encoder para melhorar a relevância dos resultados"
    )
    
    num_results = st.sidebar.slider(
        "Número de resultados", 
        min_value=1, 
        max_value=10, 
        value=3,
        help="Número de documentos a serem retornados para o chatbot"
    )
    
    if use_reranking:
        initial_results = st.sidebar.slider(
            "Resultados iniciais (antes do reranking)", 
            min_value=5, 
            max_value=20, 
            value=10,
            help="Número de documentos recuperados antes do reranking"
        )
    else:
        initial_results = num_results
    
    return use_reranking, num_results, initial_results

use_reranking, num_results, initial_results = add_reranker_settings()

# Verifica se o banco de dados vetorial está pronto antes de permitir consultas
ensure_db_is_ready()

# Inicializa o histórico de mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra o histórico de mensagens quando o app é recarregado
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Recebe a pergunta do usuário
if prompt := st.chat_input("Qual a sua pergunta sobre a REN 1000/2021 da ANEEL?"):
    # Adiciona a pergunta ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Exibe a pergunta na interface
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Mostra a resposta da IA em um container de mensagem
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("**Pensando...** 🧠")

        # 1. Consulta o banco de dados vetorial com reranking
        if use_reranking:
            message_placeholder.markdown("**Buscando documentos relevantes...** 📚")
            retrieved_chunks = query_vector_db(
                prompt, 
                n_results=initial_results,
                use_reranking=True,
                rerank_top_k=num_results
            )
        else:
            retrieved_chunks = query_vector_db(
                prompt, 
                n_results=num_results,
                use_reranking=False
            )
        
        if not retrieved_chunks:
            full_response = "Desculpe, não consegui encontrar informações relevantes nos documentos consultados para responder à sua pergunta."
        else:
            # 2. Gera a resposta usando o modelo Gemini
            message_placeholder.markdown("**Gerando resposta...** 🤖")
            full_response = generate_response_with_gemini(prompt, retrieved_chunks)

        # Atualiza a mensagem com a resposta final
        message_placeholder.markdown(full_response)
        
        # Show sources with hierarchical information
        with st.expander("Ver fontes e contexto"):
            # Get the last query results with metadata
            if hasattr(st.session_state, 'last_query_results'):
                results = st.session_state.last_query_results
                for i, (doc, metadata) in enumerate(zip(results.get('documents', [[]])[0], results.get('metadatas', [[]])[0])):
                    st.caption(f"**Fonte {i+1}:**")
                    if metadata.get('full_hierarchical_path'):
                        st.caption(f"📍 **Localização:** {metadata['full_hierarchical_path']}")
                    if use_reranking:
                        st.caption("🏆 **Reranked result**")
                    st.caption(f"📄 **Conteúdo:** {doc[:200]}...")
                    st.divider()
            else:
                for i, doc in enumerate(retrieved_chunks):
                    st.caption(f"**Fonte {i+1}:** {doc[:200]}...")
    
    # Adiciona a resposta ao histórico
    st.session_state.messages.append({"role": "assistant", "content": full_response})