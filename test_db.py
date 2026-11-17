import os
import psycopg
from dotenv import load_dotenv

# Load database credentials from the .env file
load_dotenv()

try:
    # Connect to PostgreSQL
    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    ) as conn:

        # Run a test query
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), version();")
            result = cur.fetchone()

            print("Successfully connected to PostgreSQL!")
            print("Database name:", result[0])
            print("PostgreSQL version:", result[1])

except Exception as e:
    print("Database connection failed.")
    print("Error:", e)

#3M9LNlshHNPzNO4ZypFd6m1TZIQ_6eyJSEvBstk5oKjaaxtQf