from pygsear.Game import Game
from pygsear.Event import TIMEOUT_Event

class G(Game):
    splash_filename = None

    def initialize(self):
        t = TIMEOUT_Event(3000, callback=self.start_pinging)
        self.events.add(t)

        self.events.add(TIMEOUT_Event(delay=8000, count=-1, callback=self.reset_pinger))

    def start_pinging(self, ev):
        self.pinger = TIMEOUT_Event(delay=500, count=5, callback=self.ping, keepalive=1)
        self.events.add(self.pinger)

    def ping(self, ev):
        print 'ping'

    def reset_pinger(self, ev):
        print 'pong'
        self.pinger.reset()

if __name__ == '__main__':
    g = G()
    g.mainloop()
