from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> list[str]:
    """
    Divide o texto em pedaços menores com base no tamanho do chunk e na sobreposição.
    :param text: String de texto a ser dividida.
    :param chunk_size: Tamanho máximo de cada pedaço de texto.
    :param chunk_overlap: Número de caracteres que se sobrepõem entre pedaços consecutivos.
    :return: Lista de pedaços de texto.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True
    )
    documents = text_splitter.create_documents([text])
    return [doc.page_content for doc in documents]