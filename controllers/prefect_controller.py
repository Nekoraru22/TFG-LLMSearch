import random, random
import time
from prefect import flow, task


@flow(log_prints=True)
def new_file(file: str) -> None:
    """
    Process a new file
    
    Args:
        file: The path to the file
    """
    meow(file)


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
def proccess_query(query: str) -> str:
    """
    Process a query

    Args:
        query: The query to process
    """
    return meow(query)


@task
def meow(message: str) -> str:
    """Prueba"""
    time.sleep(random.randint(1, 5))
    print(message)
    return message
