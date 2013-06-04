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

"""Keyboard and mouse event handling.

This module is used to create objects that relate raw pygame events
(keys being pressed on the keyboard, mouse buttons being clicked,
the pygame window being closed, joystick movement (incomplete))
with other object methods and functions.

For instance, in your game you may want to use a control where every
time the up arrow is pressed on the keyboard, your player's ship
starts to accelerate.  That might look something like::

    class Ship:
        def initialize(self):
            self.events.add(Event.KEYDOWN_Event(key=K_UP, callback=self.accel))

Actually controlling the ship is a bit more complicated than this, since
you probably want the player to be able to hold down the arrow to keep
on accelerating. See some of the examples for more ideas on how to do that.

"""

import pygame
from pygame.locals import KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, QUIT
from pygame.locals import K_LSHIFT, K_RSHIFT, K_LCTRL, K_RCTRL, K_LALT, K_RALT
MODIFIERS = [K_LSHIFT, K_RSHIFT, K_LCTRL, K_RCTRL, K_LALT, K_RALT]

TIMEOUT = -1
KEY = -2
MOUSEBUTTON = -4

import conf


class Event(pygame.sprite.Sprite):
    """Relates Pygame Events with related actions."""

    def __init__(self, type, callback=None, **kwargs):
        """Initialize the event.

        @param type: L{pygame.event} type. Currently this includes
            C{KEYDOWN}, C{KEYUP}, C{MOUSEBUTTONDOWN}, C{MOUSEBUTTONUP}, and
            C{QUIT}
        @param callback: Function or method to call when the event occurs.
        @param kwargs: Additional parameters that should be passed on to
            the callback.

        """

        if kwargs.has_key('group'):
            group = kwargs['group']
            del(kwargs['group'])
        else:
            group = ()
        pygame.sprite.Sprite.__init__(self, group)

        self.type = type
        try:
            for t in type:
                if t > 0:
                    pygame.event.set_allowed(t)
        except TypeError:
            if type > 0:
                pygame.event.set_allowed(type)

        if callback is None:
            self.callback = self.nop
        else:
            self.callback = callback
        self.kwargs = kwargs

        self.enable()

    def add(self, group):
        """Add this L{Event} to an L{EventGroup}."""

        if group:
            pygame.sprite.Sprite.add(self, group)

    def enable(self):
        """Allow callbacks to go through."""

        self.enabled = 1

    def disable(self):
        """Do not allow callbacks to go through."""

        self.enabled = 0

    def nop(self, ev, **kwargs):
        """Do nothing."""

        pass

    def call(self, pygame_event, **kwargs):
        """Perform the callback, if enabled.

        @param pygame_event: The actual L{pygame.event.Event} that
            triggered this Event.
        @param kwargs: Additional parameters that should be passed
            on to the callback. Note that keyword args included here
            will overwrite those added at the creation of the event.

        """

        kwargs.update(self.kwargs)
        if self.enabled:
            self.callback(pygame_event, **kwargs)


class QUIT_Event(Event):
    def __init__(self, callback, **kwargs):
        """Initialize a QUIT Event

        The QUIT event is generated when the window close button is clicked.

        @param callback: Function or method to call when the event occurs.
        @param kwargs: Additional parameters that should be passed on to
            the callback.

        """

        Event.__init__(self, QUIT, callback, **kwargs)


