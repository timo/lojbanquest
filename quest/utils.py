from models import *
import nagare.database
import re
from sqlalchemy import or_, and_
import sqlalchemy.orm.exc 
import random

roomseed = "pinka"

def makeWorldGraph():
    out = open("world.dot", "w")
    out.write("""graph "Tersistu'as" {
  graph [overlap=true]
  node [shape=none fontsize=10]
  edge [color=grey]
""")

    out.write("""  subgraph "cmavo" {
    node [fontcolor=blue]\n""")

    for room in Room.query.order_by(Room.name):
        if len(room.name) == 5: continue
        if len(room.doors) == 0:
            out.write('    "%s"' % room.name)
        for other in room.doors:
            if other.name < room.name:
                out.write("""    "%s" -- "%s"\n""" % (room.name, other.name))

    out.write("""}
  subgraph "gismu" {
    node [fontcolor=red]\n""")

    for room in Room.query.order_by(Room.name):
        if len(room.name) != 5: continue
        if len(room.doors) == 0:
            out.write('    "%s"' % room.name)
        for other in room.doors:
            if other.name < room.name:
                out.write("""    "%s" -- "%s"\n""" % (room.name, other.name))

    out.write("""  }\n
}""")

def likeLevenOne(name):
    return and_(or_(*(Room.name.like("%s_%s" % (name[:i], name[i+1:])) for i in range(len(name)))),
                Room.name != name)

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
        others.append(pairs[name[0]] + name[1:])
    except: pass

    return and_(or_(*(Room.name == other for other in others)),
                Room.name != name)

def populate_valsi():
    print "loading wordlists"
    print

    print "gismu and rafsi-cmavo:"

    lines = open("gismu.txt").readlines()[1:]

    num = 0
    count = len(lines)

    def make_or_get_selmaho(selmaho):
        try:
            sm = session.query(Selmaho).filter_by(selmaho = selmaho).one()
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

    lines = open("cmavo.txt").readlines()[1:]

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

def make_rooms():
    num = 0
    count = WordCard.query.count()

    for gismu in WordCard.query.order_by(WordCard.word):
        num += 1
        print "\r(% 5i/% 5i) %s" % (num, count, gismu.word),

        room = Room()
        room.name = gismu.word

def connect_rooms():
    num = 0

    for theroom in Room.query.order_by(Room.name):
        num += 1
        
        rafsi = WordCard.query.filter(WordCard.word == theroom.name).one().rafsi.split()
        
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

def prune_rooms(roomseeds):
    known = []
    look_at = [Room.get_by(name = roomseed) for roomseed in roomseeds]

    while len(look_at) > 0:
        ther = look_at.pop()
        for other in ther.doors:
            if other not in known:
                look_at.append(other)

        known.append(ther)

    for theroom in Room.query.order_by(Room.name):
        if theroom not in known:
            session.delete(theroom)

def cut_doors(maxdoornum):
    weight = lambda num: max((9 - num) ** 2, 1)

    count = len(known)

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

            for k in kills:
                k.doors.remove(theroom)
                theroom.doors.remove(k)

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

    prune_rooms([roomseed])

    maxdoornum = 5
    print
    print
    print "Cut number of doors down to %i per room..." % maxdoornum
    print

    cut_doors(maxdoornum)

    print
    print "Generating graphviz file."
    print

    makeWorldGraph()

def populate_db():
    defire = re.compile("(.*?);")
    print "will now populate the database."

    print "First step: valsi"
    populate_valsi()

