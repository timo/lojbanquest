from __future__ import absolute_import
from quest.eventlog import Log, send_to, poke, render_log
from nagare.namespaces import xhtml
from nose.tools import raises

log = None
def setup_module():
    global log
    log = Log("testuser")

def teardown_module():
    global log
    log = None

#def render_test():
#    render_log(log, xhtml.Renderer())

def send_test():
    # no browser is connected, thus it will return false.
    send_to("testuser", "testuser left")
    send_to("idontexist", "what?")

@raises(ValueError)
def send_fail():
    send_to(1, "hello")

def poke_test():
    assert poke("testuser")
    assert not poke("foobar")
