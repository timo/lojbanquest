from __future__ import with_statement

import threading
import time
import models
import eventlog
from datetime import datetime, timedelta

from nagare.database import session

login_event = threading.Event()
stop_osw_event = threading.Event()

osw_lock = threading.Lock()

class OfflineSenseWorker(threading.Thread):
    """This thread constantly runs and tries to poke the comet channels of
    players every 5 minutes to see, if players are still online."""
    def run(self):
        print "OfflineSenseWorker initialized"
        # wait for stuff to initialize or the first login
        login_event.wait(300)
        if login_event.isSet():
            login_event.clear()
        time.sleep(5)

        wtime = 300
        while not stop_osw_event.isSet():
            numonline = 0
            for plr in session.query(models.Player).filter(models.Player.status > 0).all():
                if not eventlog.poke(plr.username):
                    print "poked %s - offline" % (plr.username)
                    eventlog.send_to(plr.position, "%s left" % (plr.username))
                    plr.status = 0
                else:
                    print "poked %s - still online" % (plr.username)
                    if datetime.now() - plr.lastact > timedelta(minutes=10):
                        plr.status = 0
                        eventlog.send_to(plr.position, "%s left" % (plr.username,))
                        print "  but the last activity is too long ago. set to offline."
                    else:
                        numonline += 1
            if numonline > 0:
                wtime = 300
            else:
                wtime = 3600
            print "poker waiting for %i minutes" % (wtime / 60)
            login_event.wait(wtime)
            if login_event.isSet():
                print "woken up by player login!"
                login_event.clear()
            time.sleep(5)

osw = None
def start_osw():
    global osw
    if stop_osw_event.isSet():
        osw = None
    stop_osw_event.clear()
    with osw_lock:
        if not osw:
            osw = OfflineSenseWorker()
            osw.daemon = True
            osw.start()

def stop_osw():
    global osw
    stop_osw_event.set()
