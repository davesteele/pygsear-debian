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

from distutils.core import setup
from distutils.command.install_data import install_data

#data installer with improved intelligence over distutils
#data files are copied into the project directory instead
#of willy-nilly (( FROM PYGAME ))
class smart_install_data(install_data):
    def run(self):
        #need to change self.install_dir to the actual library dir
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        return install_data.run(self)


setup(name="pygsear",
           version="0.53.2",
           description="Simple Pygame API",
           author="Lee Harr",
           author_email="lee@easthighschool.net",
           license="GNU General Public License (GPL)",
           url="http://savannah.nongnu.org/projects/pygsear/",
           packages=['pygsear'],
           cmdclass={'install_data': smart_install_data},
           data_files=[
                        ['pygsear/libdata/images',
                            ['pygsear/libdata/images/None.png',
                            'pygsear/libdata/images/turtle.png',
                            'pygsear/libdata/images/pygsear_logo.png']
                        ],

                        ['pygsear/libdata/sounds',
                            ['pygsear/libdata/sounds/test_sound.wav']
                        ]
            ]
)

