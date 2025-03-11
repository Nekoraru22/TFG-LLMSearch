from typing import List, Tuple, Any, Optional

import sqlite3
import os


class DatabaseController:
    """
    Clase para gestionar operaciones básicas con bases de datos SQLite.
    """
    
    def __init__(self, db_file: str) -> None:
        """
        Inicializa la conexión a la base de datos.
        
        Args:
            db_file: Ruta al archivo de la base de datos
        """
        self.db_file = db_file
        self.connection = None
        self.cursor = None
    

    def connect(self) -> bool:
        """
        Establece la conexión con la base de datos.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            # Verifica si la base de datos existe
            db_exists = os.path.exists(self.db_file)
            
            # Conecta a la base de datos
            self.connection = sqlite3.connect(self.db_file)
            self.cursor = self.connection.cursor()
            
            if not db_exists:
                print(f"Base de datos '{self.db_file}' creada exitosamente.")
            else:
                print(f"Conexión exitosa a '{self.db_file}'.")
            
            return True
        except sqlite3.Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return False
    

    def disconnect(self) -> None:
        """
        Cierra la conexión con la base de datos.
        """
        if self.connection:
            self.connection.close()
            print("Conexión cerrada.")
            self.connection = None
            self.cursor = None
    

    def execute_query(self, query: str, params: tuple = ()) -> bool:
        """
        Ejecuta una consulta SQL sin retorno de datos (CREATE, INSERT, UPDATE, DELETE).
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            bool: True si la ejecución fue exitosa, False en caso contrario
        """
        if not self.connection or not self.cursor:
            print("Error: No hay conexión a la base de datos. Llame a connect() primero.")
            return False
            
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return False
    

    def execute_select(self, query: str, params: tuple = ()) -> List[Tuple[Any]]:
        """
        Ejecuta una consulta SQL con retorno de datos (SELECT).
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            List[Tuple[Any]]: Resultados de la consulta
        """
        if not self.connection or not self.cursor:
            print("Error: No hay conexión a la base de datos. Llame a connect() primero.")
            return []
            
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al ejecutar la consulta SELECT: {e}")
            return []
    

    def create_table(self, table_name: str, columns: dict) -> bool:
        """
        Crea una tabla en la base de datos.
        
        Args:
            table_name: Nombre de la tabla
            columns: Diccionario con nombres de columnas y sus tipos
            
        Returns:
            bool: True si la creación fue exitosa, False en caso contrario
        """
        if not self.connection or not self.cursor:
            print("Error: No hay conexión a la base de datos. Llame a connect() primero.")
            return False
            
        try:
            # Construye la definición de columnas
            columns_definition = ", ".join([f"{col} {data_type}" for col, data_type in columns.items()])
            
            # Crea la consulta SQL
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})"
            
            # Ejecuta la consulta
            self.cursor.execute(query)
            self.connection.commit()
            print(f"Tabla '{table_name}' creada exitosamente.")
            return True
        except sqlite3.Error as e:
            print(f"Error al crear la tabla: {e}")
            return False
    
    
    def insert_data(self, table_name: str, data: dict) -> Optional[int]:
        """
        Inserta datos en una tabla.
        
        Args:
            table_name: Nombre de la tabla
            data: Diccionario con nombres de columnas y valores a insertar
            
        Returns:
            Optional[int]: ID del último registro insertado o None en caso de error
        """
        if not self.connection or not self.cursor:
            print("Error: No hay conexión a la base de datos. Llame a connect() primero.")
            return None
            
        try:
            # Obtiene los nombres de las columnas y los valores
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            values = tuple(data.values())
            
            # Crea la consulta SQL
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            # Ejecuta la consulta
            self.cursor.execute(query, values)
            self.connection.commit()
            
            # Retorna el ID del último registro insertado
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error al insertar datos: {e}")
            return None
    

    def update_data(self, table_name: str, data: dict, condition: str, condition_params: tuple) -> int:
        """
        Actualiza datos en una tabla.
        
        Args:
            table_name: Nombre de la tabla
            data: Diccionario con nombres de columnas y nuevos valores
            condition: Condición WHERE para la actualización
            condition_params: Parámetros para la condición
            
        Returns:
            int: Número de filas afectadas
        """
        if not self.connection or not self.cursor:
            print("Error: No hay conexión a la base de datos. Llame a connect() primero.")
            return 0
            
        try:
            # Construye la parte SET de la consulta
            set_clause = ", ".join([f"{column} = ?" for column in data.keys()])
            values = tuple(data.values()) + condition_params
            
            # Crea la consulta SQL
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
            
            # Ejecuta la consulta
            self.cursor.execute(query, values)
            self.connection.commit()
            
            # Retorna el número de filas afectadas
            return self.cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error al actualizar datos: {e}")
            return 0
    

    def delete_data(self, table_name: str, condition: str = "", condition_params: tuple = ()) -> int:
        """
        Elimina datos de una tabla.
        
        Args:
            table_name: Nombre de la tabla
            condition: Condición WHERE para la eliminación (opcional)
            condition_params: Parámetros para la condición (opcional)
            
        Returns:
            int: Número de filas afectadas
        """
        if not self.connection or not self.cursor:
            print("Error: No hay conexión a la base de datos. Llame a connect() primero.")
            return 0
            
        try:
            # Crea la consulta SQL
            query = f"DELETE FROM {table_name}"
            
            # Agrega la condición si existe
            if condition:
                query += f" WHERE {condition}"
            
            # Ejecuta la consulta
            self.cursor.execute(query, condition_params)
            self.connection.commit()
            
            # Retorna el número de filas afectadas
            return self.cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error al eliminar datos: {e}")
            return 0
    

    def table_exists(self, table_name: str) -> bool:
        """
        Verifica si una tabla existe en la base de datos.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            bool: True si la tabla existe, False en caso contrario
        """
        if not self.connection or not self.cursor:
            print("Error: No hay conexión a la base de datos. Llame a connect() primero.")
            return False
            
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        self.cursor.execute(query, (table_name,))
        return bool(self.cursor.fetchone())
    

    def get_table_info(self, table_name: str) -> List[Tuple[Any]]:
        """
        Obtiene información sobre las columnas de una tabla.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            List[Tuple[Any]]: Información de las columnas
        """
        if not self.connection or not self.cursor:
            print("Error: No hay conexión a la base de datos. Llame a connect() primero.")
            return []
            
        try:
            query = f"PRAGMA table_info({table_name})"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al obtener información de la tabla: {e}")
            return []
