from pygsear.Drawable import Layer, Circle
from pygsear.Game import Game
from pygsear.Path import CirclePath
from pygsear.locals import BLUE, RED, GREEN, ORANGE, PURPLE, YELLOW



class L2(Layer):
    def move(self):
        Layer.move(self)
        x, y = self.get_position()
        #print x
        if 50 > x > 45:
            print 'change'
            self.set_background(color=RED)

class C2(Circle):
    def move(self):
        x, y = self.get_position()
        #print 'moving', x, y
        Circle.move(self)


game = Game()

layer = game.addLayer(size=(500, 500))
#print 1
layer.center()
#print 1
layer.set_background(color=BLUE)
layer.border(10)
#layer.path.set_velocity(vx=10, vy=10)

path = CirclePath()
path.set_loop(-1)
layer.set_path(path)
game.sprites.add(layer, level=1)


circle = C2(layer, color=GREEN)
#print 2
circle.center(y=20)
#print 2
circle.path.set_velocity(vx=-15, vy=10)
layer.sprites.add(circle)


circle2 = C2(color=RED)
#print 3
circle2.center(y=20)
#print 3
circle2.path.set_velocity(vx=-15, vy=10)
game.sprites.add(circle2, level=2)

circle2a = C2(color=ORANGE)
#print 3
circle2a.center(y=20)
#print 3
circle2a.path.set_velocity(vx=-15, vy=15)
game.sprites.add(circle2a, level=0)


circle3 = C2(layer, color=YELLOW)
#print 3
circle3.center()
#print 3
x, y = circle3.get_position()
path = CirclePath(startLocation=(x, y), size=40, clockwise=0)
path.set_loop(-1)
circle3.set_path(path)
layer.sprites.add(circle3)


game.mainloop()
