from typing import List, Tuple, Any, Optional

import sqlite3
import os


class DatabaseController:
    """
    Class to manage basic operations with SQLite databases.
    """
    
    def __init__(self, db_file: str) -> None:
        """
        Initializes the database connection.
        
        Args:
            db_file: Path to the database file
        """
        self.db_file = db_file
        self.connection = None
        self.cursor = None
    

    def connect(self) -> bool:
        """
        Establishes the connection with the database.
        
        Returns:
            bool: True if the connection was successful, False otherwise
        """
        try:
            # Checks if the database exists
            db_exists = os.path.exists(self.db_file)
            
            # Connects to the database
            self.connection = sqlite3.connect(self.db_file)
            self.cursor = self.connection.cursor()
            
            if not db_exists:
                print(f"Database '{self.db_file}' created successfully.")
            else:
                print(f"Successful connection to '{self.db_file}'.")
            
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")
            return False
        

    def disconnect(self) -> None:
        """
        Closes the connection to the database.
        """
        if self.connection:
            self.connection.close()
            print("Connection closed.")
            self.connection = None
            self.cursor = None
        

    def execute_query(self, query: str, params: tuple = ()) -> bool:
        """
        Executes an SQL query without returning data (CREATE, INSERT, UPDATE, DELETE).
        
        Args:
            query: SQL query to execute
            params: Parameters for the query (optional)
            
        Returns:
            bool: True if the execution was successful, False otherwise
        """
        if not self.connection or not self.cursor:
            print("Error: There is no connection to the database. Call connect() first.")
            return False
            
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return False
        

    def execute_select(self, query: str, params: tuple = ()) -> List[Tuple[Any]]:
        """
        Executes an SQL query that returns data (SELECT).
        
        Args:
            query: SQL query to execute
            params: Parameters for the query (optional)
            
        Returns:
            List[Tuple[Any]]: Query results
        """
        if not self.connection or not self.cursor:
            print("Error: There is no connection to the database. Call connect() first.")
            return []
            
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error executing SELECT query: {e}")
            return []
        

    def create_table(self, table_name: str, columns: dict) -> bool:
        """
        Creates a table in the database.
        
        Args:
            table_name: Name of the table
            columns: Dictionary with column names and their types
            
        Returns:
            bool: True if the creation was successful, False otherwise
        """
        if not self.connection or not self.cursor:
            print("Error: There is no connection to the database. Call connect() first.")
            return False
            
        try:
            # Build column definitions
            columns_definition = ", ".join([f"{col} {data_type}" for col, data_type in columns.items()])
            
            # Creates the SQL query
            query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition})"
            
            # Executes the query
            self.cursor.execute(query)
            self.connection.commit()
            print(f"Table '{table_name}' created successfully.")
            return True
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
            return False
        
    
    def insert_data(self, table_name: str, data: dict) -> Optional[int]:
        """
        Inserts data into a table.
        
        Args:
            table_name: Name of the table
            data: Dictionary with column names and values to insert
            
        Returns:
            Optional[int]: ID of the last inserted row or None in case of error
        """
        if not self.connection or not self.cursor:
            print("Error: There is no connection to the database. Call connect() first.")
            return None
            
        try:
            # Gets the column names and values
            columns = ", ".join(data.keys())
            placeholders = ", ".join(["?" for _ in data])
            values = tuple(data.values())
            
            # Creates the SQL query
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            # Executes the query
            self.cursor.execute(query, values)
            self.connection.commit()
            
            # Returns the ID of the last inserted row
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")
            return None
        

    def update_data(self, table_name: str, data: dict, condition: str, condition_params: tuple) -> int:
        """
        Updates data in a table.
        
        Args:
            table_name: Name of the table
            data: Dictionary with column names and new values
            condition: WHERE condition for the update
            condition_params: Parameters for the condition
            
        Returns:
            int: Number of rows affected
        """
        if not self.connection or not self.cursor:
            print("Error: There is no connection to the database. Call connect() first.")
            return 0
            
        try:
            # Constructs the SET clause of the query
            set_clause = ", ".join([f"{column} = ?" for column in data.keys()])
            values = tuple(data.values()) + condition_params
            
            # Creates the SQL query
            query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
            
            # Executes the query
            self.cursor.execute(query, values)
            self.connection.commit()
            
            # Returns the number of rows affected
            return self.cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error updating data: {e}")
            return 0
        

    def delete_data(self, table_name: str, condition: str = "", condition_params: tuple = ()) -> int:
        """
        Deletes data from a table.
        
        Args:
            table_name: Name of the table
            condition: WHERE condition for deletion (optional)
            condition_params: Parameters for the condition (optional)
            
        Returns:
            int: Number of rows affected
        """
        if not self.connection or not self.cursor:
            print("Error: There is no connection to the database. Call connect() first.")
            return 0
            
        try:
            # Creates the SQL query
            query = f"DELETE FROM {table_name}"
            
            # Adds the condition if it exists
            if condition:
                query += f" WHERE {condition}"
            
            # Executes the query
            self.cursor.execute(query, condition_params)
            self.connection.commit()
            
            # Returns the number of rows affected
            return self.cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error deleting data: {e}")
            return 0
        

    def table_exists(self, table_name: str) -> bool:
        """
        Checks if a table exists in the database.
        
        Args:
            table_name: Name of the table
            
        Returns:
            bool: True if the table exists, False otherwise
        """
        if not self.connection or not self.cursor:
            print("Error: There is no connection to the database. Call connect() first.")
            return False
            
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        self.cursor.execute(query, (table_name,))
        return bool(self.cursor.fetchone())
        

    def get_table_info(self, table_name: str) -> List[Tuple[Any]]:
        """
        Gets information about the columns of a table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List[Tuple[Any]]: Column information
        """
        if not self.connection or not self.cursor:
            print("Error: There is no connection to the database. Call connect() first.")
            return []
            
        try:
            query = f"PRAGMA table_info({table_name})"
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting table information: {e}")
            return []