class KEY_Event(Event):
    """Keyboard events."""

    def __init__(self, type=KEY, key=None, callback=None, on_press=None, on_hold=None, on_release=None, **kwargs):
        """Initialize a keyboard event.

        @param type: L{pygame.event} type. Should be C{KEYDOWN} or C{KEYUP}
        @param key: The keyboard key which will trigger this event, or a
            sequence of keys. (I{B{ie:} Pressing any one of these keys will
            trigger the event}) If key is C{None} then any keypress will
            fire the callback.
        @param callback: Function or method to call when the event occurs.
        @param on_press: Function to call when key is first pressed
        @param on_hold: Function to call while key is being held down. Will be
            called once for each pass through the game's mainloop. I am not yet
            convinced that C{on_hold} is going to be useful at all.
        @param on_release: Function to call when key is finally released
        @param kwargs: Additional parameters that should be passed on to
            the callback.

        """

        if type == KEY:
            g = EventGroup()

            if callback is not None:
                g.add(KEYDOWN_Event(key=key, callback=callback, **kwargs))
                g.add(KEYUP_Event(key=key, callback=callback, **kwargs))
            if on_press is not None:
                g.add(KEYDOWN_Event(key=key, callback=on_press, **kwargs))
            if on_release is not None:
                g.add(KEYUP_Event(key=key, callback=on_release, **kwargs))
            if on_hold is not None:
                g.add(TIMEOUT_Event(0, count=-1, callback=self.check_holding, **kwargs))
                g.add(KEYDOWN_Event(key=key, callback=self.press))
                g.add(KEYUP_Event(key=key, callback=self.release))
                self.key_held = 0

            self.contains = g
        else:
            self.contains = None

        Event.__init__(self, type, callback, **kwargs)

        self.on_press = on_press
        self.on_hold = on_hold
        self.on_release = on_release

        try:
            len(key)
            self.key = key
        except TypeError:
            if key is not None:
                self.key = [key]
            else:
                self.key = None

    def press(self, ev, **kwargs):
        self.key_held = 1

    def release(self, ev, **kwargs):
        self.key_held = 0

    def check_holding(self, ev, **kwargs):
        if self.key_held:
            self.on_hold(ev, **kwargs)

    def call(self, pygame_event, **kwargs):
        """Perform the callback, if the event is enabled, and the key
        pressed is the right key.

        @param pygame_event: The actual L{pygame.event.Event} that
            triggered this Event.
        @param kwargs: Additional parameters that should be passed
            on to the callback. Note that keyword args included here
            will overwrite those added at the creation of the event.

        """

        if hasattr(pygame_event, 'key'):
            key = pygame_event.key
        else:
            raise TypeError

        #print 'calling key', self.key, pygame_event, self.callback
        if self.key is None or key in self.key:
            if self.contains is None:
                Event.call(self, pygame_event, **kwargs)
            else:
                pygame_event_type = pygame_event.type
                for event in self.contains.events():
                    event_type = event.type
                    if pygame_event_type == event_type:
                        event.call(pygame_event, **kwargs)


class KEYDOWN_Event(KEY_Event):
    def __init__(self, key=None, callback=None, **kwargs):
        """Initialize a KEYDOWN event.

        The KEYDOWN is generated when the key is first pressed. Any key can
        generate a KEYDOWN event, it has nothing in particular to do with
        the up and down arrows on the keyboard.

        @param key: The keyboard key which will trigger this event, or a
            sequence of keys. (I{B{ie:} Pressing any one of these keys will
            trigger the event}) If key is C{None} then any keypress will
            fire the callback.
        @param callback: Function or method to call when the event occurs.
        @param kwargs: Additional parameters that should be passed on to
            the callback.

        """

        KEY_Event.__init__(self, KEYDOWN, key, callback, **kwargs)


class KEYUP_Event(KEY_Event):
    def __init__(self, key=None, callback=None, **kwargs):
        """Initialize a KEYUP Event

        The KEYUP is generated when the key is released. Any key can
        generate a KEYUP event, it has nothing in particular to do with
        the up and down arrows on the keyboard.

        @param key: The keyboard key which will trigger this event, or a
            sequence of keys. (I{B{ie:} Pressing any one of these keys will
            trigger the event}) If key is C{None} then any keypress will
            fire the callback.
        @param callback: Function or method to call when the event occurs.
        @param kwargs: Additional parameters that should be passed on to
            the callback.

        """

        KEY_Event.__init__(self, KEYUP, key, callback, **kwargs)


