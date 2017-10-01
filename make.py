#!/usr/bin/python

from PyInstaller.__main__ import run
import platform

arch = platform.system().lower() + "_" + platform.architecture()[0].lower()
delimiter = ";" if platform.system().lower() == 'windows' else ':'



run((
    '--windowed',
    '--distpath', 'build',
    '--workpath', 'build/tmp',
    '--clean',
    '--icon', 'D.ico',
    '--add-data', 'D.ico%s.' % delimiter,
    '--add-data', 'D.png%s.' % delimiter,
    '--add-data', 'themes%sthemes' % delimiter,
    '--add-data', 'translations%stranslations' % delimiter,
    '-n', 'durak_%s' % (arch),
    '-F', 'durak.pyw'
))
