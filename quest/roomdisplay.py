import os
from subprocess import Popen, PIPE
from nagare import presentation, component, state, var
import models
from monster import *
import pkg_resources
import re

class RoomDisplay(object):
    """This class encapsulates many Components that build up the GUI that
    the player uses to 'see' a room and status stuff."""
    def __init__(self, room, gs):
        self.gs = gs
        self.prev = room
        self.enterRoom(room)

    map_cache_path = lambda self, room, frm, typ: pkg_resources.resource_filename("quest", "../cache/%s_%s.%s" % (room, frm, typ))

    def create_map(self):
        img_path = self.map_cache_path(self.room.name, self.prev, "png")
        map_path = self.map_cache_path(self.room.name, self.prev, "map")


        crawl = [self.room]
        add = []
        for i in range(2 if len(self.room.name) == 5 else 1):
            for room in crawl:
                for reached in room.doors:
                    if reached not in crawl and reached not in add:
                        add.append(reached)
            crawl.extend(add)
            add = []

        dotproc = Popen(["neato", "-Tpng", "-o" + img_path, "-Tcmapx_np", "-o" + map_path, "/dev/stdin"], stdin=PIPE)
        dotproc.stdin.write("""graph tersistuhas {
    graph [overlap=false bgcolor="transparent" model=circuit]
    node [shape=none fontsize=7]
    edge [color=grey]
    subgraph cmavo {
        node [fontcolor=blue]\n""")

        for room in crawl:
            if len(room.name) != 5:
                if room in self.room.doors:
                    dotproc.stdin.write("""        "%(name)s" [fontsize=10 URL="goto/%(name)s"]\n""" % {"name": room.name})
                else:
                    dotproc.stdin.write("""        "%(name)s"\n""" % {"name": room.name})


        dotproc.stdin.write("""    } subgraph gismu {
        node[fontcolor=red]\n""")

        for room in self.room.doors:
            dotproc.stdin.write("""        "%(this)s" [fontsize=10 URL="goto/%(this)s"]\n""" % {"this": room.name})


        for room in crawl:
            if room == self.room:
                dotproc.stdin.write("""        "%(name)s" [shape=diamond fontsize=12]\n""" % {"name": room.name})
            elif room.name == self.prev.name:
                dotproc.stdin.write("""        "%(name)s" [shape=egg fontsize=10 URL="goto/%(name)s"]\n""" % {"name": room.name})
            
            for other in room.doors:
                if other.name < room.name and other in crawl:
                    headtail = " "
                    if other.city != room.city:
                        if other.city is not None:
                            headtail += 'arrowhead="inv" '
                        if room.city is not None:
                            headtail += 'arrowtail="inv" '
                        if room.city is not None and other.city is not None:
                            headtail += 'dir="both" '
                        elif room.city is not None:
                            headtail += 'dir="back"'
                        else:
                            headtail += 'dir="forward"'
                    dotproc.stdin.write("""        "%(this)s" -- "%(other)s" [%(ht)s]\n""" % {"this": room.name, "other": other.name, "ht": headtail})
        
        dotproc.stdin.write("""    } }""")

        dotproc.stdin.close()

        dotproc.wait()

        return img_path, map_path

    def get_map_image(self):
        try:
            cached = open(self.map_cache_path(self.room.name, self.prev, "png"), "r")
            return cached.read()
        except IOError:
            pass

        (img_path, _) = self.create_map()

        imgdata = open(img_path, "r").read()

        return imgdata

    def get_map_map(self):
        try:
            cached = open(self.map_cache_path(self.room.name, self.prev, "map"), "r")
            return cached.read()
        except IOError:
            pass

        (_, map_path) = self.create_map()

        mapdata = open(map_path, "r").read()

        return mapdata

    def enterRoom(self, room):
        try:
            self.prev = self.room
        except:
            self.prev = room
        if isinstance(room, models.Room):
            self.room = room
        else:
            self.room = models.Room.get(room)
        
        self.monsters = component.Component(Monsters(self.gs))
        self.monsters.o.addMonster(component.Component(Monster(self.gs)))

        self.gs.enterRoom(self.room)

        print "entered room", self.room

@presentation.render_for(RoomDisplay)
def roomdisplay_render(self, h, binding, *args):
    h << self.monsters
    if self.room.city:
        h << h.p("You are in ", h.span(self.room.name, id="roomname"), " in the city of ", h.span(self.room.city.name, id="cityname"))
    else:
        h << h.p("You are in ", h.span(self.room.name, id="roomname"))
    with h.div():
        h << "Doors:"
        with h.ul():
            h << (h.li(h.a(other.name).action(lambda other=other: self.enterRoom(other))) for other in self.room.doors if other != self.prev)
            h << h.li("Back: ", h.a(self.prev.name).action(lambda other=self.prev: self.enterRoom(self.prev)))

    return h.root

gotorex = re.compile("goto/([^\"]+)")

@presentation.render_for(RoomDisplay, model="map")
def render_map(self, h, binding, *args):
    h << h.img(usemap="tersistuhas").action(self.get_map_image)

    mapstr = self.get_map_map()

    mapobj = h.parse_htmlstring(mapstr)

    for area in mapobj.xpath("//area"):
        roomname = unicode(area.get("href").split("/")[1].replace("&#39;", "'"))
        area.action(lambda other=roomname: self.enterRoom(other))

    h << mapobj
    return h.root
