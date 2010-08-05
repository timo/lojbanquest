from __future__ import absolute_import

import hashlib
from datetime import datetime
from random import shuffle, randint

from nagare import presentation, var, state, util, component

from nagare.database import session

from quest.models import Player, Room, WordCard, BagEntry
from quest.cron import login_event
from quest.template import template

class AdminPanel(object):
    def __init__(self):
        self.playerlist = component.Component(PlayerList())

class PlayerList(object):
    def __init__(self):
        self.refresh_list()
        self.room_selected = None

    def refresh_list(self):
        self.players = session.query(Player).all()

    def select(self, room):
        self.room_selected = room

    def teleport(self, player):
        if self.room_selected:
            player.position = self.room_selected
            self.refresh_list()

class LocationHandle(object):
    def __init__(self, player, handler):
        self.player = player
        self.handler = handler

@presentation.render_for(PlayerList)
def playerlist(self, h, comp, *args):
    with h.div(id="playerlist"):
        with h.table():
            with h.tr():
                h << h.th("username")
                h << h.th("status")
                h << h.th("position")
            for p in self.players:
                with h.tr():
                    h << h.td(p.username)
                    h << h.td(p.status)
                    h << h.th(component.Component(LocationHandle(p, self)))

        h << h.a("refresh").action(lambda: self.refresh_list)

    return h.root

@presentation.render_for(LocationHandle)
def locationhandler(self, h, comp, *args):
    h << h.span(self.player.position_name) << " "
    h << h.a("select").action(lambda: self.handler.select(self.player.position)) << " "
    h << h.a("teleport").action(lambda: self.handler.teleport(self.player))

    return h.root

@presentation.render_for(AdminPanel)
def adminpanel(self, h, comp, *args):
    h << self.playerlist

    return h.root
