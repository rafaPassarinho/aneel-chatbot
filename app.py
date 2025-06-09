import streamlit as st
import os
import chromadb

from data_preprocess import clean_html
from text_processor import split_text
from vector_db import initialize_vector_db, query_vector_db, COLLECTION_NAME
from chatbot_logic import generate_response_with_gemini


# --- Configuração ---
ANEEL_REN_PATH = r"./data/ren20211000.html"
CHROMA_PERSIST_DIR = r"./chroma_db_data"
DB_READY_FLAG = "db_initialized.flag" # Arquivo de flag para verificar se o banco de dados foi inicializado

# --- Função auxiliar para Checar/Construir o banco de dados ---
def ensure_db_is_ready():
    """
    Verifica se o banco de dados vetorial está pronto. Se não estiver, inicializa-o.
    """
    if not os.path.exists(DB_READY_FLAG):
        st.info("Base de dados vetorial não encontrada. Inicializando...")
        st.info("Lendo e processando o conteúdo do arquivo HTML da Resolução Normativa 1000 da ANEEL...")
        with st.spinner("Isso pode levar alguns minutos... ⏳"):
            # Limpa o HTML e extrai o texto
            cleaned_text = clean_html(ANEEL_REN_PATH)
            # Divide o texto em pedaços menores
            chunks = split_text(cleaned_text)
            # Inicializa o banco de dados vetorial com os pedaços de texto
            initialize_vector_db(chunks, persist_directory=CHROMA_PERSIST_DIR)
            # Cria o arquivo de flag para indicar que o banco de dados foi inicializado
            with open(DB_READY_FLAG, 'w') as f:
                f.write("Database initialized")
        st.success("Base de dados vetorial inicializada com sucesso! ✅")
    else:
        # Mesmo que a Flag exista, vamos garantir que a coleção esteja carregada
        try:
            client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
            collection = client.get_collection(name=COLLECTION_NAME)
            import vector_db
            vector_db.client = client # Atualiza o client global
            vector_db.collection = collection # Atualiza a coleção global
            st.sidebar.success(f"Base de dados vetorial '{COLLECTION_NAME}' carregada com sucesso! ✅")
        except Exception as e:
            st.sidebar.error(f"Erro ao carregar a base de dados vetorial: {e}. Tentando recriar...")
            if os.path.exists(DB_READY_FLAG):
                os.remove(DB_READY_FLAG) # Remove a flag para forçar a reinicialização
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

# Determina qual chabe usar (entrada do usuário tem prioridade)
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
            st.sidebar.info("Chave de API configurada no ambiente. ✅")
    except Exception as e:
        st.sidebar.error(f"Erro ao configurar a chave de API do Gemini: {e}.")
else:
    st.sidebar.warning(f"Por favor, forneça sua chave de API do Gemini para continuar. {api_key}")
    st.stop()

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

        # 1. Consulta o banco de dados vetorial
        retrieved_chunks = query_vector_db(prompt, n_results=3)
        
        if not retrieved_chunks:
            full_response = "Desculpe, não consegui encontrar informações relevantes nos documentos consultados para responder à sua pergunta."
        else:
            # 2. Gera a resposta usando o modelo Gemini
            full_response = generate_response_with_gemini(prompt, retrieved_chunks)

        # Atualiza a mensagem com a resposta final
        message_placeholder.markdown(full_response)
        with st.expander("Ver fontes"):
            for doc in retrieved_chunks:
                st.caption(f"Fonte: {doc};")  # Exibe os primeiros 100 caracteres de cada documento recuperado
    
    # Adiciona a resposta ao histórico
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    