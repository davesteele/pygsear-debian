import random
import math

from pygame.locals import K_UP, K_q, K_DOWN, K_a

from pygsear.Drawable import Rectangle, Square
from pygsear.Widget import Score
from pygsear.Game import Game
from pygsear.Event import KEYDOWN_Event, KEYUP_Event
from pygsear import conf


class Paddle(Rectangle):
    def __init__(self):
        Rectangle.__init__(self, width=15, height=50)
        self.center(x=10)
        
        self.set_speed(100)

        self.up_pressed = 0
        self.down_pressed = 0

    def up(self, event):
        self.up_pressed = 1

    def noup(self, event):
        self.up_pressed = 0

    def down(self, event):
        self.down_pressed = 1

    def nodown(self, event):
        self.down_pressed = 0

    def set_speed(self, speed):
        self.speed = speed

    def hit(self):
        self.set_speed(self.speed + 5)

    def set_vel(self):
        if self.up_pressed and not self.down_pressed:
            self.path.set_velocity(vy=-self.speed)
        elif self.down_pressed and not self.up_pressed:
            self.path.set_velocity(vy=self.speed)
        else:
            self.path.set_velocity(vy=0)

    def move(self):
        self.set_vel()
        Rectangle.move(self) 
        self.onscreen(top=-5, bottom=-5, jail=1)


class Ball(Square):
    def __init__(self):
        Square.__init__(self, side=15)
        self.center()
        self.path.set_velocity(vx=150)

    def walls(self):
        if not self.onscreen(top=-5, bottom=-5, jail=1):
            self.path.bounce_y()
        if not self.onscreen(right=-5, jail=1):
            self.path.bounce_x()

    def hit(self):
        vx, vy = self.path.get_velocity()
        vx = abs(vx) + 10
        vyMax = vx / 2
        vy = random.uniform(-vyMax, vyMax)
        self.path.set_velocity(vx=vx, vy=vy)

    def move(self):
        self.walls()
        Square.move(self) 


class Pong(Game):
    def initialize(self):
        self.window.border(left=0, top=5, right=5, bottom=5)
        self.window.set_title('Pong!')

        self.paddle = Paddle()
        self.sprites.add(self.paddle)
        self.ball = Ball()
        self.sprites.add(self.ball)

        self.events.add(KEYDOWN_Event(key=(K_UP, K_q), callback=self.paddle.up))
        self.events.add(KEYUP_Event(key=(K_UP, K_q), callback=self.paddle.noup))
        self.events.add(KEYDOWN_Event(key=(K_DOWN, K_a), callback=self.paddle.down))
        self.events.add(KEYUP_Event(key=(K_DOWN, K_a), callback=self.paddle.nodown))

        self.score = Score(position=(conf.WINWIDTH-195, 40))
        self.sprites.add(self.score)

        self.maxscore = Score(text='Max:', position=(conf.WINWIDTH-170, 70))
        self.sprites.add(self.maxscore)
    
    def checkCollisions(self):
        if self.ball.collide(self.paddle):
            self.ball.hit()
            self.paddle.hit()
            self.score.addPoints(1)
            self.score.updateScore()

        if not self.ball.onscreen(left=10, jail=1):
            self.ball.onscreen(left=-10, jail=1)
            if self.ball.collide(self.paddle):
                self.checkCollisions()
                return
            self.ball.center()
            self.paddle.set_speed(100)
            self.ball.path.set_velocity(vx=150, vy=0) 
            self.maxscore.set_points(max(self.score.points, self.maxscore.points))
            self.maxscore.updateScore()
            self.score.set_points(0)
            self.score.updateScore()


if __name__ == '__main__':
    game = Pong()
    game.mainloop()
