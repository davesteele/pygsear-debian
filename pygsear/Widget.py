# pygsear
# Copyright (C) 2003 Lee Harr
#
#
# This file is part of pygsear.
#
# pygsear is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pygsear is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pygsear; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Graphical input devices"""

import time, random, math, os, sys, types
import colorsys
from code import InteractiveConsole
from code import compile_command

import pygame
import pygame.draw
from pygame.locals import K_RETURN, K_ESCAPE, K_BACKSPACE, K_F1, K_UP, K_DOWN
from pygame.locals import K_PAGEUP, K_PAGEDOWN, K_LEFT, K_RIGHT, K_DELETE
from pygame.locals import QUIT, MOUSEBUTTONUP

import conf
import Drawable
from Drawable import Rectangle
import Path
import Event
import Util
from locals import TRANSPARENT, BLACK, WHITE, LGREEN, LGRAY, GRAY, BLUE, RED


class Widget:
    def __init__(self, callback=None, group=()):
        self.set_callback(callback)
        self.events = Event.EventGroup()

    def set_callback(self, callback):
        if callback is None:
            callback = self.nop
        self.callback = callback

    def nop(self, arg=None):
        pass

    def activate(self):
        self.active = 1

    def deactivate(self):
        self.active = 0

    def _stop(self, pygame_event=None):
        self.stop = 1

    def _quit(self, pygame_event=None):
        ev = pygame.event.Event(QUIT)
        pygame.event.post(ev)
        self._stop()

    def modal(self):
        stop = Event.KEYUP_Event(key=K_ESCAPE, callback=self._stop)
        while not self.stop:
            self.events.check()


class Score(Widget, Drawable.Drawable):
    """Keep and display a score or value."""

    def __init__(self,
                    w=None,
                    position=(100, 100),
                    text="Score:",
                    digits=6,
                    fontSize=40,
                    color=WHITE,
                    bgcolor=TRANSPARENT):
        Drawable.Drawable.__init__(self, w)
        self.score_position = position
        self.text = text
        self.digits = digits
        self.color = color
        self.bgcolor = bgcolor
        self.font = pygame.font.Font(None, fontSize)
        self.points = 0
        self.updateScore()
        self.set_position(position)
        self.set_crect(self.rect)

    def addPoints(self, n):
        """Add points to the score."""

        self.points += n

    def subtractPoints(self, n):
        """Subtract points from the score."""

        self.points -= n

    def set_points(self, p):
        """Set the score to a particular value."""

        self.points = p

    def updateScore(self):
        """Render the text for showing the score."""

        if hasattr(self, 'image'):
            self.uclear()

        line = '%s %*d' % (self.text, self.digits, self.points)
        self.image = self.font.render(line, 1, self.color, self.bgcolor)
        self.rect = self.image.get_rect()
        self.set_position(self.score_position)
        if self.bgcolor == TRANSPARENT:
            self.image.set_colorkey(TRANSPARENT)


class ProgressBar(Widget, Rectangle):
    """Percentage bar graph."""

    def __init__(self,
                    w=None,
                    steps=100,
                    position=None,
                    color=BLACK,
                    width=None,
                    height=10,
                    fill=1,
                    border=0,
                    borderColor=WHITE):
        if width is None:
            width = conf.WINWIDTH-60
        self.colorOriginal = color
        self.set_color(color)
        self.width = width
        self.height = height
        Rectangle.__init__(self, w, width, height, color=color)
        self.image.set_colorkey(TRANSPARENT)
        if position is None:
            self.center(y=-30)
        else:
            self.set_position(position)
        self.fill = fill
        self.set_steps(steps)
        self.set_crect(self.image.get_rect())

    def set_steps(self, steps):
        """
        """
        self.steps = steps
        self.perStep = float(self.width)/steps
        if self.fill:
            self.stepsLeft = steps
        else:
            self.stepsLeft = 0
        self.show()

    def step(self):
        """
        """
        if self.fill:
            self.stepsLeft -= 1
            if self.stepsLeft < 1:
                self.stepsLeft = 0
        else:
            self.stepsLeft += 1
            if self.stepsLeft > self.steps:
                self.stepsLeft = self.steps
        self.show()

    def unstep(self):
        """
        """
        if not self.fill:
            self.stepsLeft -= 1
            if self.stepsLeft < 1:
                self.stepsLeft = 0
        else:
            self.stepsLeft += 1
            if self.stepsLeft > self.steps:
                self.stepsLeft = self.steps
        self.show()

    def reset(self):
        self.stepsLeft = self.steps
        self.set_color(self.colorOriginal)
        self.show()

    def set_color(self, color):
        """set the color of the bar"""

        self.color = color

    def show(self):
        """
        """
        width = int(self.stepsLeft * self.perStep)
        height = self.height

        bar = pygame.Surface((width, height))
        bar.fill(self.color)

        self.image.fill(TRANSPARENT)
        self.image.blit(bar, (0, 0))


