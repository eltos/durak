
class Trash:
    DECK36 = range(6,15)
    DECK52 = range(2,15)

    def __init__(self):
        self.cards = []

    def get_cards(self):
        return self.cards

    def add_cards(self, cards):
        self.cards += cards

    def take_cards(self, deck=None):
        cards = []
        i = 0
        while i < len(self.cards):
            if deck is None or self.cards[i].name in deck:
                cards.append(self.cards.pop(i))
            else:
                i += 1
        return cards

    def __str__(self):
        return 'Ablagestapel mit %i Karten' % (len(self.cards))
