from __future__ import absolute_import

from nagare import presentation, var, state
from elixir import *
from quest import models
from random import shuffle, randint

class QuestLogin(object):
    def __init__(self):
        self.message = state.stateless(var.Var(""))

    def login(self, username, password, binding):
        po = models.Player.query.get(username())
        if not po:
            self.message("No such user. Try registering instead.")
        elif po.password != password():
            self.message("Login failed.")
        else:
            binding.answer(username())
         

    def register(self, username, password, binding):
        # see if there are duplicate players.
        if models.Player.query.get(username()):
            self.message("A player with that username already exists.")
            return

        # create the player object
        np = models.Player(username = username(), password = password())
        np.position = models.Room.query.get(u"pensi")
        words = list(models.WordCard.query.order_by(models.WordCard.rank).limit(50))
        shuffle(words)

        maxgismu = np.gismubag
        maxcmavo = np.cmavobag

        gismunum = 0
        cmavonum = 0
        for word in words:
            if word.selmaho.selmaho == "GISMU":
                #number = randint(0, min(5, maxgismu - gismunum))
                number = 1
                gismunum += number
            else:
                number = 1
                #number = randint(0, min(5, maxcmavo - cmavonum))
                cmavonum += number
            np.bag.extend([word] * number)

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