class VProgressBar(ProgressBar):
    def __init__(self,
                    w=None,
                    steps=100,
                    position=None,
                    color=BLACK,
                    width=10,
                    height=None,
                    fill=1):
        if height is None:
            height = conf.WINHEIGHT-60
        self.colorOriginal = color
        self.set_color(color)
        self.width = width
        self.height = height
        Rectangle.__init__(self, w, width, height, color=color)
        self.image.set_colorkey(TRANSPARENT)
        if position is None:
            self.center(x=30)
        else:
            self.set_position(position)
        self.fill = fill
        self.set_steps(steps)
        self.set_crect(self.image.get_rect())

    def set_steps(self, steps):
        """
        """
        self.steps = steps
        self.perStep = float(self.height)/steps
        if self.fill:
            self.stepsLeft = steps
        else:
            self.stepsLeft = 0
        self.show()

    def show(self):
        """
        """
        width = self.width
        height = int(self.stepsLeft * self.perStep)

        bar = pygame.Surface((width, height))
        bar.fill(self.color)
        self.image.fill(TRANSPARENT)
        self.image.blit(bar, (0, self.height-height))


class Button(Widget):
    def __init__(self, callback=None, group=None):
        Widget.__init__(self)
        self.set_callback(callback)
        #print 'offset', offset, callback
        self.armed = 0
        self.events.add(Event.MOUSEBUTTONDOWN_Event(callback=self.clicked))
        self.events.add(Event.MOUSEBUTTONUP_Event(callback=self.released))
        if group is not None:
            group.add(self.events)
        self.stop = 0

    def arm(self):
        self.armed = 1

    def fire(self, pygameEvent):
        self.armed = 0
        self.callback(pygameEvent)

    def clicked(self, pygameEvent):
        pos = pygameEvent.pos
        try:
            offset = self.window.rect[0:2]
            #print 'off', offset
        except AttributeError:
            offset = (0, 0)

        if self.rect.move(offset[0], offset[1]).collidepoint(pos):
            self.arm()
            return 1
        else:
            return 0

    def released(self, pygameEvent):
        #print 'rel'
        pos = pygameEvent.pos
        try:
            offset = self.window.rect[0:2]
            #print 'off', offset
        except AttributeError:
            offset = (0, 0)

        if self.rect.move(offset[0], offset[1]).collidepoint(pos) and self.armed:
            self.fire(pygameEvent)
        else:
            self.armed = 0


class SpriteButton(Button, Drawable.Drawable):
    """Clickable button which is also a sprite."""

    def __init__(self, sprite, callback=None, group=None):
        """Initialize the button.

        @param sprite: Clickable sprite.
        @param callback: Function to call when sprite is clicked.
        @param group: Other C{EventGroup} to put this widget's events
            in to also.

        """

        pos = sprite.get_position()
        Button.__init__(self, callback, group)
        Drawable.Drawable.__init__(self, w=sprite.window)
        self.image = sprite.image
        self.rect = sprite.rect
        self.set_path(sprite.path)

    def modal(self):
        quit = Event.QUIT_Event(callback=self._stop)
        self.events.add(quit)
        stop = Event.KEYUP_Event(key=K_ESCAPE, callback=self._stop)
        self.events.add(stop)

        while not self.stop:
            self.clear()
            self.events.check()
            self.udraw()
        quit.kill()
        stop.kill()
        self.uclear()


class ImageButton(SpriteButton):
    filename = None

    def __init__(self, filename=None, callback=None, group=None):
        if filename is None:
            filename = self.filename
        sprite = Drawable.Image(filename=filename)
        SpriteButton.__init__(self, sprite=sprite, callback=callback, group=group)


class StationaryButton(Drawable.Stationary, SpriteButton):
    """Clickable button which is a sprite but does not need to move."""

    def __init__(self,
                    window=None,
                    sprite=None,
                    callback=None,
                    group=None):
        pos = sprite.get_position()
        Drawable.Stationary.__init__(self, w=window, sprite=sprite)
        SpriteButton.__init__(self, sprite, callback, group)
        self.image = sprite.image
        self.rect = sprite.rect
        self.set_position(pos)


class CloseButton(StationaryButton):
    """White square button with a black X."""

    def __init__(self, window=None, callback=None, group=None):
        b = Drawable.Square(w=window, side=15, color=WHITE)
        w, h = b.image.get_size()
        pygame.draw.line(b.image, BLACK, (0, 0), (w, h))
        pygame.draw.line(b.image, BLACK, (w, 0), (0, h))
        b.center(-5, 5)
        #print 'bc', b.center, window.screen.get_size(), b.get_position()
        StationaryButton.__init__(self, window, b, callback, group)
        self.draw()


