from quest.models import __metadata__, Room, Door, Player
from fixture import DataSet, SQLAlchemyFixture
from fixture.style import TrimmedNameStyle
from nagare.database import set_metadata, session
from sqlalchemy import MetaData
from datetime import datetime
from hashlib import sha256

__all__ = ["RoomData", "DoorData", "PlayerData", "dbfix", "meta"]

class RoomData(DataSet):
    class start_room:
        name = u"pensi"
        realm = "CVCCV"
    class other_room(start_room):
        name = u"penmi"

class DoorData(DataSet):
    class door_one:
        room_a_id = u"pensi"
        room_b_id = u"penmi"

class PlayerData(DataSet):
    class hero:
        username = u"hero"
        password = sha256(u"hero").hexdigest()
        status = 0
        login = datetime(2010, 1, 2)
        position = RoomData.start_room

meta = __metadata__
set_metadata(meta, "sqlite:///:memory:", True, {})
dbfix = SQLAlchemyFixture(
        env=globals(),
        style=TrimmedNameStyle(suffix="Data"),
        engine = meta.bind)
