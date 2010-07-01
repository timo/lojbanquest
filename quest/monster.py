from nagare import presentation, component, state, var
import models

class Monster(object):
    def __init__(self, gs):
        self.hp = 100
        self.name = "Slime of Vagueness"

@presentation.render_for(Monster)
def monster_render(self, h, binding, *args):
    with h.div(class_="monster"):
        h << self.name
        h << h.br()
        h << h.span("%i hp" % self.hp, class_="hp")
    return h.root

class Monsters(object):
    """This Component holds all Monsters in the room and allows the player
    to select a Monster to attack."""
    def __init__(self, gs):
        self.monsters = []

    def addMonster(self, monster):
        self.monsters.append(monster)

@presentation.render_for(Monsters)
def monsters_render(self, h, binding, *args):
    for mon in self.monsters:
        h << mon

    return h.root