class TextButton:
    """Clickable button with text printed on it."""

    def __init__(self,
                    window=None,
                    text='click',
                    length=None,
                    callback=None,
                    size=22,
                    color=WHITE,
                    border=2,
                    borderColor=LGREEN,
                    padding=5,
                    bgColor=BLACK):
        self.window = window
        #print window
        self.text = text
        self.length = length
        self.size = size
        self.color = color
        self.border = border
        self.borderColor = borderColor
        self.padding = padding
        self.bgColor = bgColor
        self.makeButton()

    def makeButton(self):
        window = self.window
        text = self.text
        length = self.length
        size = self.size
        color = self.color
        border = self.border
        borderColor = self.borderColor
        padding = self.padding
        bgColor = self.bgColor

        t = Drawable.String(message=text, fontSize=size, color=color,
                                    bgcolor=bgColor)

        # use inverse text at cursor position if cursor_pos is set
        if hasattr(self, 'cursor_pos'):
            c = self.cursor_pos
            before = Drawable.String(message=text[:c], fontSize=size, color=color,
                                    bgcolor=bgColor)
            bw, bh = before.image.get_size()
            cursor = Drawable.String(message=text[c:c+1], fontSize=size, color=bgColor,
                                    bgcolor=color)
            cw, ch = cursor.image.get_size()
            t.image.blit(cursor.image, (bw, 0))

        w, h = t.image.get_size()
        if length is not None:
            s = pygame.Surface((length, h))
            s.fill(bgColor)
            s.blit(t.image, (0, 0))
            w = length
        self.length = w

        bw = w + 2*padding + 2*border
        bh = h + 2*padding + 2*border

        if border:
            #print 'boxing', dir(window)
            box = Drawable.Rectangle(w=window, width=bw, height=bh,
                                        color=borderColor)
            iw = w + 2*padding
            ih = h + 2*padding
            pygame.draw.rect(box.image, bgColor,
                                ((border, border), (iw, ih)))
        else:
            #print 'boxing', dir(window)
            box = Drawable.Rectangle(w=window, width=bw, height=bh, color=bgColor)
        box.image.blit(t.image, (border+padding, border+padding))
        if bgColor == TRANSPARENT:
            box.image.set_colorkey(TRANSPARENT)

        self.box = box


class SpriteTextButton(TextButton, SpriteButton):
    """Clickable button which is also a sprite with text printed on it."""

    def __init__(self,
                    window=None,
                    text='',
                    length=None,
                    callback=None,
                    size=22,
                    color=WHITE,
                    border=2,
                    borderColor=LGREEN,
                    padding=5,
                    bgColor=BLACK,
                    group=None):
        #print 'stb', window.offset
        TextButton.__init__(self, window, text, length, callback, size,
                    color, border, borderColor, padding, bgColor)
        SpriteButton.__init__(self, self.box, callback, group)


class StationaryTextButton(TextButton, StationaryButton):
    """Clickable button which is also a sprite with text printed on it
    and does not need to move."""

    def __init__(self,
                    window=None,
                    text="",
                    length=None,
                    callback=None,
                    size=22,
                    color=WHITE,
                    border=1,
                    borderColor=LGREEN,
                    padding=5,
                    bgColor=BLACK,
                    group=None):
        TextButton.__init__(self, window, text, length, callback, size,
                    color, border, borderColor, padding, bgColor)
        StationaryButton.__init__(self, sprite=self.box, callback=callback,
                                        group=group)


