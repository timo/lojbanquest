from __future__ import absolute_import, with_statement

from nagare import presentation, component, comet, ajax
from nagare.database import session

from quest.models import Room, Player

def poke(target):
    try:
        comet.channels.send(target, "poke")
    except Exception, e:
        print "poke %s failed with %r" % (target, e)
        return False
    return True

def send_to(target, message):
    if isinstance(target, Room):
        for player in target.players:
            if player.username == message.split()[0]:
                print "skipped delivery to self"
                continue
            try:
                comet.channels.send(player.username, message)
            except Exception, e: print "failed to send to comet channel", player.username, e
            try:
                messages[player.username].append(message)
            except Exception, e: print "failed to put message in mailbox", player.username, e
        return
    elif isinstance(target, Player):
        msgtarget = target.username
    elif isinstance(target, basestring):
        msgtarget = target
    else:
        raise ValueError("eventlog.send_to expected a Room, Player or basestring, got %r (%s) instead" % (target, target.__class__))

    if msgtarget == message.split()[0]:
        print "skipped delivery to self"
        return
    try:
        comet.channels.send(msgtarget, message)
    except: print "failed to send to comet channel", msgtarget
    try:
        messages[msgtarget].append(message)
    except: print "failed to put message in mailbox", msgtarget

@ajax.javascript
def append(msg):
    if msg == "poke":
        return

    li = document.createElement('li')
    li.appendChild(document.createTextNode(msg))

    msgs = document.getElementById('eventlog')
    if not msgs.childNodes.length:
        msgs.appendChild(li)
    else:
        msgs.insertBefore(li, msgs.firstChild)

    players = document.getElementById("players")

    msgsplit = msg.split(" ")

    action = msgsplit.pop()
    player = msgsplit.pop()

    if action == "left":
        player = document.getElementById("player_" + player)
        players.removeChild(player)
    elif action == "entered":
        newplayer = document.createElement('li')
        newplayer.appendChild(document.createTextNode(player))
        newplayer.setAttribute("id", "player_" + player)
        players.appendChild(newplayer)

messages = {}

class Log(object):
    def __init__(self, playername):
        self.chanid = playername
        messages[self.chanid] = []

        comet.channels.create(self.chanid, append.name)

@presentation.render_for(Log)
def render_log(self, h, *args):
    h.head << h.head.script(ajax.py2js(append, h))

    h << component.Component(comet.channels[self.chanid])
    with h.ul(id="eventlog"):
        for message in messages[self.chanid]:
            h << h.li(message)

    return h.root
