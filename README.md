# 💬 ANEEL Chatbot - Resolução Normativa 1000/2021

Chatbot inteligente especializado em responder perguntas sobre a Resolução Normativa ANEEL nº 1000/2021. Este projeto utiliza técnicas de RAG (Retrieval-Augmented Generation) com Google Gemini AI para fornecer respostas precisas baseadas no documento oficial.

**Projeto Final de Curso - Especialização em NLP da AKCIT**

## 🚀 Funcionalidades

- ✅ Interface web intuitiva com Streamlit
- ✅ Processamento de documentos HTML da ANEEL
- ✅ Busca semântica com ChromaDB
- ✅ Respostas contextualizadas com Google Gemini AI
- ✅ Configuração flexível de API key
- ✅ Cache inteligente do banco de dados vetorial

## 📁 Estrutura do Projeto

```
aneel-chatbot/
├── app.py                    # Interface principal Streamlit
├── chatbot_logic.py         # Lógica do chatbot com Gemini AI
├── data_preprocess.py       # Processamento de documentos HTML
├── text_processor.py        # Divisão de texto em chunks
├── vector_db.py            # Gerenciamento do banco vetorial
├── requirements.txt        # Dependências do projeto
├── .env                    # Variáveis de ambiente (não commitado)
├── README.md              # Este arquivo
├── data/
│   ├── ren20211000.html   # Documento da REN 1000/2021
│   └── cleaned_text.txt   # Texto limpo (gerado automaticamente)
├── chroma_db_data/        # Banco de dados vetorial (gerado automaticamente)
└── notebooks/
    └── teste.ipynb        # Notebooks de desenvolvimento
```

## ⚙️ Pré-requisitos

- Python 3.8 ou superior
- Chave de API do Google Gemini ([obter aqui](https://aistudio.google.com/app/apikey))

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd aneel-chatbot
```

### 2. Crie um ambiente virtual (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure a chave de API do Gemini

**Opção A: Arquivo .env (recomendado)**
```bash
# Crie um arquivo .env na raiz do projeto
echo GOOGLE_API_KEY=sua_chave_api_aqui > .env
```

**Opção B: Via interface web**
- Execute o projeto e insira a chave diretamente na sidebar

## 🏃‍♂️ Como Executar

```bash
streamlit run app.py
```

O aplicativo será aberto automaticamente no seu navegador em `http://localhost:8501`

## 📖 Como Usar

1. **Configure a API Key**: Insira sua chave do Google Gemini na sidebar ou configure no arquivo `.env`
2. **Aguarde a inicialização**: Na primeira execução, o sistema processará o documento da ANEEL (pode levar alguns minutos)
3. **Faça suas perguntas**: Digite perguntas sobre a REN 1000/2021 no chat
4. **Receba respostas contextualizadas**: O chatbot responderá baseado no documento oficial

## 🗂️ Dados

O projeto utiliza o arquivo `data/ren20211000.html` que contém a Resolução Normativa ANEEL nº 1000/2021. O sistema automaticamente:

1. Processa e limpa o HTML
2. Divide o texto em chunks menores
3. Cria embeddings e armazena no ChromaDB
4. Gera um arquivo de flag para evitar reprocessamento

## 🐛 Solução de Problemas

### Erro de API Key
- Verifique se a chave está correta no arquivo `.env` ou na interface
- Certifique-se de que a chave tem permissões para o Gemini AI

### Erro de Banco de Dados
- Delete a pasta `chroma_db_data/` e o arquivo `db_initialized.flag`
- Reinicie a aplicação para recriar o banco

### Dependências
- Use um ambiente virtual isolado
- Verifique se todas as dependências do `requirements.txt` foram instaladas

## 📝 Licença

Este projeto é desenvolvido para fins acadêmicos como parte do Projeto Final de Curso da Especialização em NLP da AKCIT.

## 👥 Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request