class TextInput(SpriteTextButton):
    """Used to gather text input from the user."""

    def __init__(self,
                    window=None,
                    text='',
                    prompt='',
                    maxLength=10,
                    length=150,
                    callback=None,
                    size=22,
                    color=WHITE,
                    border=1,
                    borderColor=LGREEN,
                    padding=5,
                    bgColor=BLACK,
                    inactiveColor=LGRAY,
                    inactiveBgColor=GRAY,
                    group=None):
        """
        Initialize the TextInput widget.

        @param window: Layer on which sprite lives.
        @param text: Initial text in the window.
        @param maxLength: Maximum number of characters in input.
        @param length: Width of the text window in pixels.
        @param callback: Function to call when RETURN is pressed.
        @param size: Font size.
        @param color: Text color.
        @param border: Thickness of text window border (0 for no border)
        @param borderColor: Color of window border (if any)
        @param padding: Space between text and edge of window or border.
        @param bgColor: Background color of text window.
        @param inactiveColor: Text color when widget is inactive.
        @param inactiveBgColor: Background color when widget is inactive.
        @param group: Additional group/ groups that should watch for
            this widget's events.

        """

        self.maxLength = maxLength
        self.text = text
        self.prompt = prompt
        self.text_content = text
        t = prompt + text + " " * (maxLength - len(text))
        self.active = 0
        SpriteTextButton.__init__(self, window, t, length, callback, size, color,
                                border, borderColor, padding, bgColor, group)

        repeater = Event.Repeat_KEY_Event(on_hold=self.addLetter, group=group)
        self.events.add(repeater)
        self.events.add(repeater.contains.events())
        self.repeater = repeater
        self.events.add(Event.KEYUP_Event(key=K_RETURN, callback=self.done, group=group))

        self.activeColor = color
        self.activeBgColor = bgColor
        self.inactiveColor = inactiveColor
        self.inactiveBgColor = inactiveBgColor

    def done(self, pygame_event=None):
        """return the text_content.

        If this is triggered from one of the widget's own events (ie K_RETURN),
        it only returns the contents if the widget is active. Otherwise, if it
        was called from outside (pygame_event is None) it returns the content
        no matter what it's state was (active or inactive).  This allows another
        button to call in to the TextInput and force it to trigger its callback.

        @param pygame_event: C{pygame.Event} triggering the call. If this is
            None, C{done()} must have been called from outside the widget, and
            so it should just go ahead and callback with its text.

        """

        #print 'done', pygame_event, self.active
        if self.active or pygame_event is None:
            text = self.text_content
            self.callback(text)
            self.text = ""
            self.text_content = ""
            if hasattr(self, 'cursor_pos'):
                del(self.cursor_pos)
            self.updateButton()
        else:
            return

    def addLetter(self, pygameEvent):
        """Process the next keypress.

        @param pygameEvent: L{pygame.event.Event}. Usually passed in from
            the pygsear Event handler.

        """

        #print 'adding letter'
        if not self.active:
            return

        k = pygameEvent.key

        text = self.text_content
        new_text = text

        if k in (K_RETURN, K_ESCAPE):
            return
        elif k == K_LEFT:
            self.cursor_left()
            return
        elif k == K_RIGHT:
            self.cursor_right()
            return

        letter = pygameEvent.unicode
        if letter:
            if hasattr(self, 'cursor_pos'):
                c = self.cursor_pos
                t = list(text)
                if k == K_BACKSPACE:
                    t.pop(c-1)
                    self.cursor_pos -= 1
                elif k == K_DELETE:
                    t.pop(c)
                    if self.cursor_pos > len(t) - 1:
                        del(self.cursor_pos)
                elif len(t) >= self.maxLength:
                    Util.beep()
                    #return
                else:
                    t.insert(c, letter)
                    self.cursor_pos += 1
                new_text = ''.join(t)
            else:
                if k == K_BACKSPACE:
                    if text:
                        new_text = text[0:-1]
                    else:
                        Util.beep()
                elif k == K_DELETE:
                    Util.beep()
                elif len(text) >= self.maxLength:
                    Util.beep()
                    #return
                else:
                    new_text = text + letter

        if new_text != text:
            self.set_text(new_text)

    def set_text(self, text):
        """Save a copy of the content of the text field and update.

        Since the actual field is padded with spaces when it is rendered,
        it is necessary to save a copy of the actual contents before going
        to render.

        """

        #self.text = text
        self.text_content = text
        self.updateButton()

    def cursor_left(self):
        text = self.text_content
        if text:
            if not hasattr(self, 'cursor_pos'):
                pos = len(text) - 1
            else:
                pos = self.cursor_pos - 1
            if pos < 0:
                pos = 0
                Util.beep()
            self.cursor_pos = pos
            self.updateButton()
        else:
            pass
            Util.beep()

    def cursor_right(self):
        if not hasattr(self, 'cursor_pos'):
            Util.beep()
        else:
            pos = self.cursor_pos + 1
            if pos == len(self.text_content):
                del(self.cursor_pos)
            else:
                self.cursor_pos = pos
            self.updateButton()

    def updateButton(self):
        pos = self.get_position()
        text = self.text_content
        self.text = self.prompt + text + " " * (self.maxLength - len(text))

        self.makeButton()
        self.image = self.box.image

        self.set_position(pos)
        self.udraw()

    def makeButton(self):
        if self.prompt:
            if hasattr(self, 'cursor_pos'):
                promptlen = len(self.prompt)
                self.cursor_pos += promptlen
                TextButton.makeButton(self)
                self.cursor_pos -= promptlen
            else:
                TextButton.makeButton(self)
        else:
            TextButton.makeButton(self)

    def activate(self):
        Widget.activate(self)
        self.color = self.activeColor
        self.bgColor = self.activeBgColor
        self.updateButton()

    def deactivate(self):
        Widget.deactivate(self)
        self.color = self.inactiveColor
        self.bgColor = self.inactiveBgColor
        self.updateButton()

    def fire(self, pygameEvent):
        self.armed = 0
        self.callback(pygameEvent)

    def clicked(self, pygameEvent):
        pos = pygameEvent.pos
        try:
            offset = self.window.rect[0:2]
        except AttributeError:
            offset = (0, 0)
        if self.rect.move(offset[0], offset[1]).collidepoint(pos):
            self.activate()
            return 1
        else:
            self.deactivate()
            return 0

    def released(self, pygameEvent):
        pass

    def modal(self):
        quit = Event.QUIT_Event(callback=self._stop)
        self.events.add(quit)
        stop = Event.KEYUP_Event(key=K_ESCAPE, callback=self._stop)
        self.events.add(stop)

        self.stop = 0
        self.activate()
        while not self.stop and self.active:
            try:
                conf.ticks = min(20, conf.game.clock.tick(conf.MAX_FPS))
            except AttributeError:
                conf.ticks = 20
            self.clear()
            self.events.check()
            self.udraw()

            if not self.line.repeater.key_held and not self.stop:
                ev = pygame.event.wait()
                pygame.event.post(ev)

        self.deactivate()
        quit.kill()
        stop.kill()
        self.uclear()


