#!/usr/bin/python
import sys, os
from pysqlite2 import dbapi2 as sqlite
from subprocess import check_output, CalledProcessError
import glob

try:
    db = sys.environ["dbpath"]
except:
    db = "/home/timo/stackless/lojbanquest/data/quest.db"

if sys.argv[1:]:
    if sys.argv[1] == "config":
        print "graph_title lojbanquest players"
        print "graph_category lojbanquest"
        print "graph_scale no"
        print "graph_vlabel Count"
        print "players.label Players"
        print "online.label Playing"
        sys.exit(0)

# first, see if lojbanquest is online
try:
    ps_out = check_output(["ps", "a"])
except CalledProcessError, e:
    print "could not call 'ps a':", e, repr(e)
    sys.exit(1)
lq_online = all(map(ps_out.__contains__, ["nagare-admin", "serve", "quest"]))

c = sqlite.connect(db)
cur = c.cursor()

numplayers = c.execute("SELECT count() FROM Player").fetchone()[0]
numonline = c.execute("SELECT count() FROM Player WHERE status > 0").fetchone()[0]

cur.close()
c.close()

if lq_online:
    print "players.value %i" % (numplayers,)
    print "online.value %i" % (numonline,)
else:
    # show a gap for downtime
    print "players.value U"
    print "online.value U"
