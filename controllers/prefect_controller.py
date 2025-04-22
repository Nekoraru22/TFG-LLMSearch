import os
import uuid
import time
import json
import random

from PIL import Image, ExifTags
from PyPDF2 import PdfReader

from controllers.llm_studio_controller import LLMStudioController
from controllers.chroma_controller import ChromaClient

from chromadb import QueryResult
from prefect import flow, task
from lmstudio import PredictionResult

from utils import get_mime_type, IMAGE_PREFIX, TEXT_PREFIX, PDF_MIME, get_file_hash

# Load LLM Studio model
llm = LLMStudioController("192.168.1.137", 25565, "gemma-3-12b-it")

# Load ChromaDB client
chroma_db = ChromaClient("./data/chroma_db")

# Create or retrieve the ChromaDB collection
chroma_db.create_chroma_collection(collection_name="llm_search_collection")


@flow(log_prints=True, flow_run_name='New file')
def new_file(file_path: str) -> None:
    """
    Process a new file (image, PDF, or plain text).

    Args:
        file_path: The path to the file to process.
    """
    # Check if the file is already in the database
    if chroma_db.check_duplicate(file_path):
        print(f"File {file_path} already exists in the database")
        return
    file_path_hash = get_file_hash(file_path)

    # 1) File existence check
    if not os.path.isfile(file_path):
        print(f"File does not exist: {file_path}")
        return

    # 2) Mime‐type detection
    mime = get_mime_type(file_path)
    if mime is None:
        print(f"Could not determine MIME type for file: {file_path}")
        return

    # 3) Image branch
    if mime.startswith(IMAGE_PREFIX):
        print(f"Detected image: {mime}")
        # Kick off your image tasks
        img_res = analyze_image.submit(file_path)
        img_meta = get_image_metadata.submit(file_path, file_path_hash)

        # Wait & combine
        result = img_res.result()
        metadata = img_meta.result()

        # Embed + store
        embeddings = chroma_db.create_embeddings([result])
        ids = [f"doc_{uuid.uuid4()}"]
        chroma_db.add_or_update_documents(documents=[result], embeddings=embeddings, metadatas=[metadata], ids=ids)

    # 4) PDF branch
    elif mime == PDF_MIME:
        print(f"Detected PDF: {file_path}")
        # extract text with PyPDF2
        reader = PdfReader(file_path)
        text_chunks = []
        for page in reader.pages:
            text_chunks.append(page.extract_text() or "")
        content = "\n".join(text_chunks)

        # Summarize the content
        result = summarize_text.submit(content)
        result = result.result()
        print(content)
        print(result)

        # Embed + store
        embeddings = chroma_db.create_embeddings([result])
        ids        = [f"doc_{uuid.uuid4()}"]
        metadata = {
            "path": file_path,
            "filename": os.path.basename(file_path),
            "size": os.path.getsize(file_path),
            "creation_time": time.ctime(os.path.getctime(file_path)),
            "modification_time": time.ctime(os.path.getmtime(file_path)),
            "access_time": time.ctime(os.path.getatime(file_path)),
            "page_count": len(reader.pages),
            "hash": file_path_hash,
        }
        chroma_db.add_or_update_documents(documents=[result], embeddings=embeddings, metadatas=[metadata], ids=ids)

    # 5) Plain‐text branch (e.g. .txt, .md, .csv…)
    elif mime.startswith(TEXT_PREFIX):
        print(f"Detected text file: {mime}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Summarize the content
        result = summarize_text.submit(content)
        result = result.result()
        print(content)
        print(result)

        # Embed + store
        embeddings = chroma_db.create_embeddings([result])
        ids = [f"doc_{uuid.uuid4()}"]
        metadata = {
            "path": file_path,
            "filename": os.path.basename(file_path),
            "size": os.path.getsize(file_path),
            "creation_time": time.ctime(os.path.getctime(file_path)),
            "modification_time": time.ctime(os.path.getmtime(file_path)),
            "access_time": time.ctime(os.path.getatime(file_path)),
            "hash": file_path_hash,
        }
        chroma_db.add_or_update_documents(documents=[result], embeddings=embeddings, metadatas=[metadata], ids=ids)

    # 6) Everything else
    else:
        print(f"Unsupported file type ({mime}): {file_path}")


# TODO: En lugar de crear una nueva entrada en la base datos, modificar la existente o eliminarla y crear una nueva.
@flow(log_prints=True, flow_run_name='Modified file')
def modified_file(file_path: str) -> None:
    """
    Process a modified file
    
    Args:
        file_path: The path to the file
    """
    file_path_hash = get_file_hash(file_path)

    # 1) File existence check
    if not os.path.isfile(file_path):
        print(f"File does not exist: {file_path}")
        return

    # 2) Mime‐type detection
    mime = get_mime_type(file_path)
    if mime is None:
        print(f"Could not determine MIME type for file: {file_path}")
        return

    # 3) Image branch
    if mime.startswith(IMAGE_PREFIX):
        print(f"Detected image: {mime}")
        # Kick off your image tasks
        img_res = analyze_image.submit(file_path)
        img_meta = get_image_metadata.submit(file_path, file_path_hash)

        # Wait & combine
        result = img_res.result()
        metadata = img_meta.result()

        # Embed + store
        embeddings = chroma_db.create_embeddings([result])
        ids = [f"doc_{uuid.uuid4()}"]
        chroma_db.add_or_update_documents(documents=[result], embeddings=embeddings, metadatas=[metadata], ids=ids)

    # 4) PDF branch
    elif mime == PDF_MIME:
        print(f"Detected PDF: {file_path}")
        # extract text with PyPDF2
        reader = PdfReader(file_path)
        text_chunks = []
        for page in reader.pages:
            text_chunks.append(page.extract_text() or "")
        content = "\n".join(text_chunks)

        # Summarize the content
        result = summarize_text.submit(content)
        result = result.result()
        print(content)
        print(result)

        # Embed + store
        embeddings = chroma_db.create_embeddings([result])
        ids        = [f"doc_{uuid.uuid4()}"]
        metadata = {
            "path": file_path,
            "filename": os.path.basename(file_path),
            "size": os.path.getsize(file_path),
            "creation_time": time.ctime(os.path.getctime(file_path)),
            "modification_time": time.ctime(os.path.getmtime(file_path)),
            "access_time": time.ctime(os.path.getatime(file_path)),
            "page_count": len(reader.pages),
            "hash": file_path_hash,
        }
        chroma_db.add_or_update_documents(documents=[result], embeddings=embeddings, metadatas=[metadata], ids=ids)

    # 5) Plain‐text branch (e.g. .txt, .md, .csv…)
    elif mime.startswith(TEXT_PREFIX):
        print(f"Detected text file: {mime}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Summarize the content
        result = summarize_text.submit(content)
        result = result.result()
        print(content)
        print(result)

        # Embed + store
        embeddings = chroma_db.create_embeddings([result])
        ids = [f"doc_{uuid.uuid4()}"]
        metadata = {
            "path": file_path,
            "filename": os.path.basename(file_path),
            "size": os.path.getsize(file_path),
            "creation_time": time.ctime(os.path.getctime(file_path)),
            "modification_time": time.ctime(os.path.getmtime(file_path)),
            "access_time": time.ctime(os.path.getatime(file_path)),
            "hash": file_path_hash,
        }
        chroma_db.add_or_update_documents(documents=[result], embeddings=embeddings, metadatas=[metadata], ids=ids)

    # 6) Everything else
    else:
        print(f"Unsupported file type ({mime}): {file_path}")


@flow(log_prints=True, flow_run_name='Deleted file')
def deleted_file(file_path: str) -> None:
    """
    Process a deleted file
    
    Args:
        file_path: The path to the file
    """
    chroma_db.delete_documents(file_path)


@flow(log_prints=True, flow_run_name='Query')
def proccess_query(query: str, model: str, temperature: float) -> PredictionResult:
    """
    Process a query

    Args:
        query: The query to process
    """
    relevant_db_data = rag_query_with_db(query, n_results=3)
    return rag_query(query, relevant_db_data, model, temperature)


@task
def summarize_text(text: str) -> str:
    """
    Summarize a text

    Args:
        text: The text to summarize
    """
    llm.model = "gemma-3-12b-it"
    prompt = f"""
        Original text: {text}
        Task: Summarize the content in a single sentence.
        Output: A single sentence summary.
    """
    result = llm.analyze(prompt=prompt, temperature=0.5)

    print(result)
    return str(result)

@task
def analyze_image(image_path: str) -> str:
    """
    Analyze an image

    Args:
        image_path: The path to the image
    """
    llm.model = "gemma-3-12b-it"
    result = llm.analyze(image=image_path)

    print(result)
    return str(result)

@task
def get_image_metadata(image_path: str, file_path_hash: str) -> dict:
    """
    Obtiene metadatos de una imagen y los aplana para que cada valor sea un tipo básico.
    
    Args:
        image_path: La ruta hacia la imagen.
        
    Returns:
        Un diccionario con los metadatos aplanados, listo para almacenarlos sin perder información.
    """
    metadata = {}

    # Información del sistema de archivos
    metadata.update({
        "path": image_path,
        "filename": os.path.basename(image_path),
        "size": os.path.getsize(image_path),
        "creation_time": time.ctime(os.path.getctime(image_path)),
        "modification_time": time.ctime(os.path.getmtime(image_path)),
        "access_time": time.ctime(os.path.getatime(image_path)),
        "hash": file_path_hash,
    })

    try:
        with Image.open(image_path) as img:
            # Información básica de la imagen
            metadata.update({
                "format": img.format,
                "mode": img.mode,
                "width": img.width,
                "height": img.height
            })

            # Metadatos específicos del formato
            if img.format == 'JPEG':
                exif_data = img.getexif()
                for tag_id, value in exif_data.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except Exception:
                            value = str(value)
                    metadata[f"EXIF_{tag}"] = value
            else:
                for key, value in img.info.items():
                    metadata[f"INFO_{key}"] = value

    except Exception as e:
        metadata["error"] = str(e)

    # Filtrar metadatos para cumplir con los requisitos de ChromaDB
    chroma_metadata = {}
    for key, value in metadata.items():
        if isinstance(value, (str, int, float, bool)):
            chroma_metadata[key] = value
        else:
            chroma_metadata[key] = str(value)

    return chroma_metadata

@task
def rag_query(query: str, relevant_db_data: QueryResult, model: str, temperature: float) -> PredictionResult:
    """
    Process a query using RAG (Retrieval-Augmented Generation)
    """
    llm.model = model
    print(f"RELEVANT DATA: {relevant_db_data['documents']}")

    # Pre‑serialize to avoid f‑string brace issues
    data_json = json.dumps({
        "documents": relevant_db_data["documents"],
        "metadatas": relevant_db_data["metadatas"]
    }, indent=2)

    prompt = f"""
        Original Query: {query}

        Relevant data (from ChromaDB):
        {data_json}

        Task:
        - Discard entries irrelevant to the Original Query.
        - Reorder only if strictly needed to match the query intent.
        - Extract **only** the file paths (the substring after "Path:").
        - **Output just** the final numbered list (start at 1), one path per line, with **no** additional text.

        Example output:
        Original Query: official document from the Spanish Ministry
        1. ./filesystem/Notificacion_1742000847864 - copia.pdf
    """

    result = llm.analyze(prompt=prompt, temperature=temperature)
    print(result)
    return result

@task
def rag_query_with_db(query: str, n_results: int = 3) -> QueryResult:
    """
    Procesa una consulta usando RAG (Retrieval-Augmented Generation) con ChromaDB

    Args:
        query: La consulta a procesar.
        n_results: El número de resultados a retornar de la base de datos.

    Returns:
        QueryResult: Los resultados de la búsqueda, incluyendo documentos, distancias y metadatos.
    """
    relevant_db_data = chroma_db.search_similar(query, n_results)
    return relevant_db_data