class Dialog(Drawable.Layer, Widget):
    def __init__(self, window=None, size=None, callback=None):
        Widget.__init__(self, callback)
        if size is None:
            w, h = conf.WINSIZE
            w = int(0.5 * w)
            h = int(0.3 * h)
        else:
            w, h = size
        Drawable.Layer.__init__(self, w=window, size=(w, h))
        self.center()

        self.events.add(Event.KEYUP_Event(key=K_ESCAPE, callback=self.cancel))

        self.set_background(color=BLACK)
        self.border(width=3, color=RED)

    def cancel(self, pygame_event=None):
        self.teardown()

    def teardown(self):
        self._stop()
        self.uclear()
        self.kill()
        self.events.kill()

    def modal(self):
        quit_ev = Event.QUIT_Event(callback=self._quit)
        self.events.add(quit_ev)
        stop_ev = Event.KEYUP_Event(key=K_ESCAPE, callback=self._stop)
        self.events.add(stop_ev)

        self.stop = 0
        while not self.stop:
            self.clear()
            self.events.check()
            self.udraw()
        quit_ev.kill()
        stop_ev.kill()
        self.uclear()


class Dialog_OK(Dialog):
    """Pop up a window to get some input."""
    message = None

    def __init__(self,
                    window=None,
                    size=None,
                    message=None,
                    centertext=1,
                    callback=None):
        """Initialize dialog

        @param window: Layer in which to draw the dialog box.
        @param size: Tuple of C{(width, height)} for dialog box.
        @param message: String message to be displayed. Text will be wrapped
            automatically to fit inside the box, but an error will be raised
            if the text will not fit.
        @param centertext: Center justify the message by default.
        @param callback: Function to call when the OK button is clicked
            or the enter key is pressed.

        """

        Dialog.__init__(self, window, size, callback)

        if message is None:
            if self.message is None:
                message = 'OK ?'
            else:
                message = self.message

        self.events.add(Event.KEYUP_Event(key=K_RETURN, callback=self.ok))

        w, h = self.get_size()
        rect_w = int(0.9 * w)
        rect_h = int(h - 70)
        rect = pygame.Rect(0, 0, rect_w, rect_h)
        textrect = Util.render_textrect(message, rect, fontSize=24, justification=centertext)
        s = Drawable.Image(w=self, image=textrect)
        s.center(y=15)
        s = Drawable.Stationary(w=self, sprite=s)
        s.draw()

        ok = SpriteTextButton(self, ' OK ', callback=self.ok,
                                        group=self.events)
        ok.center(y=-30)
        ok = Drawable.Stationary(w=self, sprite=ok)
        ok.draw()

        self.return_ok = None

    def ok(self, pygame_event=None):
        self.teardown()
        self.callback(pygame_event)
        self.return_ok = 1

    def modal(self):
        Dialog.modal(self)
        if self.return_ok == 1:
            return 1


