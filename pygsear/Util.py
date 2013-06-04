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

"""Utilities for finding and loading different resources"""

import sys
import os
import random

import pygame

import Sound
from locals import *
import conf


dirs_cache = {}
def get_dirs(type=None):
    """return a list of potential data directories.

    Looks around at possible locations, and returns possible
    data directories in this order:

        1. The current working directory.
        2. The "home" directory, where the main (invoked) script lives.
            I{B{NOTE:} Not the user's home directory!}
        3. The C{data/I{type}} directory underneath the "home" directory
        4. The C{data} directory underneath the "home" directory
        5. The C{libdata/I{type}} directory underneath the pygsear lib directory.
        6. The C{libdata} directory underneath the pygsear lib directory.

    """

    global dirs_cache
    if dirs_cache.has_key(type):
        return dirs_cache[type]

    else:
        dirs = []

        # the current working directory (cwd)
        cwd = os.path.abspath('.')
        dirs.append(cwd)

        # the directory the invoked script is in
        home = os.path.abspath(os.path.dirname(sys.argv[0]))
        if home not in dirs:
            dirs.append(home)

        # the data directory with the invoking script
        data = os.path.join(home, 'data')

        # the specific data type directory under data
        if type is not None:
            datatype = os.path.join(data, type)
            if os.path.isdir(datatype) and datatype not in dirs:
                dirs.append(datatype)
            else:
                pass
                #print 'not adding', datatype

        if os.path.isdir(data) and data not in dirs:
            dirs.append(data)


        # the libdata directory with the library files
        libdir, extra = os.path.split(__file__)
        libdata = os.path.join(libdir, 'libdata')

        # the specific data type directory under libdata
        if type is not None:
            libdatatype = os.path.join(libdata, type)
            if os.path.isdir(libdatatype) and libdatatype not in dirs:
                dirs.append(libdatatype)
            else:
                pass
                #print 'not adding', libdatatype

        if os.path.isdir(libdata) and libdata not in dirs:
            dirs.append(libdata)

        dirs_cache[type] = dirs
        return dirs


def get_full_path(filename, dirs):
    """return the first existing file found in dirs.

    @param filename: Name of file to find in dirs.
    @param dirs: List of directories to search.

    """

    for dir in dirs:
        full_path = os.path.join(dir, filename)
        if os.path.exists(full_path):
            return full_path


image_cache = {}
def load_image(filename, convert=1):
    """Return pygame surface from filename string.

    Uses L{get_dirs} to know where to look for the file.

    @param filename: Name of image file to load data from.
    @param convert: Optimize if True. I{Can sometimes cause
        colorspace problems...}
        Will not convert if the image has an alpha mask.

    """

    global image_cache

    if image_cache.has_key(filename):
        image = image_cache[filename]

    else:
        dirs = get_dirs('images')

        full_path = get_full_path(filename, dirs)
        try:
            image = pygame.image.load(full_path)
        except pygame.error:
            image = None

        if image is None:
            raise pygame.error, 'Could not load %s' % filename

        image_cache[filename] = image

    alpha_mask = image.get_masks()
    if convert and not alpha_mask:
        image = image.convert()

    return image


def load_images(filenames=None, dirname=None, convert=1):
    """Return list of pygame surfaces.

    Must pass either list of filenames, or name of directory
    from which to load all images.

    Uses L{get_dirs} to know where to look for the file or
    directory.

    @param filenames: List of image file names to load data from.
    @param dirname: Name of directory from which to load all images.
    @param convert: Optimize if True. I{Can sometimes cause
        colorspace problems...}

    """

    images = []

    if dirname is not None:
        dirs = get_dirs('images')
        for dir in dirs:
            full_dirpath = os.path.join(dir, dirname)
            if os.path.isdir(full_dirpath):
                filenames = os.listdir(full_dirpath)
                for filename in filenames:
                    full_imagepath = os.path.join(full_dirpath, filename)
                    try:
                        image = load_image(full_imagepath, convert)
                    except pygame.error:
                        # must not be an image
                        # might be a CVS, .xvpics or .svn directory
                        pass
                    else:
                        images.append(image)
                break

    elif filenames is not None:
        for filename in filenames:
            images.append(load_image(filename, convert))

    else:
        raise TypeError, 'must give filenames, or dirname'

    return images