class Repeat_KEY_Event(KEY_Event):
    """KEY_Event which will auto-repeat after a delay.

    if no C{key} parameter is passed in, this Event will listen for all keyboard
    keypress events. Since the only thing I am using this for right now is for
    text input, I made the behavior somewhat like a command line interface.
    Specifically: shift, alt, and ctrl are treated specially and will not
    repeat. I considered keeping track of a C{dict} of active keypress, but
    it seemed like much work for little gain. It should not be too difficult
    though if someone needs that functionality.

    """

    def __init__(self, key=None, on_press=None, on_hold=None, on_release=None,
                    delay=400, period=50, **kwargs):
        """Initialize a keyboard event that will auto-repeat when the key is held.

        @param key: The keyboard key which will trigger this event, or a
            sequence of keys. (I{B{ie:} Pressing any one of these keys will
            trigger the event}) If key is C{None} then any keypress will
            fire the callback.
        @param on_press: Function to call when key is first pressed
        @param on_hold: Function to call while key is being held down. Will be
            called once every C{period} milliseconds after C{delay} milliseconds.
        @param on_release: Function to call when key is finally released
        @param delay: Time to wait before starting auto-repeat (in milliseconds)
        @param period: Time between auto-repeat calls to C{on_hold}(in milliseconds)
        @param kwargs: Additional parameters that should be passed on to
            the callback.

        """

        KEY_Event.__init__(self, KEY, key=key, on_press=self.rpress, on_hold=self.rhold,
                                on_release=self.rrelease, **kwargs)
        if on_press is None:
            on_press = self.nop
        if on_hold is None:
            on_hold = self.nop
        if on_release is None:
            on_release = self.nop

        self._on_press = on_press
        self._on_hold = on_hold
        self._on_release = on_release
        self.delay = delay
        self._ticks = delay
        self._holding = 0
        self._repeating = 0
        self.period = period

    def press(self, ev):
        """Do nothing, so we can handle the on_hold a different way here."""
        pass

    def release(self, ev):
        """Do nothing, so we can handle the on_hold a different way here."""
        pass

    def rpress(self, ev):
        """Start counting down the delay time until auto-repeat kicks in."""

        if self.key is not None or ev.key not in MODIFIERS:
            self.key_held = 1
            self._ev = ev
            self._ticks = self.delay
            self._on_press(ev)
            self._on_hold(ev)

    def rhold(self, ev):
        """Call the callback at the requested interval."""

        if self.key_held:
            if not self._repeating:
                self._ticks -= conf.ticks
                if self._ticks < 0:
                    self._repeating = 1
                    self._tocks = self.period
            else:
                self._tocks -= conf.ticks
                if self._tocks < 0:
                    self._on_hold(self._ev)
                    self._tocks = self.period


    def rrelease(self, ev):
        """Reset the counters."""

        if self.key is not None or ev.key not in MODIFIERS:
            self.key_held = 0
            self._repeating = 0
            self._on_release(ev)



class MOUSEBUTTON_Event(Event):
    """Mouse button events."""

    def __init__(self, type, button, callback=None, **kwargs):
        """Initialize a mouse Event

        @param type: L{pygame.event} type. Should be C{MOUSEBUTTONDOWN}
            or C{MOUSEBUTTONUP}
        @param button: The mouse button which will trigger this event, or a
            sequence of buttons. (I{B{ie:} Pressing any one of these buttons
            will trigger the event})
        @param callback: Function or method to call when the event occurs.
        @param kwargs: Additional parameters that should be passed on to
            the callback.

        """

        Event.__init__(self, type, callback, **kwargs)
        try:
            len(button)
            self.button = button
        except TypeError:
            self.button = [button]

    def call(self, pygame_event, **kwargs):
        """Perform the callback, if the event is enabled, and the mouse
        button pressed is the correct button.

        @param pygame_event: The actual L{pygame.event.Event} that
            triggered this Event.
        @param kwargs: Additional parameters that should be passed
            on to the callback. Note that keyword args included here
            will overwrite those added at the creation of the event.

        """

        #         if hasattr(pygame_event, 'button'):
        #             button = pygame_event.button
        #         else:
        #             raise TypeError
        #
        button = pygame_event.button
        if button in self.button:
            Event.call(self, pygame_event, **kwargs)


class MOUSEBUTTONDOWN_Event(MOUSEBUTTON_Event):
    def __init__(self, button=None, callback=None, **kwargs):
        """Initialize a MOUSEBUTTONDOWN event.

        The MOUSEBUTTONDOWN event is generated when the mouse button is first
        pressed.

        @param button: The mouse button which will trigger this event, or a
            sequence of buttons. (I{B{ie:} Pressing any one of these buttons
            will trigger the event}) If button is C{None} it is assumed
            that the left mouse button (button 1) is the intended button.
        @param callback: Function or method to call when the event occurs.
        @param kwargs: Additional parameters that should be passed on to
            the callback.

        """

        if callback is None:
            raise TypeError
        if button is None:
            button = [1]
        MOUSEBUTTON_Event.__init__(self, MOUSEBUTTONDOWN, button, callback, **kwargs)


class MOUSEBUTTONUP_Event(MOUSEBUTTON_Event):
    def __init__(self, button=None, callback=None, **kwargs):
        """Initialize a MOUSEBUTTONDOWN Event

        @param button: The mouse button which will trigger this event, or a
            sequence of buttons. (I{B{ie:} Pressing any one of these buttons
            will trigger the event}) If button is C{None} it is assumed
            that the left mouse button (button 1) is the intended button.
        @param callback: Function or method to call when the event occurs.
        @param kwargs: Additional parameters that should be passed on to
            the callback.

        """

        if callback is None:
            raise TypeError
        if button is None:
            button = [1]
        MOUSEBUTTON_Event.__init__(self, MOUSEBUTTONUP, button, callback, **kwargs)


