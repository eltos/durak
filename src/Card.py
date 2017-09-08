# coding=utf-8

class Card:
    # card-colors
    KARO = 0
    HERZ = 1
    PIK = 2
    KREUZ = 3

    # card-names
    ZWEI = 2
    DREI = 3
    VIER = 4
    FUENF = 5
    SECHS = 6
    SIEBEN = 7
    ACHT = 8
    NEUN = 9
    ZEHN = 10
    BUBE = 11
    DAME = 12
    KOENIG = 13
    ASS = 14

    def __init__(self, color, name, is_trump=False):
        self.color = color
        self.name = name
        self.trump = is_trump

    def maketrump(self, is_trump=True):
        self.trump = is_trump

    def get_color(self):
        return self.color

    def get_name(self):
        return self.name

    def is_trump(self):
        return self.trump

    def __cmp__(self, other):
        if type(self) != type(other): raise Exception('Can not compare %s and %s' % (type(self), type(other)))
        return self.name + 15 * self.trump - (other.name + 15 * other.trump)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return hash(self) != hash(other)

    def __hash__(self):
        return (self.color * 100 + self.name)

    def __str__(self):
        color = {0: 'Karo',
                 1: 'Herz',
                 2: 'Pik',
                 3: 'Kreuz'}[self.color]
        name = {2: '2',
                3: '3',
                4: '4',
                5: '5',
                6: '6',
                7: '7',
                8: '8',
                9: '9',
                10: '10',
                11: 'Bube',
                12: 'Dame',
                13: 'König',
                14: 'Ass'}[self.name]

        return color + ' ' + name
