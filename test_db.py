import os
import psycopg2

url = os.getenv("DATABASE_URL")
print("Using:", url)

conn = psycopg2.connect(url)
cur = conn.cursor()
cur.execute("SELECT 1;")
print("Result:", cur.fetchone())
cur.close()
conn.close()
