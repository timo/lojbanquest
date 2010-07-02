from __future__ import absolute_import

from quest.models import *
import nagare.database
import re
from sqlalchemy import or_, and_
import sqlalchemy.orm.exc 
import random

roomseed = u"pinka"

# citymap: city->rooms
# reverse citymap: room->city
def makeWorldGraph(outfile = "world.dot", limiter = None, citymap = {}, reversecitymap = {}):
    if limiter:
        print outfile, [a.name for a in limiter]
    else:
        print outfile
    out = open(outfile, "w")
    out.write("""graph "Tersistu'as" {
  graph [overlap=true]
  node [shape=none fontsize=10]
  edge [color=grey]\n""")

    if citymap:
        if not reversecitymap:
            for k, v in citymap.iteritems():
                for room in v:
                   reversecitymap[room] = k

        for k, v in citymap.iteritems():
            out.write("""    subgraph "cluster_%s" {
            node [fontcolor=black shape=round fontsize=14]\n""" % k)
            
            for room in v:
                out.write('         "%s"\n' % room.name)

            out.write("""    }\n""")

    out.write("""  subgraph "cmavo" {
    node [fontcolor=blue]\n""")

    for room in Room.query.order_by(Room.name):
        if len(room.name) == 5: continue
        if limiter and room not in limiter: continue
        out.write('    "%s"\n' % room.name)

    out.write("""}
  subgraph "gismu" {
    node [fontcolor=red]\n""")

    for room in Room.query.order_by(Room.name):
        if len(room.name) != 5: continue
        if limiter and room not in limiter: continue
        if len(room.doors) == 0:
            out.write('    "%s"' % room.name)
        for other in room.doors:
            if limiter and other not in limiter: continue
            if other.name < room.name:
                out.write("""    "%s" -- "%s"\n""" % (room.name, other.name))

    out.write("""}  subgraph "cmavo" {
    node [fontcolor=blue]\n""")

    for room in Room.query.order_by(Room.name):
        if len(room.name) == 5: continue
        if limiter and room not in limiter: continue
        if len(room.doors) == 0:
            out.write('    "%s"\n' % room.name)
        for other in room.doors:
            if limiter and other not in limiter: continue
            if other.name < room.name:
                out.write("""    "%s" -- "%s"\n""" % (room.name, other.name))

    out.write("""  }\n
}""")

def likeLevenOne(name):
    return and_(or_(*(Room.name.like("%s_%s" % (name[:i], name[i+1:])) for i in range(len(name)))),
                Room.name != name)

l2p = ["__cde", "_b_de", "_bc_e", "_bcd_",
       "a__de", "a_c_e", "a_cd_",
       "ab__e", "ab_d_",
       "abc__"]

def makeLeven2Poss():
    global l2p
    np = []
    for p in l2p:
        s = ""
        for c in p:
            if c != "_":
                s += "%(" + c + ")s"
            else:
                s += "_"
        np.append(s)
    l2p = np

makeLeven2Poss()

def likeLevenTwo(name):
    return and_(or_(*(Room.name.like(a % dict(zip("abcde", name))) for a in l2p)))

def cmavoStep(name):
    seq1 = list("uieaoui")
    seq2 = [list(x) for x in ["xptfsckxp", "gbdvzjgb", "nmn", "rlr"]]
    pairs = {u'p': u'b', u'b': u'p',
             u't': u'd', u'd': u't',
             u'k': u'g', u'g': u'k',
             u'f': u'v', u'v': u'f',
             u'c': u'j', u'j': u'c',
             u's': u'z', u'z': u's'}

    isstep = lambda seq, x, y: seq.index(x) - seq.index(y) in [-1, 1]

    addapore = re.compile("^([bcdfgjklmnoprstuvxz]?[aeiouy])([aeiouy])$")

    others = []
    
    # rule 1: add or omit i at the end
    if name[-1] == "i":
        others.append(name[:-1])
    else:
        others.append(name + "i")

    # rule 2: adds/omits an apostrophe
    if "'" in name:
        others.append(name.replace("'", ""))
    else:
        try:
            mat = addapore.match(name)
            others.append(mat.group(1) + "'" + mat.group(2))
        except: pass

    # rule 3: adds/omits p at the beginning
    if name[0] == "p":
        others.append(name[1:])
    else:
        others.append("p" + name)

    # rule 4: steps the last letter among seq1
    try:
        others.append(name[:-1] + seq1[seq1.index(name[-1]) + 1])
    except: pass

    # rule 5: steps the first letter among one of seq2
    for seq in seq2:
        if name[0] in seq:
            others.append(seq[seq.index(name[0]) + 1] + name[1:])

    # rule 6: switches the consonant from voiced to unvoiced or vice versa
    try:
        if len(name) > 1 and name[0] in pairs:
            others.append(pairs[name[0]] + name[1:])
    except Exception, e:
        print
        print "found an exception while making connections by switching voiced/unvoiced"
        print e
        print
        raise

    return and_(or_(*(Room.name == other for other in others)),
                Room.name != name)

