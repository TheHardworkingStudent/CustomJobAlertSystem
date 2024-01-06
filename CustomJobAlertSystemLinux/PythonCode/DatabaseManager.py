
import numpy as np
import sqlite3
import os

class GoogleDatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self, database_file_location):
        # Ensure the directory exists
        directory = os.path.dirname(database_file_location)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Connect to or create the database file at the specified location
        self.conn = sqlite3.connect(database_file_location)

    def close(self):
        #disconnect from database file
        self.conn.close()

    def create_table(self,query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print("Error creating table: "+str(e))
    
    def insert_data(self,table_name, data):
        columns = ', '.join(data.keys())
        placeholders = ':'+', :'.join(data.keys())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, data)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")

    def query_data(self,query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error querying data: {e}")

    def remove_old_listings(self, table_name, days_old):
        # Construct the DELETE SQL query
        delete_query = f"""
        DELETE FROM {table_name}
        WHERE DateScraped <= date('now', '-{days_old} days')
        """
        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute(delete_query)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error removing old listings: {e}")

    def check_hash_exists(self, table_name,hash_value):
        """
        Check if a given hash exists in the database.

        """
        cursor = self.conn.cursor()

        # Use string formatting to include the table name, as it can't be parameterized
        query = f"SELECT EXISTS(SELECT 1 FROM {table_name} WHERE ListHashing=? LIMIT 1)"
        cursor.execute(query, (hash_value,))

        exists = cursor.fetchone()[0]
        
        return exists