import os
import uuid
import time
import json
import random
import subprocess

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from prefect import flow, task
from lmstudio import PredictionResult
from controllers.llm_studio_controller import LLMStudioController
from controllers.chroma_controller import ChromaClient

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
    result = result.result()
    metadata = metadata.result()
    print(metadata)

    # Create or retrieve the ChromaDB collection
    chroma_db.create_chroma_collection(collection_name="image_analysis_collection")

    # Create metadata for the image
    embeddings = chroma_db.create_embeddings([result])
    ids = [f"doc_{uuid.uuid4()}"]
    chroma_db.add_documents(documents=[result], embeddings=embeddings, ids=ids) # , metadatas=[metadata]


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
    return rag_query(query, model, temperature)


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
def get_image_metadata(image_path: str) -> dict:
    """
    Get metadata from an image

    Args:
        image_path: The path to the image
    """
    metadata = {
        "basic_info": {},
        "exif_data": {},
        "iptc_data": {},
        "xmp_data": {},
        "icc_profile": {},
        "exiftool_data": {}
    }
    
    # Check if file exists
    if not os.path.isfile(image_path):
        return {"error": f"File not found: {image_path}"}
    
    # Get basic file information
    file_stats = os.stat(image_path)
    metadata["basic_info"] = {
        "filename": os.path.basename(image_path),
        "file_size_bytes": file_stats.st_size,
        "file_size_mb": round(file_stats.st_size / (1024 * 1024), 2),
        "last_modified": file_stats.st_mtime,
        "created": file_stats.st_ctime
    }
    
    try:
        # Open the image with PIL
        with Image.open(image_path) as img:
            # Get basic image information
            metadata["basic_info"].update({
                "format": img.format,
                "mode": img.mode,
                "width": img.width,
                "height": img.height,
                "resolution": img.info.get("dpi", None)
            })
            
            # Extract EXIF data - using getexif() instead of _getexif()
            exif_data = {}
            try:
                exif_data = img.getexif()
            except (AttributeError, TypeError):
                # Fallback for older versions or unsupported formats
                if hasattr(img, '_getexif'):
                    try:
                        exif_data = img.getexif() or {}
                    except Exception:
                        pass
            
            # Process EXIF data if available
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    # Handle GPS data specially
                    if tag == "GPSInfo":
                        gps_data = {}
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_data[gps_tag] = gps_value
                        metadata["exif_data"]["GPS"] = gps_data
                    else:
                        metadata["exif_data"][tag] = value
            
            # Alternative method for EXIF in case the above fails
            if not metadata["exif_data"]:
                for key, value in img.info.items():
                    if str(key).upper().startswith('EXIF'):
                        metadata["exif_data"][key] = value
            
            # Extract ICC profile if available
            icc_profile = img.info.get('icc_profile')
            if icc_profile:
                metadata["icc_profile"]["present"] = True
                metadata["icc_profile"]["size"] = len(icc_profile)
            else:
                metadata["icc_profile"]["present"] = False
    
    except Exception as e:
        metadata["basic_info"]["error"] = str(e)
        metadata["exif_data"]["error"] = str(e) 
    
    # Use ExifTool for more comprehensive metadata extraction
    try:
        # Run ExifTool with JSON output
        result = subprocess.run(
            ["exiftool", "-j", "-a", "-u", "-G1", image_path],
            capture_output=True, 
            text=True, 
            check=True
        )
        
        exiftool_data = json.loads(result.stdout)
        if exiftool_data and len(exiftool_data) > 0:
            metadata["exiftool_data"] = exiftool_data[0]
            
            # Extract specific metadata sections if present
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
    
    return metadata

@task
def rag_query(query: str, model: str, temperature: float) -> PredictionResult:
    """
    Process a query using RAG (Retrieval-Augmented Generation)
    """
    llm.model = model
    result = llm.analyze(prompt=query, temperature=temperature)
    print(result)
    return result

@task
def meow(message: str) -> str:
    """Prueba"""
    time.sleep(random.randint(1, 5))
    print(message)
    return message
