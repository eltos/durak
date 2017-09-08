
class Trash:
    def __init__(self):
        self.cards = []

    def get_cards(self):
        return self.cards

    def add_cards(self, cards):
        self.cards += cards

    def take_cards(self):
        cards = self.cards[:]
        self.cards = []
        return cards

    def __str__(self):
        return 'Ablagestapel mit %i Karten' % (len(self.cards))
