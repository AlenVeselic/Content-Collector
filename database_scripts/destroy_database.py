import psycopg2

from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    database=os.environ.get("DATABASE"),
    user=os.environ.get("DATABASE_USER"),
    password=os.environ.get("DATABASE_PASSWORD"),
    host=os.environ.get("DATABASE_HOST"),
    port=os.environ.get("DATABASE_PORT"),
)

conn.autocommit = True

cursor = conn.cursor()

sql = '''Drop database Content_Collection'''

cursor.execute(sql)
print("Database has been destroyed successfully !!")

conn.close()