import time
import sqlite3 
import functools
import hashlib

query_cache = {}

def cache_query(func):
    """Decorator to cache query results based on the SQL query string."""
    @functools.wraps(func)
    def wrapper(conn, query, *args, **kwargs):
        # Create a cache key by hashing the query
        cache_key = hashlib.md5(query.encode()).hexdigest()
        
        # Return cached result if available
        if cache_key in query_cache:
            print("Returning cached result")
            return query_cache[cache_key]
        
        # Execute query and cache the result
        result = func(conn, query, *args, **kwargs)
        query_cache[cache_key] = result
        return result
    return wrapper

def with_db_connection(func):
    """Decorator to handle database connections automatically."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

# Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")