class TIMEOUT_Event(Event):
    def __init__(self, delay, count=1, callback=None, keepalive=False, **kwargs):
        """Initialize a TIMEOUT Event

        Note that using a TIMEOUT_Event can conflict with too low a setting
        of C{conf.MAX_TICKS} causing events to fire "too soon" on overloaded
        systems. (BUT this should be fixed now...)

        @param delay: Time in milliseconds before firing the callback.
        @param count: Number of times to repeat the event. A count of C{-1}
            indicates that the event should repeat forever.
        @param callback: Function or method to call when the event occurs.
        @param keepalive: If C{True}, do not C{kill} the event when C{call}ing.
        @param kwargs: Additional parameters that should be passed on to
            the callback.

        """

        Event.__init__(self, TIMEOUT, callback, **kwargs)
        self.delay = delay
        self.count_original = count
        self.keepalive = keepalive

        self.reset()

    def reset(self):
        """Reset the Event to its initial state."""

        self.ticks = self.delay
        self.set_count(self.count_original)
        self.enable()

    def set_count(self, count=1):
        self.count = count

    def tick(self, ticks):
        """Count down ticks until time to call.

        @param ticks: Number of ticks since last checked.

        """

        self.ticks -= ticks
        if self.ticks < 0:
            self.call(None)

    def call(self, pygame_event, **kwargs):
        """Make the Event callback, then either count down calls or disable.

        If the C{count} on this Event reaches C{0}, it will be L{Event.disable}d.
        If C{keepalive} is C{False} it will also be L{pygame.sprite.Sprite.kill}ed.
        Note that this means it will have to be added to your L{EventGroup} again if
        you want to re-use the Event. This was done to avoid ending up with many
        disabled events in the event group.

        @param pygame_event: Pygame event making the call. I{NOT USED}
            If called from L{tick}. Instead it will be passed C{None}.
        @param kwargs: Additional parameters that should be passed on to
            the callback.

        """

        Event.call(self, pygame_event, **kwargs)
        self.ticks = self.delay
        if self.count > 0:
            self.count -= 1

        if self.count == 0:
            self.disable()
            if not self.keepalive:
                self.kill()


class EventGroup(pygame.sprite.Group):
    """Used to group related events."""

    def __init__(self, event=()):
        """Initialize the Group.

        @param event: L{Event} to add to the Group initially, or
            a sequence of events to add.

        """

        pygame.sprite.Group.__init__(self, event)

        self.TIMEOUT_Events = pygame.sprite.Group()

    def add(self, event):
        """Add the event to the container.

        @param event: L{Event} to add, or a sequence of events to add.

        """

        pygame.sprite.Group.add(self, event)

        if hasattr(event, 'events'):
            events = event.events()
        else:
            try:
                len(event)
                events = event
            except TypeError:
                events=[event]

        for event in events:
            try:
                event_type = event.type
            except AttributeError:
                pass
            else:
                if event_type == TIMEOUT:
                    self.TIMEOUT_Events.add(event)

                elif event_type == KEY:
                    for ev in event.contains.sprites():
                        self.add(ev)

    def events(self):
        """return a list of all events in this group."""

        return self.sprites()

    def enable(self):
        """Allow callbacks to all events in this group to go through."""

        for event in self.events():
            event.enable()

    def disable(self):
        """Do not allow callbacks to any sprites in this group to go
        through.

        """

        for event in self.events():
            event.disable()

    def check(self):
        """Go through the pygame event queue and callback to events that
        should be triggered.

        Also checks the special C{TIMEOUT_Events} queue, but only if any
        TIMEOUT_Events have been added to the group.

        I{B{Note:} This empties the queue.}

        """

        for pygame_event in pygame.event.get():
            pygame_event_type = pygame_event.type
            for event in self.events():
                event_type = event.type
                if pygame_event_type == event_type:
                    event.call(pygame_event)

        if self.TIMEOUT_Events:
            ticks = conf.ticks
            for event in self.TIMEOUT_Events.sprites():
                event.tick(ticks)

    def kill(self):
        """Call the C{kill} method on every event in this group, to remove
        all of the events from all of the groups they are in.

        """

        for event in self.events():
            event.disable()
            event.kill()

        # This should not be needed ... ?
        for event in self.TIMEOUT_Events.sprites():
            event.disable()
            event.kill()
