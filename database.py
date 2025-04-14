# database.py
import sqlite3
import pandas as pd

class DatabaseManager:
    def __init__(self, db_name="headlines.db"):
        self.db_name = db_name
        self.conn = None

    def initialize_database(self):
        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS headlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                headline TEXT,
                date TEXT,
                accessible INTEGER
            )
        ''')
        self.conn.commit()

    def store_headlines(self, headlines):
        cursor = self.conn.cursor()
        for entry in headlines:
            cursor.execute('''
                INSERT INTO headlines (source, headline, date, accessible)
                VALUES (?, ?, ?, ?)
            ''', (entry['source'], entry['headline'], entry['date'], int(entry['accessible'])))
        self.conn.commit()

    def load_headlines(self):
        query = "SELECT * FROM headlines"
        df = pd.read_sql_query(query, self.conn)
        return df

    def has_headlines(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM headlines")
        count = cursor.fetchone()[0]
        return count > 0

    def clear_headlines(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM headlines")
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()
