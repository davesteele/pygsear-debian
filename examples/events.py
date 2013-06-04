import pygame
from pygame.locals import K_a, K_s, K_x, K_z, K_d, K_l, K_c, K_i, K_SPACE, K_DOWN


from pygsear.Game import Game
from pygsear import Event
from pygsear.Widget import Dialog_OK, Dialog_LineInput, Dialog_ColorSelector

from pygsear.Drawable import Turtle


class G(Game):
    def initialize(self):
        self.set_background(color=(57, 142, 83))

        self.events.add(Event.KEYDOWN_Event(key=K_i, callback=self.instructions))

        self.gr = Event.EventGroup()
        self.gr_enabled = 1
        ev = Event.KEYDOWN_Event(key=(K_a, K_s), callback=self.foo, ship='player')
        self.gr.add(ev)
        self.events.add(ev)

        self.events.add(Event.KEYDOWN_Event(key=K_x, callback=self.toggle))
        self.events.add(Event.KEYDOWN_Event(key=K_z, callback=self.enable))

        self.events.add(Event.KEYDOWN_Event(key=K_d, callback=self.dialog))
        self.events.add(Event.KEYDOWN_Event(key=K_l, callback=self.line))

        self.events.add(Event.KEYDOWN_Event(key=K_c, callback=self.colors))

        self.events.add(Event.Repeat_KEY_Event(key=K_SPACE,
                                                on_press=self.start_space,
                                                on_hold=self.space,
                                                on_release=self.end_space))
        self.events.add(Event.Repeat_KEY_Event(key=K_DOWN, on_hold=self.down))

        self.instructions()


    def instructions(self, pygame_event=None):
        instructions = """Controls:

        i - show these instructions

        a - call the foo method
        s - call the foo method

        z - enable event group
        x - toggle event group

        space - auto-repeat spacebar
        down arrow - auto-repeat arrow

        d - show OK dialog
        l - show LineInput dialog
        c - show ColorSelector dialog"""

        dlg = Dialog_OK(message=instructions, size=(350, 450)).modal()

    def start_space(self, ev):
        print 'start - space'

    def end_space(self, ev):
        print ' end  - space'

    def space(self, ev):
        print 'space'

    def down(self, ev):
        print 'down'

    def foo(self, pygame_event, ship):
        print 'foo', pygame_event, ship

    def enable_gr(self):
        self.gr_enabled = 1
        self.gr.enable()

    def disable_gr(self):
        self.gr_enabled = 0
        self.gr.disable()

    def toggle(self, pygame_event):
        print 'toggling', pygame_event
        if self.gr_enabled:
            self.disable_gr()
        else:
            self.enable_gr()

    def enable(self, pygame_event):
        print 'enabling', pygame_event
        self.enable_gr()

    def dialog(self, pygame_event):
        message =   "A very very long message, \
which would overflow the \
edges of that little rectangle \
but won't since the lines get wrapped automatically"
        dlg = Dialog_OK(message=message)
        dlg.modal()

    def line(self, pygame_event):
        message =   """Enter your name:"""
        dlg = Dialog_LineInput(message=message, callback=self.get_name)
        dlg.modal()

    def get_name(self, name):
        print 'name is', name

    def colors(self, ev):
        dlg = Dialog_ColorSelector()
        color = dlg.modal()
        if color is not None:
            self.set_background(color=color)


if __name__ == '__main__':
    g = G()
    g.mainloop()
