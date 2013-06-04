from pygsear.Drawable import Circle, Multi, Rectangle
from pygsear.Game import Game
from pygsear import Event

from pygame.locals import K_j, K_k, K_l
from pygame.sprite import Sprite


class M0(Multi):
    def __init__(self):
        Multi.__init__(self)
        for x in range(0, 175, 25):
            c = Circle()
            self.addSprite(c, xOffset=x)


class G(Game):
    def initialize(self):

        r = Rectangle(width=500, height=5)
        self.sprites.add(r)
        r.set_position(100,100)

        self.multi1 = M0()
        self.sprites.add(self.multi1)
        self.multi1.set_position((10, 300))
        self.multi1.path.set_velocity(vx=20)
        self.events.add(Event.KEYDOWN_Event(key=K_j, callback=self.m1kill))


        self.multi2 = M0()
        self.multi2.center()
        self.sprites.add(self.multi2)
        self.multi2.path.set_velocity(vx=70)
        self.events.add(Event.KEYDOWN_Event(key=K_k, callback=self.m2kill))

        self.m3a = M0()
        self.m3b = M0()
        self.multi3 = Multi()
        self.multi3.addSprite(self.m3a)
        self.multi3.addSprite(self.m3b, yOffset=50)
        self.multi3.path.set_velocity(vy=50)
        self.multi3.center()
        self.sprites.add(self.multi3)
        self.events.add(Event.KEYDOWN_Event(key=K_l, callback=self.m3kill))


    def m1kill(self, *a):
        self.multi1.kill()

    def m2kill(self, *a):
        self.multi2.kill()

    def m3kill(self, *a):
        self.multi3.kill()




if __name__ == '__main__':
    g = G()
    g.mainloop()
