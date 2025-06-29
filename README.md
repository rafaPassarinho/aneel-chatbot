# Chatbot Inteligente ANEEL - Resolução Normativa 1000/2021

Repositório de código referente ao **Projeto Final de Curso** da Especialização _lato sensu_ em Processamento de Linguagem Natural (NLP) do **AKCIT** - Centro de Competência EMBRAPII em Tecnologias Imersivas (_Advanced Knowledge Center for Immersive Technologies_).

Este projeto implementa um chatbot inteligente especializado em responder perguntas sobre a Resolução Normativa ANEEL nº 1000/2021, utilizando técnicas de RAG (Retrieval-Augmented Generation) com Google Gemini AI.

## Recomendação

É altamente recomendado que você tenha conhecimento básico em Python, Streamlit e conceitos de RAG antes de executar este projeto.

## Como executar?

Acompanhe o seguinte passo a passo para configurar e executar o chatbot ANEEL.

1. **Baixe o código** disponível aqui, nesse repositório, clicando no botão **Code** e depois em **Download ZIP**.

2. **Extraia o arquivo** baixado para uma pasta de sua escolha.

3. **Verifique a estrutura** da pasta extraída. Ela deve possuir a seguinte organização:
   ```
   aneel-chatbot/
   ├── app.py                    # Interface principal Streamlit
   ├── chatbot_logic.py         # Lógica do chatbot com Gemini AI
   ├── text_processor.py      # Processamento de PDF com hierarquia
   ├── vector_db.py            # Gerenciamento do banco vetorial
   ├── requirements.txt        # Dependências do projeto
   ├── .env.example            # Exemplo de arquivo de ambiente
   ├── README.md              # Este arquivo
   ├── data/
   │   └── atren20211000.pdf   # Documento da REN 1000/2021 (baixado automaticamente)
   ├── chroma_db_data/        # Banco de dados vetorial (criado automaticamente)
   └── notebooks/
       └── teste.ipynb        # Notebooks de desenvolvimento
   ```

4. **Obtenha sua chave de API do Google Gemini**:
   - Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Crie uma conta ou faça login
   - Gere uma nova chave de API
   - Guarde essa chave em local seguro

---

> ❗ **Importante**: Você precisará de uma chave de API válida do Google Gemini para usar este chatbot. Sem ela, o sistema não funcionará.

---

> ❗ **Antes de prosseguir**: Certifique-se de ter o **Anaconda** instalado em seu sistema. Se não tiver, baixe e instale através do [site oficial do Anaconda](https://www.anaconda.com/products/distribution).

---

5. **Configure o ambiente Anaconda**:

   **Windows:**
   ```bash
   # Abra o Anaconda Powershell Prompt (não o CMD comum)
   cd caminho\para\aneel-chatbot
   conda create --name aneel-chatbot python=3.9
   conda activate aneel-chatbot
   ```

   **Linux/Mac:**
   ```bash
   # Abra o terminal
   cd caminho/para/aneel-chatbot
   conda create --name aneel-chatbot python=3.9
   conda activate aneel-chatbot
   ```

6. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```
   
   > 💡 **Dica**: Se preferir usar apenas conda, você pode instalar as principais dependências com:
   > ```bash
   > conda install streamlit
   > pip install -r requirements.txt  # Para dependências específicas não disponíveis no conda
   > ```

7. **Configure suas variáveis de ambiente**:
   - Copie o arquivo `.env.example` e renomeie para `.env`
   - Edite o arquivo `.env` e substitua `sua_chave_api_aqui` pela sua chave real do Google Gemini:
   
   ```
   GOOGLE_API_KEY=sua_chave_api_aqui
   ```

8. **Execute o aplicativo**:
   ```bash
   # Certifique-se de que o ambiente está ativo
   conda activate aneel-chatbot
   streamlit run app.py
   ```

9. **Acesse o chatbot**:
   - O aplicativo será aberto automaticamente no seu navegador
   - Caso não abra, acesse: `http://localhost:8501`

10. **Primeira execução**:
    - Na primeira vez, o sistema baixará automaticamente o PDF da ANEEL
    - O processamento do documento pode levar alguns minutos
    - Aguarde até que apareça a mensagem "Base de dados vetorial inicializada com sucesso!"

11. **Interaja com o chatbot**:
    - Digite suas perguntas sobre a REN 1000/2021 na caixa de chat
    - O chatbot responderá com base no documento oficial da ANEEL
    - Use perguntas como:
      - "O que é consumidor livre?"
      - "Quais são as modalidades tarifárias?"
      - "Como funciona o sistema de compensação de energia?"

> ❗ **Lembre-se** de aguardar alguns segundos após enviar sua pergunta para o chatbot processar e responder.

## 🔧 Funcionalidades

- ✅ **Interface web intuitiva** com Streamlit
- ✅ **Processamento inteligente de PDF** com extração hierárquica
- ✅ **Busca semântica** utilizando ChromaDB
- ✅ **Respostas contextualizadas** com Google Gemini AI
- ✅ **Configuração flexível** de API key (.env ou interface)
- ✅ **Cache inteligente** do banco de dados vetorial
- ✅ **Fontes das respostas** com localização hierárquica

## 🐛 Solução de Problemas

### Erro de API Key
- Verifique se a chave está correta no arquivo `.env`
- Certifique-se de que a chave tem permissões para o Gemini AI
- Teste a chave diretamente no Google AI Studio

### Erro de Banco de Dados
- Delete a pasta `chroma_db_data/` e o arquivo `db_initialized.flag`
- Reinicie a aplicação para recriar o banco

### Erro de Dependências
- Certifique-se de estar no ambiente Anaconda correto: `conda activate aneel-chatbot`
- Atualize o pip: `python -m pip install --upgrade pip`
- Reinstale as dependências: `pip install -r requirements.txt --force-reinstall`
- Se usar Windows, certifique-se de estar usando o **Anaconda Powershell Prompt**

### Erro de Ambiente Anaconda
- Liste os ambientes disponíveis: `conda env list`
- Se o ambiente não existir, recrie-o: `conda create --name aneel-chatbot python=3.9`
- Para remover um ambiente corrompido: `conda env remove --name aneel-chatbot`

### Erro de Memória
- Reduza o tamanho dos chunks em `text_processor.py`
- Feche outros aplicativos que consomem muita memória
- No Anaconda, você pode monitorar o uso de memória com: `conda list`

## 📝 Tecnologias Utilizadas

- **Python 3.8+**: Linguagem principal
- **Streamlit**: Interface web
- **Google Gemini AI**: Modelo de linguagem
- **ChromaDB**: Banco de dados vetorial
- **LangChain**: Processamento de texto
- **PyMuPDF**: Processamento de PDF

> 🎓 *Este projeto demonstra a aplicação prática de técnicas de RAG e processamento de linguagem natural para criar soluções inteligentes no domínio regulatório brasileiro.*