def load_images_dict(filenames=None, dirname=None, convert=1):
    """Return dict of C{filename: image} pygame surfaces.

    Must pass either a list of filenames or the name of a directory
    from which to load all images.

    Uses L{get_dirs} to know where to look for the file or directory.

    @param filenames: List of image file names to load data from.
    @param dirname: Name of directory from which to load all images.
    @param convert: Optimize if True. I{Can sometimes cause
        colorspace problems...}

    """

    images = {}

    if dirname is not None:
        dirs = get_dirs('images')
        for dir in dirs:
            full_dirpath = os.path.join(dir, dirname)
            if os.path.isdir(full_dirpath):
                filenames = os.listdir(full_dirpath)
                if 'CVS' in filenames:
                    filenames.remove('CVS')
                if '.xvpics' in filenames:
                    filenames.remove('.xvpics')
                for filename in filenames:
                    full_imagepath = os.path.join(full_dirpath, filename)
                    images[filename] = load_image(full_imagepath, convert)
                break

    elif filenames is not None:
        for filename in filenames:
            images[filename] = load_image(filename, convert)

    else:
        images = {}

    return images


sound_cache = {}
def load_sound(filename):
    """Return pygame sound object.

    Sound file shoud be a C{.wav} file.

    Checks the status of the sound system first, and if there
    is a problem, hands out L{pygsear.Sound.DummySound} objects
    instead of actual L{pygame.mixer.Sound} objects.

    @param filename: Name of file to load data from.

    """

    global sound_cache

    if sound_cache.has_key(filename):
        sound = sound_cache[filename]
        return sound

    else:
        if conf.sound_status is None:
            Sound.check_sound()

        dirs = get_dirs('sounds')

        full_path = get_full_path(filename, dirs)
        try:
            if conf.sound_status == 'OK':
                sound = pygame.mixer.Sound(full_path)
            else:
                sound = Sound.DummySound()
        except pygame.error:
            sound = None

        if sound is None:
            raise pygame.error, 'Could not load %s' % filename

        #sound_cache[filename] = sound
        return sound


def beep():
    print chr(7)


point_cache = {}
def load_points(filename):
    """Return list of points C{(x, y)}.

    @param filename: Name of file to load data from.
        Data should be formatted as C{(x, y)} with
        one point per line.

    """

    global point_cache

    if point_cache.has_key(filename):
        points = point_cache[filename]
        return points

    else:
        dirs = get_dirs('paths')

        full_path = get_full_path(filename, dirs)
        try:
            f = file(full_path)
        except IOError:
            f = None

        if f is None:
            raise pygame.error, 'Could not load %s' % filename

        points = []
        for line in f.readlines():
            line = line.strip()
            xRaw, yRaw = line.split(',')
            x = int(xRaw[1:])
            y = int(yRaw[:-1])
            points.append((x, y))

        point_cache[filename] = points
        return points


# LINE INTERSECTION CODE IS
# ADAPTED FROM PYGAME PCR
DONT_INTERSECT = 0
COLINEAR = -1

def have_same_signs(a, b):
    """return True if both integers have the same signs.

    @param a: One number.
    @type a: int
    @param b: Another number.
    @type b: int

    """

    return ((a ^ b) >= 0)

def line_seg_intersect(line1point1, line1point2, line2point1, line2point2):
    """return True if 2 line segments intersect.

    @param line1point1: (x, y) coord of one end of first line
    @param line1point2: (x, y) coord of other end of first line
    @param line2point1: (x, y) coord of one end of second line
    @param line2point2: (x, y) coord of other end of second line

    """

    x1 = line1point1[0]
    y1 = line1point1[1]
    x2 = line1point2[0]
    y2 = line1point2[1]
    x3 = line2point1[0]
    y3 = line2point1[1]
    x4 = line2point2[0]
    y4 = line2point2[1]

    a1 = y2 - y1
    b1 = x1 - x2
    c1 = (x2 * y1) - (x1 * y2)

    r3 = (a1 * x3) + (b1 * y3) + c1
    r4 = (a1 * x4) + (b1 * y4) + c1

    if ((r3 != 0) and (r4 != 0) and ((r3 ^ r4) >= 0)):
        return(DONT_INTERSECT)

    a2 = y4 - y3
    b2 = x3 - x4
    c2 = x4 * y3 - x3 * y4

    r1 = a2 * x1 + b2 * y1 + c2
    r2 = a2 * x2 + b2 * y2 + c2

    if ((r1 != 0) and (r2 != 0) and ((r1 ^ r2) >= 0)):
         return(DONT_INTERSECT)

    denom = (a1 * b2) - (a2 * b1)
    if denom == 0:
        return(COLINEAR)
    elif denom < 0:
        offset = (-1 * denom / 2)
    else:
        offset = denom / 2

    num = (b1 * c2) - (b2 * c1)
    if num < 0:
        x = (num - offset) / denom
    else:
        x = (num + offset) / denom

    num = (a2 * c1) - (a1 * c2)
    if num <0:
        y = (num - offset) / denom
    else:
        y = (num - offset) / denom

    return (x, y)