class Dialog_LineInput(Dialog_OK):
    """Used to get a single line of input"""

    def __init__(self, window=None, size=None, message='', default='', callback=None, group=None):
        """Initialize the line input dialog.

        @param window: Layer in which to draw the dialog box.
        @param message: Text message to print above the input box.
        @param callback: Function to call when input is finished. returns
            the input text to the callback function.
        @param group: Other event group in which to include this widget's
            events, in addition to its own event group.

        """

        Dialog_OK.__init__(self, window, size, message, callback=callback)

        w, h = self.get_size()
        self.line = TextInput(self, callback=self.finished, text=default, maxLength=50, length=w-50, group=self.events)
        self.events.add(self.line.events.events())
        self.line.center()
        self.line.activate()
        self.has_finished = 0

        if group is not None:
            group.add(self.events.events())
            group.add(self.line.events.events())

        self.return_text = ''

    def ok(self, pygame_event):
        """Called when OK button is clicked. Also called when widget is active
        and ENTER key is pressed.

        @param pygame_event: The pygame event that triggered the callback.

        """

        if pygame_event.type == MOUSEBUTTONUP or self.line.active:
            self.line.done()

        if self.has_finished:
            self.teardown()

    def finished(self, text):
        """Default callback when text input is complete."""

        if not self.has_finished:
            self.return_text = text
            self.callback(text)
            self.line.deactivate()
            self.has_finished = 1

    def modal(self):
        quit_ev = Event.QUIT_Event(callback=self._quit)
        self.events.add(quit_ev)
        stop_ev = Event.KEYUP_Event(key=K_ESCAPE, callback=self._stop)
        self.events.add(stop_ev)

        self.line.activate()

        self.stop = 0
        while not self.stop:
            try:
                conf.ticks = min(20, conf.game.clock.tick(conf.MAX_FPS))
            except AttributeError:
                conf.ticks = 20
            self.clear()
            self.events.check()
            self.line.udraw()
            self.udraw()

            if not self.line.repeater.key_held and not self.stop:
                ev = pygame.event.wait()
                pygame.event.post(ev)

        quit_ev.kill()
        stop_ev.kill()
        self.uclear()

        if self.return_text:
            return self.return_text


class Dialog_ColorSelector(Dialog_OK):
    """Used to choose a color interactively"""

    def __init__(self, window=None):
        """Initialize the color selector"""

        Dialog_OK.__init__(self, window=window, size=(400, 380))

        self.color_square = Drawable.Square(w=self, side=256)
        self.color_square.set_position((10, 10))
        self.color_square_array = pygame.surfarray.array2d(self.color_square.image)
        #self.R = 0
        self.hue = 0
        self.set_color_square()

        self.color_rect = Drawable.Rectangle(w=self, width=20, height=360)
        self.color_rect.set_position((370, 10))
        self.set_color_rect()

        self.show_square = Drawable.Square(w=self, side=50)
        self.show_square.set_position((300, 10))
        self.color_chosen = WHITE
        self.set_color_chosen(self.color_chosen)

        self.mousebuttonup(None)

    def set_color_square(self):
        """Paint a square with possible colors.

        This uses the ColorSelector C{hue} property for the hue of the
        color, then ranges over all possible saturations and values to make
        a square.

        This is way too slow.

        """

        image = self.color_square.image

        h = self.hue
        r, g, b = colorsys.hsv_to_rgb(h, 1, 1)

        rmax = r * 255
        gmax = g * 255
        bmax = b * 255

        dr = (255 - rmax) / 255.0
        dg = (255 - gmax) / 255.0
        db = (255 - bmax) / 255.0

        for y in range(256):
            r = g = b = 0

            xdr = rmax / 255.0
            xdg = gmax / 255.0
            xdb = bmax / 255.0

            for x in range(256):
                image.set_at((x, y), (r, g, b))
                r += xdr
                g += xdg
                b += xdb

            rmax += dr
            gmax += dg
            bmax += db

        self.color_square.udraw()


        #         image = self.color_square.image
        #
        #         h = self.hue
        #         r, g, b = colorsys.hsv_to_rgb(h, 1, 1)
        #
        #         x,y = N.indices((256,256), N.Float)
        #         y /= 256.0
        #         row_mul = 1-y
        #
        #         y *= x
        #         x *= row_mul
        #
        #         rgb = N.zeros((256,256,3), N.Float)
        #         rgb[...,0] = x * r + y
        #         rgb[...,1] = x * g + y
        #         rgb[...,2] = x * b + y
        #
        #         a = pygame.surfarray.pixels3d(image)
        #         a[...] = rgb.astype(N.UnsignedInt8)
        #
        #         self.color_square.udraw()


    def set_color_rect(self):
        """Set up the chooser for the red value of the color."""

        image = self.color_rect.image
        #         for R in range(256):
        #             pygame.draw.line(image, (R, 0, 0), (0, R), (19, R))
        for hue in range(360):
            h = hue / 360.0
            s = v = 1.0
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            R, G, B = 255 * r, 255* g, 255 * b
            pygame.draw.line(image, (R, G, B), (0, hue), (19, hue))
        self.color_rect.udraw()

    def set_color_chosen(self, color):
        """Set the chosen color, and update the display of the chosen color."""

        self.color_chosen = color
        self.show_square.set_color(color)
        self.show_square.udraw()

    def mousebuttondown(self, ev):
        """Set a flag indicating the mouse button is held down."""

        self.button_pressed = 1

    def mousebuttonup(self, ev):
        """Reset the mouse button held down flag."""

        self.button_pressed = 0

    def mousebutton_action(self):
        """Actions to perform any time the mouse button is held down.

        Checks to see if the mouse is inside either of the C{color_square}
        or the C{color_rect} and either sets the chosen color, or sets the
        red value for possible colors and updates the C{color_square}.

        """

        try:
            offset = self.rect[0:2]
        except AttributeError:
            offset = (0, 0)

        lx, ly = offset

        x, y = pygame.mouse.get_pos()
        pos = x-lx, y-ly

        if self.color_square.rect.collidepoint(pos):
            try:
                pos = x-lx-10, y-ly-10
                color = self.color_square.image.get_at(pos)
            except IndexError:
                pass
            else:
                self.set_color_chosen(color[0:3])
        elif self.color_rect.rect.collidepoint(pos):
            try:
                pos = x-lx-370, y-ly-10
                color = self.color_rect.image.get_at(pos)
            except IndexError:
                pass
            else:
                R, G, B = color[0:3]
                r, g, b = R / 256.0, G / 256.0, B / 256.0
                h, s, v = colorsys.rgb_to_hsv(r, g, b)
                self.hue = h
                self.set_color_square()


    def modal(self):
        quit_ev = Event.QUIT_Event(callback=self._quit)
        self.events.add(quit_ev)
        stop_ev = Event.KEYUP_Event(key=K_ESCAPE, callback=self._stop)
        self.events.add(stop_ev)

        down = Event.MOUSEBUTTONDOWN_Event(callback=self.mousebuttondown)
        self.events.add(down)
        up = Event.MOUSEBUTTONUP_Event(callback=self.mousebuttonup)
        self.events.add(up)

        self.stop = 0
        while not self.stop:
            self.clear()
            self.events.check()
            if self.button_pressed:
                self.mousebutton_action()
            self.udraw()
        quit_ev.kill()
        stop_ev.kill()
        self.uclear()

        if self.return_ok:
            return self.color_chosen


