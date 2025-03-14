from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import chromadb


def crear_embeddings(textos):
    """
    Crea embeddings para una lista de textos usando Sentence Transformers.
    
    Args:
        textos: Lista de strings con textos a procesar
    
    Returns:
        list: Lista de embeddings vectoriales
    """
    modelo = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = modelo.encode(textos)
    return embeddings


def crear_chroma_db(collection_name="mi_coleccion", persist_directory="./chroma_db"):
    """
    Crea una instancia de ChromaDB y una colección.
    
    Args:
        collection_name (str): Nombre de la colección
        persist_directory (str): Directorio donde se almacenarán los datos de forma persistente
    
    Returns:
        chromadb.Collection: Objeto de colección Chroma
    """
    # Crear un cliente Chroma con persistencia en disco
    cliente = chromadb.PersistentClient(path=persist_directory)
    print(f"Base de datos Chroma configurada para almacenarse en: {persist_directory}")
    
    # Crear una colección
    try:
        # Intentar obtener la colección si ya existe
        collection = cliente.get_collection(collection_name)
        print(f"Colección '{collection_name}' ya existe, utilizando la existente.")
    except Exception:
        # Crear una nueva colección si no existe
        collection = cliente.create_collection(collection_name)
        print(f"Colección '{collection_name}' creada exitosamente.")
    
    return collection


def agregar_documentos(collection, documentos, embeddings=None, metadatos=None, ids=None):
    """
    Agrega documentos a una colección Chroma.
    
    Args:
        collection (chromadb.Collection): Colección Chroma
        documentos (list): Lista de documentos (strings)
        embeddings (list, optional): Lista de embeddings. Si es None, se generan automáticamente.
        metadatos (list, optional): Lista de metadatos (diccionarios) para cada documento
        ids (list, optional): Lista de IDs para cada documento. Si es None, se generan automáticamente.
    """
    if ids is None:
        ids = [f"doc_{i}" for i in range(len(documentos))]
    
    if metadatos is None:
        metadatos = [{"source": "ejemplo"} for _ in range(len(documentos))]
    
    if embeddings is None:
        # Usar embeddings generados automáticamente por Chroma
        collection.add(
            documents=documentos,
            metadatas=metadatos,
            ids=ids
        )
    else:
        # Usar embeddings personalizados
        collection.add(
            documents=documentos,
            embeddings=embeddings,
            metadatas=metadatos,
            ids=ids
        )


def buscar_similares(collection, query, n_results=3, embeddings=None):
    """
    Busca documentos similares a una consulta en la colección Chroma.
    
    Args:
        collection (chromadb.Collection): Colección Chroma
        query (str): Texto de consulta
        n_results (int): Número de resultados a devolver
        embeddings (np.array, optional): Embedding de la consulta. Si es None, se genera automáticamente.
    
    Returns:
        dict: Resultados de la búsqueda
    """
    if embeddings is None:
        resultados = collection.query(
            query_texts=[query],
            n_results=n_results
        )
    else:
        resultados = collection.query(
            query_embeddings=[embeddings],
            n_results=n_results
        )
    
    return resultados


def visualizar_embeddings_3d(embeddings, labels=None, title="Visualización 3D de Embeddings", highlight_index=None, figsize=(10, 8)):
    """
    Visualiza embeddings en un espacio 3D usando PCA para reducir la dimensionalidad.
    
    Args:
        embeddings (np.array): Matrix de embeddings
        labels (list, optional): Lista de etiquetas para cada punto
        title (str): Título del gráfico
        highlight_index (int, optional): Índice del punto a resaltar
        figsize (tuple): Tamaño de la figura (ancho, alto)
    """
    # Reducir dimensionalidad a 3D usando PCA
    pca = PCA(n_components=3)
    embeddings_3d = pca.fit_transform(embeddings)
    
    # Crear figura 3D
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
    # Colores base para todos los puntos
    colors = ['blue'] * len(embeddings_3d)
    sizes = [30] * len(embeddings_3d)
    
    # Si hay un punto a resaltar, cambiarlo a rojo y hacerlo más grande
    if highlight_index is not None:
        colors[highlight_index] = 'red'
        sizes[highlight_index] = 100
    
    # Añadir etiquetas si se proporcionan
    if labels is not None:
        for i, (x, y, z) in enumerate(embeddings_3d):
            ax.text(x, y, z, labels[i], size=8, zorder=1, color='black')
    
    # Añadir información de la varianza explicada por cada componente
    explained_variance = pca.explained_variance_ratio_
    ax.set_xlabel(f'PC1 ({explained_variance[0]:.2%})')
    ax.set_ylabel(f'PC2 ({explained_variance[1]:.2%})')
    ax.set_zlabel(f'PC3 ({explained_variance[2]:.2%})') # type: ignore
    
    # Título y leyenda
    ax.set_title(title)
    
    # Añadir líneas de distancia desde el punto destacado a los demás
    if highlight_index is not None:
        punto_destacado = embeddings_3d[highlight_index]
        for i, punto in enumerate(embeddings_3d):
            if i != highlight_index:
                ax.plot([punto_destacado[0], punto[0]], 
                        [punto_destacado[1], punto[1]], 
                        [punto_destacado[2], punto[2]], 
                        'gray', alpha=0.3, linestyle=':')
                
                # Calcular distancia euclidiana
                distancia = np.linalg.norm(embeddings[highlight_index] - embeddings[i])
                # Punto medio para mostrar la distancia
                punto_medio = (punto_destacado + punto) / 2
                ax.text(punto_medio[0], punto_medio[1], punto_medio[2], f'{distancia:.2f}', size=8, color='red') # type: ignore
    
    plt.tight_layout()
    return fig


