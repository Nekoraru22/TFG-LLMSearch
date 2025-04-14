import os
import uuid
import time
import json
import random
import subprocess

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from controllers.llm_studio_controller import LLMStudioController
from controllers.chroma_controller import ChromaClient

from chromadb import QueryResult
from prefect import flow, task
from lmstudio import PredictionResult

# Load LLM Studio model
llm = LLMStudioController("192.168.1.137", 25565, "gemma-3-12b-it")

# Load ChromaDB client
chroma_db = ChromaClient("./data/chroma_db")


@flow(log_prints=True)
def new_file(file_path: str) -> None:
    """
    Process a new file
    
    Args:
        file: The path to the file
    """
    # Check if file exists
    if not os.path.isfile(file_path):
        print(f"File does not exist: {file_path}")
        return

    # TODO: If image, If other...

    # Analyze the image and get metadata
    result = analyze_image.submit(file_path)
    metadata = get_image_metadata.submit(file_path)

    # Wait for the tasks to complete
    result = result.result() + "\n" + f"Path: \"{file_path}\""
    metadata = metadata.result()
    print(metadata)

    # Create or retrieve the ChromaDB collection
    chroma_db.create_chroma_collection(collection_name="image_analysis_collection")

    # Create metadata for the image
    embeddings = chroma_db.create_embeddings([result])
    ids = [f"doc_{uuid.uuid4()}"]
    chroma_db.add_documents(documents=[result], embeddings=embeddings, metadatas=[metadata], ids=ids)


@flow(log_prints=True)
def modified_file(file: str) -> None:
    """
    Process a modified file
    
    Args:
        file: The path to the file
    """
    meow(file)


@flow(log_prints=True)
def deleted_file(file: str) -> None:
    """
    Process a deleted file
    
    Args:
        file: The path to the file
    """
    meow(file)


@flow(log_prints=True)
def proccess_query(query: str, model: str, temperature: float) -> PredictionResult:
    """
    Process a query

    Args:
        query: The query to process
    """
    relevant_db_data = rag_query_with_db(query, n_results=3)
    return rag_query(query, relevant_db_data, model, temperature)


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

def flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
    """
    Aplana un diccionario anidado. Cada clave resultante será la concatenación de las claves
    de cada nivel separadas por `sep`.
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            # Si el diccionario está vacío, lo serializamos a JSON
            if not v:
                items[new_key] = json.dumps(v)
            else:
                items.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list):
            # Convertimos las listas a una cadena JSON
            items[new_key] = json.dumps(v)
        elif v is None:
            # Opcional: puedes usar una cadena vacía o mantener "None" como string
            items[new_key] = ""
        else:
            items[new_key] = v
    return items

@task
def get_image_metadata(image_path: str) -> dict:
    """
    Obtiene metadatos de una imagen y los aplana para que cada valor sea un tipo básico.
    
    Args:
        image_path: La ruta hacia la imagen.
        
    Returns:
        Un diccionario con los metadatos aplanados, listo para almacenarlos sin perder información.
    """
    metadata = {
        "basic_info": {},
        "exif_data": {},
        "iptc_data": {},
        "xmp_data": {},
        "icc_profile": {},
        "exiftool_data": {}
    }
    
    # Verificar si el archivo existe
    if not os.path.isfile(image_path):
        return {"error": f"Archivo no encontrado: {image_path}"}
    
    # Información básica del archivo
    file_stats = os.stat(image_path)
    metadata["basic_info"] = {
        "filename": os.path.basename(image_path),
        "file_size_bytes": file_stats.st_size,
        "file_size_mb": round(file_stats.st_size / (1024 * 1024), 2),
        "last_modified": file_stats.st_mtime,
        "created": file_stats.st_ctime
    }
    
    try:
        # Abrir la imagen con PIL
        with Image.open(image_path) as img:
            # Actualizar información básica de la imagen
            metadata["basic_info"].update({
                "format": img.format,
                "mode": img.mode,
                "width": img.width,
                "height": img.height,
                "resolution": img.info.get("dpi", None)
            })
            
            # Extraer datos EXIF
            exif_data = {}
            try:
                exif_data = img.getexif()
            except (AttributeError, TypeError):
                if hasattr(img, '_getexif'):
                    try:
                        exif_data = img.getexif() or {}
                    except Exception:
                        pass
            
            # Procesar EXIF si está disponible
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == "GPSInfo":
                        gps_data = {}
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_data[gps_tag] = gps_value
                        metadata["exif_data"]["GPS"] = gps_data
                    else:
                        metadata["exif_data"][tag] = value
            
            # Método alternativo para extraer EXIF
            if not metadata["exif_data"]:
                for key, value in img.info.items():
                    if str(key).upper().startswith('EXIF'):
                        metadata["exif_data"][key] = value
            
            # Extraer perfil ICC
            icc_profile = img.info.get('icc_profile')
            if icc_profile:
                metadata["icc_profile"]["present"] = True
                metadata["icc_profile"]["size"] = len(icc_profile)
            else:
                metadata["icc_profile"]["present"] = False
    
    except Exception as e:
        metadata["basic_info"]["error"] = str(e)
        metadata["exif_data"]["error"] = str(e)
    
    # Utilizar ExifTool para una extracción más completa de metadatos
    try:
        result = subprocess.run(
            ["exiftool", "-j", "-a", "-u", "-G1", image_path],
            capture_output=True, 
            text=True, 
            check=True
        )
        exiftool_data = json.loads(result.stdout)
        if exiftool_data and len(exiftool_data) > 0:
            metadata["exiftool_data"] = exiftool_data[0]
            
            # Extraer secciones específicas (como IPTC y XMP)
            for key, value in exiftool_data[0].items():
                if ":" in key:
                    section, name = key.split(":", 1)
                    if section == "IPTC":
                        metadata["iptc_data"][name] = value
                    elif section == "XMP":
                        metadata["xmp_data"][name] = value
    except Exception as e:
        metadata["exiftool_data"]["error"] = str(e)
        metadata["exiftool_data"]["output"] = None

    # Aplanar el diccionario de metadatos para cumplir con el formato requerido
    flat_metadata = flatten_dict(metadata)
    return flat_metadata

@task
def rag_query(query: str, relevant_db_data: QueryResult, model: str, temperature: float) -> PredictionResult:
    """
    Process a query using RAG (Retrieval-Augmented Generation)
    """
    llm.model = model
    print(f"RELEVANT DATA: {relevant_db_data['documents']}")
    prompt = f"Query: {query}\n\nRelevant data:\n{relevant_db_data['documents']}"
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
    
    print("\nSearch results for:", query)
    if (relevant_db_data['documents'] is not None and relevant_db_data['distances'] is not None):
        for i, doc in enumerate(relevant_db_data['documents'][0]):
            metadata = (relevant_db_data.get("metadatos", [[None]])[0][i]
                        if relevant_db_data.get("metadatos") is not None else None)
            print(f"{i+1}. {doc} (Distance: {relevant_db_data['distances'][0][i]:.4f}) - Metadata: {metadata}")
    else:
        print("No similar documents were found.")
    
    return relevant_db_data

@task
def meow(message: str) -> str:
    """Prueba"""
    time.sleep(random.randint(1, 5))
    print(message)
    return message
