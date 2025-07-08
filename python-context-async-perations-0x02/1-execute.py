import sqlite3

class ExecuteQuery:
    """Reusable context manager for executing queries."""
    
    def __init__(self, db_name, query, params=None):
        self.db_name = db_name
        self.query = query
        self.params = params or ()
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        """Execute the query and return results."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        return self.cursor.fetchall()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

# Usage example
with ExecuteQuery('users.db', "SELECT * FROM users WHERE age > ?", (25,)) as results:
    for row in results:
        print(row)
