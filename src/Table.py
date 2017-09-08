
class Table:
    def __init__(self):
        '''Table Class'''
        self.attack_cards = []
        self.defence_cards = []

    def reset(self):
        # raise NotImplemented
        self.attack_cards = []
        self.defence_cards = []

    def get_cards(self):
        c = []
        for i in range(len(self.attack_cards)):
            c += [[self.attack_cards[i], self.defence_cards[i]]]
        return c

    def get_attack_cards(self):
        return self.attack_cards

    def get_defence_cards(self):
        return self.defence_cards

    def add_attack_card(self, card, maximum_number_of_cards):
        '''Adds attack card to table'''
        all_names = []
        for c in self. attack_cards +self.defence_cards:
            if c != None: all_names += [c.get_name()]
        if len(self.attack_cards) > 0 and (card.get_name() not in all_names or \
                                                           self.defence_cards.count
                                                               (None ) +1 > maximum_number_of_cards):
            # invalid action
            return card
        else:
            self.attack_cards += [card]
            self.defence_cards += [None]
            return True

    def add_defence_card(self, card, on_card):
        '''Adds defence card to table'''
        if on_card not in self.attack_cards or card <= on_card or \
                (card.get_color() != on_card.get_color() and not card.is_trump()):
            # invalid action
            return card
        elif self.defence_cards[self.attack_cards.index(on_card)] == None:
            self.defence_cards[self.attack_cards.index(on_card)] = card
            return True
        else:
            # replace card
            c = self.defence_cards[self.attack_cards.index(on_card)]
            self.defence_cards[self.attack_cards.index(on_card)] = card
            return c

    def take_defence_card(self, card):
        '''returns defence card from table'''
        if card not in self.defence_cards:
            return False
        card_index = self.defence_cards.index(card)
        self.defence_cards[card_index] = None
        return self.attack_cards[card_index]

    def take_all_cards(self):
        '''returns all open cards'''
        cards = self. attack_cards +self.defence_cards
        while None in cards:
            cards.remove(None)
        self.attack_cards = []
        self.defence_cards = []
        return cards

    def remove_cards(self):
        '''takes all open cards away, if attack is fendet'''
        if None in self.defence_cards:
            # invalid action
            return False
        else:
            cards = self.take_all_cards()
            return cards
