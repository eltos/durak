import pickle, os
from PyQt4 import QtGui, QtCore



class Settings():
    SETTINGS_FILE = None
    THEME_DIR = None

    def __init__(self):
        self.__theme = '-'
        self.__animation_duration = 500
        self.__is_fulscreen = False
        self.__full_deck = False
        self.load()
        self.load_resources()

    def save(self):
        f = open(Settings.SETTINGS_FILE, 'w')
        pickle.dump(
            {'theme': self.__theme,
             'fs': self.__is_fulscreen,
             'full': self.__full_deck
             }, f)
        f.close()

    def load(self):
        try:
            f = open(Settings.SETTINGS_FILE, 'r')
            tmp = pickle.load(f)
            f.close()
            if 'theme' in tmp: self.__theme = tmp['theme']
            if 'fs' in tmp: self.__is_fulscreen = tmp['fs']
            if 'full' in tmp: self.__full_deck = tmp['full']
        except IOError:
            pass

        if not QtCore.QDir(os.path.join(Settings.THEME_DIR, self.__theme)).exists():
            themesdir = QtCore.QDir(Settings.THEME_DIR)
            themes = themesdir.entryList(filters=QtCore.QDir.AllDirs)
            themes.removeAt(themes.indexOf('.'))
            themes.removeAt(themes.indexOf('..'))
            if len(themes) >= 1:
                self.__theme = str(themes[0])
            else:
                print 'Error'
                print 'No themes were found in: ', Settings.THEME_DIR
                raise IOError('No theme files')

    def setTheme(self, theme):
        self.__theme = str(theme)

    def getTheme(self):
        return self.__theme

    def getAnimationDuration(self):
        return self.__animation_duration

    def setAnimationDuration(self, ms):
        self.__animation_duration = ms

    def isFullscreen(self):
        return self.__is_fulscreen

    def setFullscreen(self, fs):
        self.__is_fulscreen = fs

    def toggleFullscreen(self):
        self.__is_fulscreen = not self.__is_fulscreen
        return self.isFullscreen()

    def isFullDeck(self):
        return self.__full_deck

    def setFullDeck(self, full):
        self.__full_deck = full

    def load_resources(self):
        self.resources = {'playing_cards_back': QtGui.QImage(os.path.join(Settings.THEME_DIR, self.__theme, 'playing_cards_back.png')),
                          'playing_cards': QtGui.QImage(os.path.join(Settings.THEME_DIR, self.__theme, 'playing_cards.png')),
                          'playing_symbols': QtGui.QImage(os.path.join(Settings.THEME_DIR, self.__theme, 'symbols.png')),
                          'background': QtGui.QImage(os.path.join(Settings.THEME_DIR, self.__theme, 'background.png')),
                          'seats': QtGui.QImage(os.path.join(Settings.THEME_DIR, self.__theme, 'seats.png')),
                          'seats_large': QtGui.QImage(os.path.join(Settings.THEME_DIR, self.__theme, 'seats_large.png')),
                          'table': QtGui.QImage(os.path.join(Settings.THEME_DIR, self.__theme, 'table.png')),
                          'stack': QtGui.QImage(os.path.join(Settings.THEME_DIR, self.__theme, 'stack.png'))
                          }
        self.colors = {'font': QtGui.QColor(50, 29, 17),
                       'font disabled': QtGui.QColor(102, 60, 35),
                       'button': QtGui.QColor(149, 96, 56),
                       'button highlight': QtGui.QColor(124, 73, 43),
                       'button blink': QtGui.QColor(255, 200, 0)
                       }
        try:
            f = open(os.path.join(Settings.THEME_DIR, self.__theme, 'colors'), 'r')
            self.colors.update(pickle.load(f))
            f.close()
        except:
            pass

