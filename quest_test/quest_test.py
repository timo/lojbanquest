from quest.quest import GameSession
from fixtures import *

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
