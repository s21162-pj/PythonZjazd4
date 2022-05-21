import sqlite3


def get_database(path) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys = ON;")
    return db


def initialize(db: sqlite3.Connection):
    print("Dropping db")
    db.isolation_level = None
    for call in ["PRAGMA writable_schema = 1;",
    "DELETE FROM sqlite_master;",
    "PRAGMA writable_schema = 0;",
    "VACUUM;",
    "PRAGMA integrity_check;"]:
        db.execute(call)

    db.isolation_level = ''
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE users (
        id integer PRIMARY KEY,
        login text NOT NULL UNIQUE,
        password text NOT NULL
    )
    """)

    cursor.execute('''
        CREATE TABLE rooms (
            id integer PRIMARY KEY,
            password text NOT NULL,
            owner_id integer NOT NULL,
            FOREIGN KEY (owner_id) REFERENCES users (id) 
        )
    ''')

    cursor.execute('''
        CREATE TABLE joined_rooms (
            id integer PRIMARY KEY,
            room_id integer NOT NULL,
            user_id integer NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id) ,
            FOREIGN KEY (room_id) REFERENCES rooms (id) ,
            UNIQUE(room_id, user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE topics (
            id integer PRIMARY KEY,
            room_id integer NOT NULL UNIQUE,
            value text NOT NULL,
            FOREIGN KEY (room_id) REFERENCES rooms (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE votes (
            id integer PRIMARY KEY,
            topic_id integer NOT NULL,
            user_id integer NOT NULL,
            value float NOT NULL,
            FOREIGN KEY (topic_id) REFERENCES topics (id),
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE (user_id, topic_id)
        )
    ''')