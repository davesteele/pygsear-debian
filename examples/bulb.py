from pygsear.Drawable import MultiImage, String, Image, Stationary
from pygsear.Game import Game
from pygsear.Event import KEY_Event, KEYUP_Event, TIMEOUT_Event
from pygsear.Widget import Dialog, SpriteTextButton
from pygsear.Util import render_textrect
from pygsear import conf
from pygsear.locals import BLACK

import pygame
from pygame.locals import K_SPACE, K_RETURN


class Bulb(MultiImage):
    filenames = ('bulb_on.png', 'bulb_off.png')

    def __init__(self):
        MultiImage.__init__(self)
        if conf.game is None:
            game = Game()
            conf.game = game
            game.sprites.add(self)
            game.step()
        self.turn_off()

    def turn_off(self):
        self.state = 'off'
        self.bgcolor = (25, 25, 125)
        self.flip()

    def turn_on(self):
        self.state = 'on'
        self.bgcolor = (125, 125, 225)
        self.flip()

    def on(self):
        return self.state == 'on'

    def toggle(self):
        if self.on():
            self.turn_off()
        else:
            self.turn_on()

    def flip(self):
        key = 'bulb_%s.png' % self.state
        MultiImage.flip(self, key)
        conf.game.set_background(color=self.bgcolor)


class Wizard(Dialog):
    def __init__(self,
                    window=None,
                    size=None,
                    message='Continue to next step...',
                    centertext=1,
                    next_text='Next',
                    next_callback=None,
                    back_text='Back',
                    back_callback=None,
                    ):
        """Initialize dialog

        @param window: Layer in which to draw the dialog box.
        @param size: Tuple of C{(width, height)} for dialog box.
        @param message: String message to be displayed. Text will be wrapped
            automatically to fit inside the box, but an error will be raised
            if the text will not fit.
        @param centertext: Center justify the message by default.
        @param next_callback: Function to call when the "Next" button is clicked
            or the enter key is pressed.

        """

        Dialog.__init__(self, window, size)

        self.next_callback = next_callback
        self.back_callback = back_callback

        self.events.add(KEYUP_Event(key=K_RETURN, callback=self.next))

        w, h = self.get_size()
        rect_w = int(0.9 * w)
        rect_h = int(h - 70)
        rect = pygame.Rect(0, 0, rect_w, rect_h)
        textrect = render_textrect(message, rect, fontSize=24, justification=centertext)
        s = Image(w=self, image=textrect)
        s.center(y=15)
        s = Stationary(w=self, sprite=s)
        s.draw()

        next = SpriteTextButton(self, next_text, callback=self.next,
                                        group=self.events)
        next.center(dx=80, y=-30)
        next = Stationary(w=self, sprite=next)
        next.draw()

        back = SpriteTextButton(self, back_text, callback=self.back,
                                        group=self.events)
        back.center(dx=-80, y=-30)
        back = Stationary(w=self, sprite=back)
        back.draw()

    def next(self, pygame_event=None):
        self.teardown()
        self.next_callback(pygame_event)

    def back(self, pygame_event=None):
        self.teardown()
        self.back_callback(pygame_event)


class TutText:
    def __init__(self):
        self.n = 0
        self.demo = conf.game

    def set_frame(self):
        frame = 'frame%02d' % self.n
        if hasattr(self, frame):
            getattr(self, frame)()

            banner = String(message=self.title, fontSize=40)
            banner.center(y=20)
            self.demo.sprites.add(banner)
            self.banner = banner

            dlg = Wizard(message=self.text,
                            size=(400,500),
                            next_callback=self.flip,
                            back_callback=self.flipback,
                            centertext=0)
            dlg.nudge(dx=180, dy=20)
            self.demo.sprites.add(dlg)
            self.demo.events.add(dlg.events)
            self.dlg = dlg

    def flip(self, ev=None):
        self.n += 1
        if hasattr(self, 'dlg'):
            self.dlg.kill()
            self.banner.kill()

        self.set_frame()


    def flipback(self, ev=None):
        if self.n > 0:
            self.n -= 1
        if hasattr(self, 'dlg'):
            self.dlg.kill()
            self.banner.kill()

        self.set_frame()


    def frame00(self):
        self.title = "Welcome to Your Illumination"
        self.text = """This program will introduce you to the concept of \
"object oriented" computer programming using the Python language.

        """
        self.timenext = 5000

        self.demo.events.add(TIMEOUT_Event(200, callback=self.demo.destroy_bulb))

    def frame01(self):
        self.title = "What Is an Object?"
        self.text = """An object is some "thing" that you want \
to represent with your computer program.

For instance, you might want to model a \
lightbulb.

To create the lightbulb, you could import \
the code for the lightbulb and then create \
one:

from illumination import Bulb

lightbulb = Bulb()

        """
        self.timenext = 3000

        self.demo.events.add(TIMEOUT_Event(4000, callback=self.demo.make_bulb))

    def frame02(self):
        self.title = "Object Data"
        self.text = """Every object has data, which \
is just another word for information about the object.

For instance, the Bulb object has an instance variable called \
state, which holds either the value 'on' or 'off'. It would \
also have been quite reasonable to just use numerical values \
for state (that is, either 1 or 0) or even to change the name \
of the variable and use a boolean value.

In other words it might have an instance variable called bulb_lit \
and use values True or False.

        """
        self.timenext = 5000


class BulbDemo(Game):
    def initialize(self):
        self.events.add(TIMEOUT_Event(1000, callback=self.run_tut))
        self.bulb_events = self.addEventGroup()

    def make_bulb(self, ev=None):
        if not hasattr(self, 'bulb'):
            bulb = Bulb()
            bulb.set_position((50, 50))
            self.bulb = bulb
            self.sprites.add(bulb)
            toggle = KEY_Event(key=K_SPACE, on_press=self.toggle_bulb)
            self.events.add(toggle)
            self.bulb_events.add(toggle)

    def destroy_bulb(self, ev=None):
        if hasattr(self, 'bulb'):
            self.set_background(color=BLACK)
            self.bulb.kill()
            self.bulb_events.kill()
            del(self.bulb)

    def toggle_bulb(self, ev=None):
        self.bulb.toggle()

    def run_tut(self, ev=None):
        self.tut = TutText()
        self.tut.set_frame()



if __name__ == '__main__':
    game = BulbDemo()
    game.mainloop()
