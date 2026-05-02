import psycopg2
from psycopg2 import sql

def check_postgres():
    try:
        # Try to connect to default 'postgres' database
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="localhost"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if lifestream exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'lifestream'")
        exists = cur.fetchone()
        
        if not exists:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier("lifestream")))
            print("Database 'lifestream' created successfully.")
        else:
            print("Database 'lifestream' already exists.")
            
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_postgres()
