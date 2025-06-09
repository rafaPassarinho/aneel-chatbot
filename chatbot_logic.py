import google.generativeai as genai
import os

try:
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("A chave de API do Google Generative AI não está definida.")
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception as e:
    print(f"Erro ao configurar o Gemini API: {e}. Certifique-se de definir a variável de ambiente GOOGLE_API_KEY.")

def generate_response_with_gemini(query: str, context_chunks: list[str]) -> str:
    """
    Gera uma resposta usando o modelo Gemini da Google Generative AI, incorporando o contexto fornecido.
    :param query: Texto da consulta do usuário.
    :param context_chuncks: Lista de fragmentos de contexto que fornecem informações adicionais para a resposta.
    :return: Resposta gerada pelo modelo Gemini.
    """
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("Erro: A chave de API do Gemini não está definida. Por favor, defina a variável de ambiente GOOGLE_API_KEY.")
    
    # Prepara o contexto para a consulta
    context_str = "\n\n---\n\n".join(context_chunks)
    prompt = f"""
Você é um assistente de IA especializado em leis e regulamentos brasileiros da ANEEL.
Sua tarefa é responder à pergunta do usuário com base estritamente nos trechos de lei fornecidos abaixo.
Não utilize conhecimento externo. Se a resposta não puder ser encontrada nos trechos fornecidos,
declare explicitamente que a informação não está disponível nos documentos consultados.
Seja conciso e direto ao ponto. Responda em português brasileiro.

**Contexto (Trechos da Lei):**
{context_str}

**Pergunta do Usuário:**
{query}

**Sua Resposta:**
"""
    
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-8b")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Erro durante a chamada de API do Gemini: {e}")
        return "Desculpe, ocorreu um erro ao tentar gerar uma resposta."
