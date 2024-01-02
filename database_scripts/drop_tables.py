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

sql_commands = (
'''
    DROP TABLE IF EXISTS tags_content
''',
'''
    DROP TABLE IF EXISTS tags_posts
''',
'''
    DROP TABLE IF EXISTS favorites
''',
'''
    DROP TABLE IF EXISTS comments
''',
'''
    DROP TABLE IF EXISTS tags
''',
'''
    DROP TABLE IF EXISTS content
''',
'''
    DROP TABLE IF EXISTS posts
''',
'''
    DROP TABLE IF EXISTS users
''',
'''
    DROP TABLE IF EXISTS roles
''',
)


for command in sql_commands:
    cursor.execute(command)
print("Tables have been dropped successfully !!")

conn.close()