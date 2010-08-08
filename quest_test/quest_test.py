from quest.quest import GameSession
from quest.models import __metadata__, Room, Door, Player
from fixture import DataSet, SQLAlchemyFixture
from fixture.style import TrimmedNameStyle
from hashlib import sha256
from datetime import datetime
from nagare.database import set_metadata, session
from sqlalchemy import MetaData

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

def setup():
    meta.create_all()

def teardown():
    meta.drop_all()

def start_test():
    gs = GameSession()

@dbfix.with_data(PlayerData, RoomData)
def login_test(data):
    gs = GameSession()
    
    gs.loginManager.o.un(u"hero")
    gs.loginManager.o.pwd(u"hero")
    gs.loginManager.o.login(gs.loginManager)
    
    assert gs.model() == "game", gs.model()

@dbfix.with_data(RoomData)
def register_test(data):
    gs = GameSession()
    gs.loginManager.o.un(u"villain")
    gs.loginManager.o.pwd(u"rule the world!")
    gs.loginManager.o.register(gs.loginManager)
    assert gs.model() == "game", gs.model()
    gs.logout()
    assert gs.model() == "login", gs.model()

@dbfix.with_data(PlayerData)
def login_fail(data):
    gs = GameSession()
    
    gs.loginManager.o.un(u"hero")
    gs.loginManager.o.pwd(u"wrong pwd")
    gs.loginManager.o.login(gs.loginManager)
    assert gs.model() == "login", gs.model()

    gs.loginManager.o.un(u"random")
    gs.loginManager.o.pwd(u"wrong pwd")
    gs.loginManager.o.login(gs.loginManager)
    assert gs.model() == "login", gs.model()
