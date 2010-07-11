from __future__ import absolute_import

from nagare import presentation, var, state
from elixir import *
from quest.models import Player, Room, WordCard, BagEntry
from random import shuffle, randint

class QuestLogin(object):
    def __init__(self):
        self.message = state.stateless(var.Var(""))

    def login(self, username, password, binding):
        po = session.query(Player).get(username())
        if not po:
            self.message("No such user. Try registering instead.")
        elif po.password != password():
            self.message("Login failed.")
        else:
            binding.answer(username())

    def register(self, username, password, binding):
        # see if there are duplicate players.
        if session.query(Player).get(username()):
            self.message("A player with that username already exists.")
            return

        # create the player object
        np = Player(username = username(), password = password())
        np.position = session.query(Room).get(u"pensi")
        session.add(np)

        words = list(session.query(WordCard).order_by(WordCard.rank).limit(50))
        shuffle(words)

        maxgismu = np.gismubag
        maxcmavo = np.cmavobag

        gismunum = 0
        cmavonum = 0
        for word in words:
            if word.selmaho.selmaho == "GISMU":
                number = randint(0, min(5, maxgismu - gismunum))
                gismunum += number
            else:
                number = randint(0, min(5, maxcmavo - cmavonum))
                cmavonum += number
            if number > 0:
                be = BagEntry()
                be.player = np
                be.word = word
                be.count = number
                session.add(be)

        session.add(np)
        session.flush()
        self.login(username, password, binding)

@presentation.render_for(QuestLogin)
def login_form(self, h, binding, *args):
    un = var.Var()
    pwd = var.Var()
    return h.form("Please sign in with your username and password or register a new account.",
                  h.br(),
                  self.message(),
                  h.br(),
                  h.input.action(un),
                  h.input.action(pwd),
                  h.input(type="submit", value="login").action(lambda: self.login(un, pwd, binding)),
                  h.input(type="submit", value="register").action(lambda: self.register(un, pwd, binding))
                  )
