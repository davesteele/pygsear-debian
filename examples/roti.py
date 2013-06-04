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

from pygsear import Game, Drawable, conf

class AGame(Game.Game):
    def initialize(self):
        CENTER = (conf.WINWIDTH/2, conf.WINHEIGHT/2)

        bar = Drawable.Rectangle(width=75, height=5)

        bar.set_color('random')
        self.rbar0 = Drawable.RotatedImage(image=bar.image, steps=60)
        self.rbar0.set_position((400, 375))
        self.sprites.add(self.rbar0)

        bar.set_color('random')
        self.rbar1 = Drawable.RotatedImage(image=bar.image, steps=60, cy=60)        
        self.rbar1.set_position((420, 150))
        self.sprites.add(self.rbar1)

        bar.set_color('random')
        self.rbar2 = Drawable.RotatedImage(image=bar.image, steps=60, cx=-50)
        self.rbar2.set_position((160, 160))
        self.sprites.add(self.rbar2)
    
        bar.set_color('random')
        self.rbar3 = Drawable.RotatedImage(image=bar.image, steps=60, cx=20)
        self.rbar3.set_position((175, 315))
        self.sprites.add(self.rbar3)

    def checkCollisions(self):
        self.rbar0.flip()
        self.rbar1.flip()
        self.rbar2.flip()
        self.rbar3.flip()


if __name__ == '__main__':
    game = AGame()
    game.mainloop()

