from stackless import channel, tasklet

class CentralBus(object):
    def __init__(self):
        print "initialized messagebus"
        self.channels = {}

    def subscribe(self, domain):
        newc = channel()

        if domain not in self.channels:
            self.channels[domain] = []

        self.channels[domain].append(newc)

        return newc

    def unsubscribe(self, cha, domain):
        self.channels[domain].remove(chan)


    def send(self, message, domains):
        def sendtasklet(domains, message, chan):
            chan.send((domains, message))

        print "messagebus sending '%r' to %s" % (message, domains)

        if isinstance(domains, basestring):
            domains = [domains]

        recipients = {}

        for dom in domains:
            for rec in self.channels[dom]:
                if rec not in recipients:
                    recipients[rec] = []
                recipients[rec].append(dom)

        num = 0

        for rec, domains in recipients.iteritems():
            num += 1
            #rec.send((domains, message))
            task = tasklet(sendtasklet)
            task.setup(domains, message, rec)
            task.run()

        print "sent to %d recipients." % (num)
        return num

bus = CentralBus()

class CallbackRecipient(object):
    def __init__(self, name, domain):
        self.callback = lambda x: x
        self.name = name
        self.domain = domain

        self.alive = True

        self.chan = bus.subscribe(domain)
    
    def __call__(self):
        task = tasklet(self.tasklet)
        task.setup()

    def resubscribe(self, newdomain):
        self.kill()
        bus.unsubscribe(self.chan, self.domain)
        self.domain = newdomain
        self.chan = bus.subscribe(newdomain)
        self()

    def kill(self):
        self.alive = False
        self.chan.send_exception(StopIteration)

    def tasklet(self):
        print "callback to %r now active." % (self.callback, )
        try:
            while self.alive:
                msg = self.chan.receive()
                self.callback(msg)
                print "callback to %r with %r." % (self.callback, msg)
        except StopIteration:
            print "CallbackRecipient to %r stopped." % (self.callback, )
