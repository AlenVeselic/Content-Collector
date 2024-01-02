import psycopg2

from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    database="postgres",
    user=os.environ.get("DATABASE_USER"),
    password=os.environ.get("DATABASE_PASSWORD"),
    host=os.environ.get("DATABASE_HOST"),
    port=os.environ.get("DATABASE_PORT"),
)

conn.autocommit = True

cursor = conn.cursor()

sql = f'''CREATE database {os.environ.get("DATABASE")}'''

cursor.execute(sql)
print("Database has been created successfully !!")

conn.close()