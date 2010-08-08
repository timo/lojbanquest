from fixtures import *
from quest.roomdisplay import RoomDisplay
from quest.quest import GameSession
from quest.models import Room
from nagare.database import session

import subprocess

import StringIO
import mox


def setup():
    meta.create_all()

def teardown():
    meta.drop_all()

mock = mox.Mox()

@dbfix.with_data(RoomData)
def init_test(data):
    gsm = mock.CreateMock(GameSession)
    mrd = RoomDisplay(u"pensi", gsm)

@dbfix.with_data(RoomData)
def path_test(data):
    class MyPopen:
        def __init__(progargs, stdin=None):
            self.progargs = progargs
            assert stdin == subprocess.PIPE
            self.stdin = StringIO()

        def wait():
            pass

    # replace Popen with MyPopen
    mock.StubOutWithMock(subprocess, "Popen", use_mock_anything=True)
    subprocess.Popen().AndReturn(MyPopen)

    gsm = mock.CreateMock(GameSession)
    mrd = RoomDisplay(u"pensi", gsm)
    mrd.create_map()
