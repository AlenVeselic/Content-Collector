import os

def getDatabaseOptions():
    return {
                "database":os.environ.get("DATABASE"),
                "user":os.environ.get("DATABASE_USER"),
                "password":os.environ.get("DATABASE_PASSWORD"),
                "host":os.environ.get("DATABASE_HOST"),
                "port": os.environ.get("DATABASE_PORT"),
            }