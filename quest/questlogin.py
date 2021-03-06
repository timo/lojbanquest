from __future__ import absolute_import

import hashlib
from datetime import datetime
from random import shuffle, randint

from elixir import *
from nagare import presentation, var, state

from quest.models import Player, Room, WordCard, BagEntry
from quest.cron import login_event

class QuestLogin(object):
    def __init__(self):
        self.message = var.Var("")
        state.stateless(self.message)
        self.un = var.Var()
        self.pwd = var.Var()

    def login(self, binding):
        po = session.query(Player).get(self.un())
        
        shao = hashlib.sha256()
        shao.update(self.pwd())
        pwd = unicode(shao.hexdigest())
        del shao
        
        if not po:
            self.message("No such user. Try registering instead.")
            
        elif po.password != pwd:
            self.message("Login failed.")
        else:
            login_event.set()
            po.status = 1 # login the player
            po.login = datetime.now()
            binding.answer(self.un())

    def register(self, binding):
        # see if there are duplicate players.
        if session.query(Player).get(self.un()):
            self.message("A player with that username already exists.")
            return
        elif len(self.un()) < 3:
            self.message("Your nickname must not be shorter than 3 letters.")
            return
        elif len(self.un()) > 16:
            self.message("Your nickname must not be longer than 16 letters.")
            return
        elif " " in self.un():
            self.message("Your nickname must not contain spaces.")
            return

        shao = hashlib.sha256()
        shao.update(self.pwd())
        pwd = shao.hexdigest()
        del shao

        # create the player object
        np = Player(username = self.un(), password = pwd)
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
        self.login(binding)

@presentation.render_for(QuestLogin)
def login_form(self, h, binding, *args):
    return h.form("Please sign in with your username and password or register a new account.",
                  h.br(),
                  self.message(),
                  h.br(),
                  h.input.action(self.un),
                  h.input.action(self.pwd),
                  h.input(type="submit", value="login").action(lambda: self.login(binding)),
                  h.input(type="submit", value="register").action(lambda: self.register(binding))
                  )
