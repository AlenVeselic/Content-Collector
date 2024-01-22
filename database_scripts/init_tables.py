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
sql_commands = (f'''
    CREATE TABLE IF NOT EXISTS tags(
    id SERIAL PRIMARY KEY,  
    created_on TIMESTAMPTZ NOT NULL DEFAULT now(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(255) NOT NULL
    )
''',
'''
    CREATE TABLE IF NOT EXISTS content(
    id SERIAL PRIMARY KEY,
    original_directory VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    original_title VARCHAR(255),
    
    currentLocation VARCHAR(255) NOT NULL,
    source VARCHAR(255),

    scraped_on TIMESTAMPTZ,
    created_on TIMESTAMPTZ NOT NULL DEFAULT now()

    )
''',
'''
    CREATE TABLE IF NOT EXISTS roles(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL

    )
''',
'''
    CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    role_id INT NOT NULL,
    username VARCHAR(255) NOT NULL,
    FOREIGN KEY (role_id)
    REFERENCES roles(id)
    ON UPDATE CASCADE ON DELETE CASCADE
    )
''',
'''
    CREATE TABLE IF NOT EXISTS posts(
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_on TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_on TIMESTAMPTZ,
    hidden BOOLEAN DEFAULT FALSE,

    views BIGINT NOT NULL DEFAULT 0,
    likes BIGINT NOT NULL DEFAULT 0,
    dislikes BIGINT NOT NULL DEFAULT 0,

    uploaded_by INT NOT NULL,

    FOREIGN KEY (uploaded_by)
    REFERENCES users(id)
    ON UPDATE CASCADE ON DELETE CASCADE

    )
''',

'''
    CREATE TABLE IF NOT EXISTS tags_content(
    content_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY(content_id , tag_id),
    FOREIGN KEY(content_id)
        REFERENCES content(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(tag_id)
        REFERENCES tags(id)
        ON UPDATE CASCADE ON DELETE CASCADE
    )
''',

'''
    CREATE TABLE IF NOT EXISTS tags_posts(
    post_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY(post_id , tag_id),
    FOREIGN KEY(post_id)
        REFERENCES posts(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(tag_id)
        REFERENCES tags(id)
        ON UPDATE CASCADE ON DELETE CASCADE
    )

''',
'''
    CREATE TABLE IF NOT EXISTS favorites(
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY(post_id , user_id),
    FOREIGN KEY(post_id)
        REFERENCES posts(id)
        ON UPDATE CASCADE ON DELETE CASCADE,
    FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON UPDATE CASCADE ON DELETE CASCADE
    )
''',
'''
    CREATE TABLE IF NOT EXISTS comments(
    id SERIAL PRIMARY KEY,
    post_id INT NOT NULL,
    contents TEXT NOT NULL,
    hidden BOOL NOT NULL DEFAULT FALSE,

    FOREIGN KEY (post_id)
    REFERENCES posts(id)
    ON UPDATE CASCADE ON DELETE CASCADE

        
    )
'''
)

for command in sql_commands:
    cursor.execute(command)
print("Tables have been created successfully !!")

conn.close()