import random
import time

from lmstudio import PredictionResult
from controllers.llm_studio_controller import LLMStudioController
from prefect import flow, task

# Load LLM Studio model
llm = LLMStudioController("192.168.1.137", 25565, "gemma-3-12b-it")


@flow(log_prints=True)
def new_file(file: str) -> None:
    """
    Process a new file
    
    Args:
        file: The path to the file
    """
    analyze_image(file)


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
def analyze_image(image: str) -> PredictionResult:
    """
    Analyze an image
    """
    llm.model = "gemma-3-12b-it"
    result = llm.analyze(image=image)
    print(result) # TODO: A la base de datos formateado xD
    return result

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
