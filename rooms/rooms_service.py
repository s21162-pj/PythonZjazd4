from sqlite3 import Cursor
from typing import Union

import bcrypt

from database.rooms_model import Room, Topic


def create_room(db: Cursor, owner_id: int, password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    out = db.execute("INSERT INTO rooms (owner_id, password) VALUES (?, ?) RETURNING id", (owner_id, hashed_password)).fetchone()[0]
    if not join_room(db, owner_id, out, password):
        raise Exception("Owner could not join the room!")


def get_room(db: Cursor, id: int):
    db_room = db.execute("SELECT * FROM rooms WHERE id=?", (id, )).fetchone()
    if db_room is None:
        return None

    return Room(id=db_room[0], owner_id=db_room[2], password=db_room[1])


def delete_room_by_id(db: Cursor, id: int):
    db.execute("DELETE FROM joined_rooms WHERE room_id=?", (id, ))
    db.execute("DELETE FROM rooms WHERE id=?", (id, ))


def join_room(db: Cursor, user_id: int, room_id: int, password: str) -> bool:
    room = get_room(db, room_id)
    if room is None:
        return False

    if not bcrypt.checkpw(password.encode('utf-8'), room.password.encode('utf-8')):
        return False

    db.execute("INSERT INTO joined_rooms (user_id, room_id) VALUES (?, ?)", (user_id, room_id))
    return True


def joined_room(db: Cursor, user_id: int, room_id: int) -> bool:
    return len(db.execute("SELECT * FROM joined_rooms WHERE room_id = ? AND user_id = ?", (room_id, user_id)).fetchall()) > 0


def get_topic(db: Cursor, room_id: int) -> Union[Topic, None]:
    topic = db.execute("SELECT * FROM topics WHERE room_id = ?", (room_id, )).fetchone()
    if topic is None:
        return None

    return Topic(id=topic[0], room_id=topic[1], value=topic[2])


def get_topic_by_id(db: Cursor, topic_id: int) -> Union[Topic, None]:
    topic = db.execute("SELECT * FROM topics WHERE id = ?", (topic_id,)).fetchone()
    if topic is None:
        return None

    return Topic(id=topic[0], room_id=topic[1], value=topic[2])


def remove_topic(db: Cursor, room_id: int):
    db.execute("DELETE FROM topics WHERE room_id = ?", (room_id, ))


def create_topic(db: Cursor, room_id: int, topic: str):
    db.execute("INSERT INTO topics (room_id, value) VALUES (?, ?)", (room_id, topic))


def add_vote(db: Cursor, topic_id: int, value: float, user_id: int):
    db.execute("INSERT INTO votes (topic_id, value, user_id) VALUES (?, ?, ?)", (topic_id, value, user_id))


def remove_all_votes(db: Cursor, topic_id: int):
    db.execute("DELETE FROM votes WHERE topic_id=?", (topic_id, ))