def scale_image(img, width, height, keepAspectRatio=1):
    """return a scaled copy of a L{pygame.Surface}

    @param img: Original L{pygame.Surface}.
    @param width: width of returned surface.
    @param height: height of returned surface.
    @param keepAspectRatio: If True, the returned surface will be padded with
        transparent borders.

    """

    width = int(width)
    height = int(height)

    if keepAspectRatio:
        flags = img.get_flags()
        new_img = pygame.Surface((width, height), flags, img)

        img_w, img_h = img.get_size()
        ratio = float(img_w) / img_h
        new_ratio = float(width) / height

        colorkey = img.get_colorkey()
        if colorkey is None:
            colorkey = TRANSPARENT
        new_img.fill(colorkey)
        new_img.set_colorkey(colorkey)

        alpha = img.get_alpha()
        if alpha is not None:
            new_img.set_alpha(alpha)

        if ratio >= new_ratio:
            new_w = int(width)
            new_h = int(float(new_w) / ratio)
            x = 0
            y = (height - new_h) / 2
        else:
            new_h = int(height)
            new_w = int(float(new_h) * ratio)
            x = (width - new_w) / 2
            y = 0

        scaled_img = pygame.transform.scale(img, (new_w, new_h))
        new_img.blit(scaled_img, (x, y))

    else:
        new_img = pygame.transform.scale(img, (width, height))

    return new_img


def does_surface_have_pixel_alpha(surface):
    return surface.get_masks()[3] != 0


# WORD WRAPPED TEXT CODE IS
# ADAPTED FROM PYGAME PCR
class TextRectException(Exception):
    def __init__(self, message=None):
        self.message = message
    def __str__(self):
        return self.message

def render_textrect(string, rect, text_color=WHITE, bgcolor=BLACK, fontSize=20, justification=0, trim=0):
    """Returns a surface containing the passed text.

    The text string will be reformatted to fit within the given rect,
    word-wrapping as necessary. The text will be anti-aliased.

    Raises a C{TextRectException} if the text won't fit onto the surface.

    @returns: A surface object with the text rendered onto it.

    @param string: The text you wish to render. Newline character begins
        a new line.
    @param fontSize: A Font object
    @param rect: A rectstyle giving the size of the surface requested.
    @param text_color: RGB color tuple (ex (0, 0, 0) = BLACK)
    @param bgcolor: A three-byte tuple of the rgb value of the surface.
    @param justification: Alignment of the text in the rectangle
        - 0 (default) left-justified
        - 1 horizontally centered
        - 2 right-justified
    @param trim: If True, return a Surface just large enough to contain
        the text.

    """

    final_lines = []

    requested_lines = string.splitlines()

    # Create a series of lines that will fit on the provided
    # rectangle.

    font = pygame.font.Font(None, fontSize)

    for requested_line in requested_lines:
        if font.size(requested_line)[0] > rect.width:
            words = requested_line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.
                if font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(requested_line)

    # Let's try to write the text out on the surface.

    surface = pygame.Surface(rect.size)
    surface.fill(bgcolor)

    accumulated_height = 0
    for line in final_lines:
        if accumulated_height + font.size(line)[1] >= rect.height:
            raise TextRectException, "Once word-wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, text_color)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulated_height))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulated_height))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulated_height))
            else:
                raise TextRectException, "Invalid justification argument: " + str(justification)
        accumulated_height += font.size(line)[1]

    if not trim:
        return surface
    else:
        trimmed = pygame.Surface((rect.width, accumulated_height))
        trimmed.blit(surface, (0, 0))
        return trimmed



if pygame.color.THECOLORS:
    named_colors = pygame.color.THECOLORS
else:
    named_colors = {'white': WHITE,
                    'black': BLACK,
                    'blue': BLUE,
                    'red': RED,
                    'yellow': YELLOW,
                    'green': GREEN,
                    'orange': ORANGE,
                    'purple': PURPLE,
                    'lightred': LRED,
                    'lightgreen': LGREEN,
                    'lightblue': LBLUE,
                    'darkred': DRED,
                    'darkblue': DBLUE,
                    'darkgreen': DGREEN,
                    }

def color_lighten(color):
    return [int(color[c]+(255-color[c])*0.8) for c in range(3)]

def color_darken(color):
    return [int(color[c]*0.8) for c in range(3)]

def color(name, modifier=None):
    if name in named_colors.keys():
        acolor = list(named_colors[name])

    elif name == 'random':
        acolor = [random.randrange(256) for c in range(3)]

    else:
        acolor = pygame.color.Color(name)

    if modifier is not None:
        if modifier == 'light':
            while sum(acolor) < 600:
                acolor = color_lighten(acolor)
        elif modifier == 'dark':
            while sum(acolor) > 150:
                acolor = color_darken(acolor)
        elif modifier == 'medium':
            while sum(acolor) > 500:
                acolor = color_darken(acolor)
            while sum(acolor) < 250:
                acolor = color_lighten(acolor)
        else:
            raise TypeError, "Unknown modifier, " + modifier

    return tuple(acolor)













