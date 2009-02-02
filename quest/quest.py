from __future__ import with_statement

import os
from nagare import presentation, component, state
from nagare.namespaces import xhtml

from nagare.var import Var

import models
import random

class Monster(object):
    def __init__(self):
        self.hp = 100
        self.name = "Slime of Ambiguity"

@presentation.render_for(Monster)
def monster_render(self, h, binding, *args):
    with h.div(class_="monster"):
        h << self.name
        h << h.br()
        h << h.span("%i hp" % self.hp, class_="hp")
    return h.root

class Monsters(object):
    def __init__(self):
        self.monsters = []

    def addMonster(self, monster):
        self.monsters.append(monster)

@presentation.render_for(Monsters)
def monsters_render(self, h, binding, *args):
    for mon in self.monsters:
        h << mon

    return h.root

class Wordbag(object):
    def __init__(self):
        self.diceWords()

    def diceWords(self):
        self.words = {}

        words = list(models.WordCard.query.order_by(models.WordCard.word))
        sum = 0
        while sum < 100:
            num = random.randint(1, 10)
            self.words[random.choice(words)] = num
            sum += num

    def useWord(self, wo):
        wc = [wrd for wrd in self.words if wrd.word == wo][0]
        self.words[wc] -= 1
        if self.words[wc] == 0:
            del self.words[wc]

class Player(object):
    def __init__(self, name = "la timos"):
        self.name = name
        self.hp = 100
        self.wordbag = state.stateless(Wordbag())

    def changeHp(self, offset):
        self.hp += offset

@presentation.render_for(Player)
def player_render(self, h, binding, *args):
    with h.div(class_ = "playerbox"):
        h << h.h1(self.name)
        with h.span():
           h << "You currently have "
           h << h.span(self.hp, id="hp")
           h << " health points."
           h << h.a("--").action(lambda: self.changeHp(-1))
           h << h.a("++").action(lambda: self.changeHp(+1))

    return h.root

@presentation.render_for(Player, model="wordbag")
def wordbag_render(self, h, binding, *args):
    if len(self.wordbag.words) > 0:
        with h.div(class_="wordbag"):
            h << {"style": "-moz-column-count:5;" }
            h << h.a("re-fill bag.").action(self.wordbag.diceWords)
            with h.ul():
                for wo, ct in self.wordbag.words.iteritems():
                    with h.li():
                        h << h.span(ct, class_="count")
                        h << h.a(" " + wo.word).action(lambda wo=wo: self.wordbag.useWord(wo.word))
    else:
        with h.div(class_="wordbag"):
            h << "Woops. No words :("
    
    return h.root

class Quest(object):
    def __init__(self):
        self.playerBox = component.Component(Player("la timos"))
        self.monsters = Monsters()
        self.monsters.addMonster(component.Component(Monster()))
        self.monstersC = component.Component(self.monsters)

@presentation.render_for(Quest)
def render(self, h, *args):
    h << h.h1("Welcome to LojbanQuest!")
    h << self.playerBox.render(xhtml.AsyncRenderer(h))
    h << self.playerBox.render(xhtml.AsyncRenderer(h), model="wordbag")
    h << self.monstersC
    return h.root

# ---------------------------------------------------------------

app = Quest
