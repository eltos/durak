

class Player:
    # type
    HUMAN = 0
    KI = 1

    def __init__(self, name, visible=False):
        self.name = name
        self.cards = []
        self.active = True
        self.score = [0, 0, None]  # score, played games, last place
        # score depending on place, first: +1, last: +0, k. of n: +(n-k)/(n-1))
        self.visible = visible
        self.type = Player.HUMAN  # 0= Player; 1= KI

    def get_type(self):
        return self.type

    def reset(self):
        self.cards = []
        self.active = True
        self.score[2] = None

    def reset_score(self):
        self.score[0] = 0
        self.score[1] = 0

    def get_cards(self):
        return self.cards

    def set_active(self, act):
        self.active = act

    def clear_cards(self):
        self.cards = []

    def add_cards(self, cards):
        self.cards += cards
        self.sort_cards()

    def play_card(self, card):
        self.cards.remove(card)
        return card

    def sort_cards(self):
        self.cards.sort()

    def number_of_cards(self):
        return len(self.cards)

    def __str__(self):
        return self.name

