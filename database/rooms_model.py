class Room:
    def __init__(self, id: int, owner_id: int, password: str):
        self.id = id
        self.owner_id = owner_id
        self.password = password


class Topic:
    def __init__(self, id: int, room_id: int, value: str):
        self.id = id
        self.room_id = room_id
        self.value = value