def populate_valsi():
    print "loading wordlists"
    print

    print "gismu and rafsi-cmavo:"

    try:
        lines = open("data/gismu.txt").readlines()[1:]
    except:
        lines = open("../data/gismu.txt").readlines()[1:]

    num = 0
    count = len(lines)

    def make_or_get_selmaho(selmaho):
        try:
            sm = Selmaho.query.filter_by(selmaho = selmaho).one()
        except sqlalchemy.orm.exc.NoResultFound:
            sm = Selmaho()
            sm.selmaho = selmaho
            sm.milti = 1
            session.add(sm)

        return sm

    for valsi in lines:
        num += 1

        val = unicode(valsi[0:6].strip())
        gloss = unicode(valsi[20:42]).strip()
        try:
            defi = unicode(defire.match(valsi[62:159]).group(1)).strip()
        except:
            defi = unicode(valsi[62:195]).strip()

        rafsi = unicode(valsi[7:20]).strip()

        if len(val) != 5:
            smt = None
        else:
            smt = u"GISMU"

        print "\r(% 5i/% 5i) %s" % (num, count, val),
        wc = WordCard()
        wc.word = val
        wc.gloss = gloss
        wc.definition = defi
        wc.rafsi = rafsi

        sm = None
        if smt:
            wc.selmaho = make_or_get_selmaho(smt)
        else:
          wc.selmaho = None

        session.add(wc)

    print
    print "rafsi-less cmavo and selma'o of rafsi-cmavo"
    print

    try:
        lines = open("data/cmavo.txt").readlines()[1:]
    except:
        lines = open("../data/cmavo.txt").readlines()[1:]

    count= len(lines)
    num = 0

    for valsi in lines:
        num += 1
        if "*" in valsi[12:20]:
            continue
        
        print "\r(% 5i/% 5i) %s" % (num, count, val),

        val = unicode(valsi[0:11].strip())
        if val[0] == ".": val = val[1:]

        selmaho = unicode(valsi[11:20].strip())
        
        oldval = WordCard.query.filter_by(word = val)

        if oldval.count() != 0:
            ov = oldval.one()
            ov.selmaho = make_or_get_selmaho(selmaho)
            session.add(ov)
        else:
            gloss = unicode(valsi[20:62].strip())
            defi = unicode(valsi[62:168].strip())
            rafsi = u""

            wc = WordCard()
            wc.word = val
            wc.gloss = gloss
            wc.definition = defi
            wc.selmaho = make_or_get_selmaho(selmaho)
            wc.rafsi = rafsi
            session.add(wc)

count = 0
def make_rooms():
    global count
    num = 0
    count = WordCard.query.count()

    for gismu in WordCard.query.order_by(WordCard.word):
        num += 1
        # only print every 10th line
        if num % 10 == 0:
            print "\r(% 5i/% 5i) %s" % (num, count, gismu.word),

        room = Room()
        room.name = gismu.word

def connect_rooms():
    global count
    num = 0

    for theroom in Room.query.order_by(Room.name):
        num += 1
        
        rafsi = WordCard.query.filter(WordCard.word == theroom.name).one().rafsi.split()
        
        if num % 10 == 0: # only every 10th one.
            print "\r(% 5i/% 5i) %s - %s                          " % (num, count, theroom.name, rafsi),

        # is this a gismu or is this a rafsi?


        #if WordCard.query.filter(WordCard.word == theroom.name).one().selmaho.selmaho == "GISMU":
        if len(theroom.name) == 5:
            adjacentrooms = Room.query.filter(or_(likeLevenOne(theroom.name),
                                                  Room.name.in_(rafsi)))
        else:
            adjacentrooms = Room.query.filter(cmavoStep(theroom.name))

        for other in adjacentrooms:
            if other not in theroom.doors:
                theroom.doors.append(other)
            if theroom not in other.doors:
                other.doors.append(theroom)

def connect_other_continent(rooms):
    print
    print "making other continent"
    print

    count = len(rooms)

    num = 0
    for theroom in rooms:
        if len(theroom.name) != 5:
            continue
        
        if num % 10 == 0: # only every 10th one.
            print "\r(% 5i/% 5i) %s                               " % (num, count, theroom.name),
        
        adjacentrooms = Room.query.filter(likeLevenTwo(theroom.name))
        
        for other in adjacentrooms:
            if other not in rooms: continue # only intracontinental connections allowed
            if other not in theroom.doors:
                theroom.doors.append(other)
            if theroom not in other.doors:
                other.doors.append(theroom)

        num += 1
    print "other continent has %d rooms." % num

known = []
def prune_rooms(roomseeds):
    global known
    known = []
    look_at = [Room.get_by(name = roomseed) for roomseed in roomseeds]

    while len(look_at) > 0:
        ther = look_at.pop()
        for other in ther.doors:
            if other not in known:
                look_at.append(other)

        known.append(ther)

    toprune = []

    for theroom in Room.query.order_by(Room.name):
        if theroom not in known:
            toprune.append(theroom)

    return toprune

