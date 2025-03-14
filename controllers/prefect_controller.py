import random, random
import time
from prefect import flow, task


@flow(log_prints=True)
def new_file(file: str):
    """
    Process a new file
    
    Args:
        file: The path to the file
    """
    meow(file)


@flow(log_prints=True)
def modified_file(file: str):
    """
    Process a modified file
    
    Args:
        file: The path to the file
    """
    meow(file)


@flow(log_prints=True)
def deleted_file(file: str):
    """
    Process a deleted file
    
    Args:
        file: The path to the file
    """
    meow(file)


@flow(log_prints=True)
def proccess_query(query: str):
    """
    Process a query

    Args:
        query: The query to process
    """
    meow(query)


@task
def meow(message: str):
    """Prueba"""
    print(message)
    time.sleep(random.randint(1, 5))