class Console(Widget):
    def __init__(self, locals={}, size=(600, 200)):
        self.locals = locals
        Widget.__init__(self)

        self.size = size
        self.history = []
        self.history_curr_index = 0
        self.buffer = []
        self.paged_up = 0

        self.save_stdout = sys.stdout
        self.save_stderr = sys.stderr

        self.make_widget()

    def make_widget(self):
        self.events.kill()

        size = self.size
        w, h = size
        chars = int(w / 8.0)

        self.layer = Drawable.Layer(size=size, color=BLACK)
        self.layer.center(x=10, y=-10)
        self.terp = InteractiveConsole(self.locals)
        self.line = TextInput(self.layer, callback=self.run_command, text='', prompt='>>> ',
                                maxLength=chars, length=w, border=0, group=self.events)
        self.events.add(self.line.events.events())
        self.line.center(x=10, y=-10)
        self.events.add(self.line.events)
        #self.events.add(Event.KEYUP_Event(key=K_F1, callback=self.toggle_visible))

        self.events.add(Event.KEYUP_Event(key=K_UP, callback=self.history_prev))
        self.events.add(Event.KEYUP_Event(key=K_DOWN, callback=self.history_next))

        self.events.add(Event.KEYUP_Event(key=K_PAGEUP, callback=self.handle_pageup))
        self.events.add(Event.KEYUP_Event(key=K_PAGEDOWN, callback=self.handle_pagedown))

        self.lines_width = int(0.95 * w)
        self.lines_height = 5000
        self.lines_per_screen = int(0.8 * (h-45))
        self.lines = Drawable.Layer(w=self.layer, size=(self.lines_width, self.lines_height), color=BLACK)
        self.lines.center(x=10, y=15)
        self.lines_position = h - 52

    def resize(self, size):
        self.size = size
        self.make_widget()
        self.layer.udraw()

    def activate(self):
        Widget.activate(self)
        self.line.activate()
        self.layer.udraw()

    def deactivate(self):
        Widget.deactivate(self)
        self.line.deactivate()
        self.layer.uclear()

    def new_line(self, text, prompt=''):
        save_text = prompt + text
        s = Drawable.String(w=self.lines, message=save_text, fontSize=22)
        w, h = s.get_size()

        # deal with output longer than one line
        if w > self.lines_width:
            try:
                t = Util.render_textrect(save_text, pygame.Rect(0, 0, self.lines_width, 1500), fontSize=22, trim=1)
                s = Drawable.Image(image=t)
            except Exception, e:
                s = Drawable.String(w=self.lines, message='Output too long for this window...', fontSize=22)
            w, h = s.get_size()
        s.set_position((5, self.lines_position))
        self.lines_position += h

        if self.lines_position > self.lines_height - 50:
            # starting to run out of room in the lines surface...
            # i am not sure how large to make this or if i should
            # bother trying to extend it if it starts to get full.
            Util.beep()

        s = Drawable.Stationary(w=self.lines, sprite=s)
        s.draw()
        self.lines.clear()
        self.lines.nudge(dy=-h)
        self.lines.udraw()

    def write(self, text):
        self.handle_print(text)

    def handle_print(self, text):
        text = text.strip()
        lines = str(text).split('\n')
        for line in lines:
            self.new_line(line, prompt='')

    def handle_pageup(self, pygame_event=None):
        self.paged_up += self.lines_per_screen
        self.lines.clear()
        self.lines.nudge(dy=self.lines_per_screen)
        self.lines.udraw()

    def handle_pagedown(self, pygame_event=None):
        self.paged_up -= self.lines_per_screen
        if self.paged_up >= 0:
            self.lines.clear()
            self.lines.nudge(dy=-self.lines_per_screen)
            self.lines.udraw()
        else:
            self.paged_up = 0
            Util.beep()

        if self.paged_up == 0:
            self.line.udraw()

    def handle_exception(self, e):
        for line in str(e).split('\n'):
            self.new_line(line, prompt='')
        self.line.prompt = '>>> '

    def run_command(self, text):
        """Process the next line of input.

        This is called when the user presses ENTER in the console widget.
        If this new text completes a command, the command is executed,
        otherwise this text is added to a buffer awaiting the next line.

        @param text: The next line of input. Does not include the newline.

        """

        if text:
            self.history.append(text)
            self.history_curr_index = len(self.history)

        self.new_line(text, self.line.prompt)

        self.buffer.append(text)
        command = '\n'.join(self.buffer)

        sys.stdout = self
        sys.stderr = self
        code = None
        try:
            code = compile_command(command)
        except Exception, e:
            self.handle_exception(e)
            self.buffer = []
        else:
            if code is not None:
                self.deactivate()
                try:
                    self.terp.runcode(code)
                except SyntaxError, e:
                    self.handle_exception(e)
                except Exception, e:
                    self.handle_exception(e)
                self.buffer = []
                self.line.prompt = '>>> '
                self.activate()
            else:
                self.line.prompt = '... '

        sys.stdout = self.save_stdout
        sys.stderr = self.save_stderr

    def toggle_visible(self, pygame_event):
        if self.active:
            self.deactivate()
        else:
            self.activate()

    def history_prev(self, pygame_event):
        if self.history_curr_index == len(self.history):
            self.partial_line = self.line.text_content
        self.history_curr_index -= 1
        if self.history_curr_index < 0:
            Util.beep()
            self.history_curr_index = 0

        if self.history:
            text = self.history[self.history_curr_index]
            self.line.set_text(text)

    def history_next(self, pygame_event):
        self.history_curr_index += 1
        if self.history_curr_index > len(self.history)-1:
            if self.line.text_content == self.partial_line:
                Util.beep()
            self.history_curr_index = len(self.history)
            self.line.set_text(self.partial_line)

        elif self.history:
            text = self.history[self.history_curr_index]
            self.line.set_text(text)

        else:
            Util.beep()

    def set_modal_events(self):
        self.quit_ev = Event.QUIT_Event(callback=self._quit)
        self.events.add(self.quit_ev)
        self.stop_ev = Event.KEYUP_Event(key=K_ESCAPE, callback=self._stop)
        self.events.add(self.stop_ev)

    def modal(self):
        self.activate()

        self.set_modal_events()

        self.new_line('Press ESC to close console')

        self.line.udraw()

        self.stop = 0
        while not self.stop:
            try:
                conf.ticks = min(20, conf.game.clock.tick(conf.MAX_FPS))
            except AttributeError:
                conf.ticks = 20
            self.layer.clear()
            self.events.check()
            if self.active:
                self.line.udraw()
                self.layer.udraw()

            if not self.line.repeater.key_held and not self.stop:
                ev = pygame.event.wait()
                pygame.event.post(ev)

        self.quit_ev.kill()
        self.stop_ev.kill()
        self.layer.uclear()

        self.deactivate()


class EscCatcher(Widget):
    def __init__(self, callback=None):
        if callback is None:
            callback = self._quit
        self.set_callback(callback)
        Event.KEYDOWN_Event(self.escape)

    def escape(self, pygameEvent):
        key = pygameEvent.key
        if key == K_ESCAPE:
            self.callback(self)

    def _quit(self, pygame_event=None):
        import sys
        sys.exit()
