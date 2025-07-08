import sqlite3
import functools
from datetime import datetime

def log_queries(func):
    """Decorator to log SQL queries with timestamps before executing them."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract query from kwargs or args
        query = kwargs.get('query', args[0] if args else None)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] Executing query: {query}")
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Fetch users while logging the query with timestamp
users = fetch_all_users(query="SELECT * FROM users")