def delete_rooms(rooms):
    for room in rooms:
        session.delete(room)

def cut_doors(maxdoornum):
    global known
    weight = lambda num: max((9 - num) ** 2, 1)

    count = len(known)
    num = 0

    killedcount = 0

    for theroom in Room.query.order_by(Room.name):
        num += 1
        dnum = len(theroom.doors)
        
        print "\r(% 5i/% 5i) %s (%i)      " % (num, count, theroom.name, dnum),

        if dnum > maxdoornum:
            rooms = []
            for other in theroom.doors:
                # never kick gismu -> cmavo doors
                if (len(other.name) == 5) == (len(theroom.name) == 5):
                    rooms.append([other] * weight(len(other.doors)))

            random.shuffle(rooms)
            # play russian roulette
            kills = set()
            while len(kills) < dnum - maxdoornum and rooms:
                kills = kills | set(rooms.pop())
                
            killedcount += len(kills)

            for k in kills:
                try:
                    if k != theroom:
                        k.doors.remove(theroom)
                        theroom.doors.remove(k)
                except Exception, e:
                    print
                    print e
                    print theroom.name
                    print k.name
                    print
    print "killed %d connections in total." % killedcount

def generate_world():
    print "Creating rooms from WordCards..."
    print

    make_rooms()

    print
    print
    print "Connecting rooms."
    print

    connect_rooms()

    print
    print
    print "Seeding island from '%s'." % (roomseed, )
    print

    connect_other_continent(prune_rooms([roomseed]))

    maxdoornum = 5
    print
    print
    print "Cut number of doors down to %i per room..." % maxdoornum
    print

    cut_doors(maxdoornum)

    print
    print "connecting the two continents"
    print

    bridge = Room.get("y'y")
    p1 = Room.get("kadno")
    p2 = Room.get("frica")
    bridge.doors.extend([p1, p2])
    p1.doors.append(bridge)
    p2.doors.append(bridge)

    print
    print "finding left-over unreachable rooms"
    print

    pruned = prune_rooms([roomseed])
    print len(pruned), [room.name for room in pruned]

    print
    print "Generating graphviz file."
    print

    makeWorldGraph()

def populate_db():
    defire = re.compile("(.*?);")
    print "will now populate the database."

    print "First step: valsi"
    populate_valsi()

    print "Second step: the world"
    generate_world()

    print "third step: find some cities"
    cities = []
    randrms = random_rooms()
    maxsize = 0
    try:
        while maxsize < 70:
            room = randrms.next()
            if len(room.name) == 5:
                city = find_city(room.name)
                if len(city) > maxsize:
                    maxsize = len(city)
                if len(city) > 15:
                    cities.append((room.name, city))
    except StopIteration:
        print "all rooms exhausted"

    cities.sort(key=lambda c: len(c[1]))
    cities.reverse()
    
    print "separating cities"
    exhaustedrooms = []
    acceptedcities = []
    for city in cities:
        overlap = 0
        for room in city[1]:
            if room in exhaustedrooms:
                overlap += 1

        if overlap > 0:
            continue

        exhaustedrooms.extend(city[1])
        acceptedcities.append(city)

        cityObj = City()
        cityObj.name = city[0]
        session.add(cityObj)

        for room in city[1]:
            room.city = cityObj

    print "\n".join(["%d - %s" % (len(c[1]), c[0]) for c in acceptedcities])

    makeWorldGraph(outfile="world_cities.dot", citymap=dict(acceptedcities))

def random_rooms():
    num = Room.query.count()
    nums = range(num)
    random.shuffle(nums)
    for num in nums:
        yield Room.query.offset(num).first()

class CityCrawler(object):
    def __init__(self, startroom):
        self.visitedrooms = [Room.get_by(name=startroom)]

    def crawl(self):
        self.step_one()
        self.step_one()
        while self.add_rooms() > 0:
            self.follow_corridors()
        return self.visitedrooms

    def step_one(self):
        additions = []
        for room in self.visitedrooms:
            for croom in room.doors:
                if croom not in additions and croom not in self.visitedrooms:
                    additions.append(croom)
        self.visitedrooms.extend(additions)
        self.follow_corridors()

    def follow_corridors(self):
        for room in self.visitedrooms:
            if len(room.doors) == 1:
                if room.doors[0] not in self.visitedrooms:
                    self.visitedrooms.append(room.doors[0])

    def add_rooms(self, minter=2): # "minimum interconnections"
        rooms_added = 0
        for vroom in self.visitedrooms:
            others = vroom.doors
            looked_at = 0
            for o in others:
                if o in self.visitedrooms:
                    continue
                if len(o.name) != 5:
                    continue
                looked_at += 1
                cons = sum([int(otr in self.visitedrooms) for otr in o.doors])
                if cons >= minter:
                    self.visitedrooms.append(o)
                    rooms_added += 1

        return rooms_added

def find_city(startroom = "pinka"):
    crawler = CityCrawler(startroom)
    rooms = crawler.crawl()
    return rooms