# Calcular y visualizar matriz de distancias
def visualizar_matriz_distancias(embeddings, labels=None, figsize=(10, 8)):
    """
    Visualiza una matriz de distancias entre embeddings.
    
    Args:
        embeddings (np.array): Matrix de embeddings
        labels (list, optional): Lista de etiquetas para cada embedding
        figsize (tuple): Tamaño de la figura (ancho, alto)
    """
    # Calcular matriz de distancias
    n = len(embeddings)
    dist_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            dist_matrix[i, j] = np.linalg.norm(embeddings[i] - embeddings[j])
    
    # Crear DataFrame para mejor visualización
    if labels is None:
        labels = [f"Doc {i}" for i in range(n)]
    
    df_dist = pd.DataFrame(dist_matrix, index=labels, columns=labels)
    
    # Visualizar matriz de distancias como heatmap
    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(dist_matrix, cmap='viridis')
    
    # Añadir barra de color
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Distancia Euclidiana", rotation=-90, va="bottom")
    
    # Añadir etiquetas
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    
    # Rotar etiquetas para mejor visualización
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Añadir valores de distancia en cada celda
    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{dist_matrix[i, j]:.2f}",
                           ha="center", va="center", color="white" if dist_matrix[i, j] > dist_matrix.max()/2 else "black")
    
    ax.set_title("Matriz de Distancias entre Embeddings")
    fig.tight_layout()
    
    return fig, df_dist


# Ejemplo de uso
if __name__ == "__main__":
    # Crear algunos documentos de ejemplo
    documentos = [
        "Python es un lenguaje de programación interpretado de alto nivel",
        "Los embeddings son representaciones vectoriales de texto",
        "Chroma es una base de datos vectorial para almacenar embeddings",
        "Los modelos de lenguaje pueden generar embeddings semánticos",
        "La visualización 3D ayuda a entender la distancia entre embeddings",
        "Las bases de datos vectoriales son útiles para búsquedas semánticas",
        "Los embeddings capturan la semántica de las palabras y frases",
        "Python tiene muchas bibliotecas para procesamiento de lenguaje natural"
    ]
    
    # Crear embeddings para los documentos
    embeddings = crear_embeddings(documentos)
    
    # Crear una colección Chroma con persistencia
    collection = crear_chroma_db("ejemplo_embeddings", "./data/chroma_db")
    
    # Añadir documentos con embeddings personalizados
    metadatos = [{"tipo": "definición", "fuente": "ejemplo"} for _ in range(len(documentos))]
    ids = [f"doc_{i}" for i in range(len(documentos))]
    agregar_documentos(collection, documentos, embeddings, metadatos, ids)
    
    # Realizar una búsqueda
    query = "¿Qué son los embeddings?"
    resultados = buscar_similares(collection, query, n_results=3)
    
    print("\nResultados de búsqueda para:", query)
    if resultados['documents'] is not None and resultados["distances"] is not None:
        for i, doc in enumerate(resultados['documents'][0]):
            print(f"{i+1}. {doc} (Distancia: {resultados['distances'][0][i]:.4f})")
    else:
        print("No se encontraron documentos similares.")
    
    # Visualizar embeddings en 3D
    labels = [f"Doc {i}: {doc[:20]}..." for i, doc in enumerate(documentos)]
    
    # Visualizar con el punto de consulta resaltado
    query_embedding = crear_embeddings([query])[0]
    all_embeddings = np.vstack([embeddings, query_embedding])
    all_labels = labels + [f"Query: {query}"]
    
    fig = visualizar_embeddings_3d(
        embeddings=all_embeddings,
        labels=all_labels, 
        title="Visualización 3D de Embeddings con Consulta",
        highlight_index=len(embeddings)
    )
    
    # Visualizar matriz de distancias
    fig_matriz, df_dist = visualizar_matriz_distancias(embeddings, labels)
    
    plt.show()
    
    print("\nMatriz de distancias:")
    print(df_dist)
