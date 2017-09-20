import random


class Stack:
    def __init__(self):
        self.cards = []
        self.trump = None

    def get_trump(self):
        '''returns current trump'''
        return self.trump

    def get_cards(self):
        return self.cards

    def reset(self):
        raise NotImplemented
        self.cards = []
        # generate 36 cards
        for color in range(4):
            for name in range(6, 15):
                self.cards += [Card(color, name)]
        self.trump = self.cards[-1].get_color()

    def add_cards(self, cards):
        self.cards += cards
        if len(self.cards) > 0:
            self.trump = self.cards[-1].get_color()

    def shuffle(self):
        '''shuffles cards'''
        random.shuffle(self.cards)
        self.trump = self.cards[-1].get_color()

    def set_value_by_trump(self):
        '''make the trump-cards know what they are'''
        for card in self.cards:
            card.maketrump(card.get_color() == self.trump)

    def take(self, number=1):
        cards = self.cards[:number]
        self.cards = self.cards[number:]
        return cards

    def take_all_cards(self):
        cards = self.cards[:]
        self.cards = []
        return cards

    def size(self):
        return len(self.cards)

    def __str__(self):
        color = {0: 'Karo',
                1: 'Herz',
                2: 'Pik',
                3: 'Kreuz',
                None: 'Nichts'}[self.trump]
        return 'Stapel mit %i Karten (%s ist Trumpf)'%(self.size(), color)
