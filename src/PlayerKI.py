import random

from Player import Player

class PlayerKI(Player):
    def __init__(self, name):
        Player.__init__(self, name)
        self.type = Player.KI # KI
        self.KI_brainSIZE = None # maximum saved player cards (None=infinity)

        self.KI_players = {} # players (hash): [number of cards, [known cards]]
        self.KI_table = [] # [[A,D],[A,D],...]
        self.KI_active_players = [] # attacking, attacked, third
        self.KI_trashcards = []
        self.KI_isblocked = None

    def KIforget(self):
        '''forget cards so that KI don't overflow brain'''
        if self.KI_brainSIZE == None: return

        s = len(self.KI_trashcards)
        for p in self.KI_players:
            s += len(self.KI_players[p][1])

        while s > self.KI_brainSIZE and s > 0:
            i = random.randint(0, len(self.KI_players))
            if i == 0:
                if len(self.KI_trashcards ) >0:
                    del self.KI_trashcards[0]
                    s -= 1
            else:
                p = random.sample(self.KI_players.keys(), 1)[0]
                if len(self.KI_players[p][1] ) >0:
                    del self.KI_players[p][1][0]
                    s -= 1


    def KIinfo_players(self, players):
        '''gives KI information about players in game (resets KI knowledge)'''
        self.KI_players = {}
        self.KI_table = []
        self.KI_active_players = []
        self.KI_trashcards = []
        self.KI_isblocked = None
        for player in players:
            self.KI_players.update({player: [0, []]})
            # print self, 'KI INFO PLAYERS'


    def KIinfo_status(self, player_number_of_cards, table_cards,
                      attacking_player, attacked_player,
                      second_attacking_player, blocked):
        '''gives KI information about status'''
        for player in player_number_of_cards:
            self.KI_players[player][0] = player_number_of_cards[player]
        self.KI_table = table_cards
        self.KI_active_players = [attacking_player, attacked_player, second_attacking_player]
        self.KI_isblocked = blocked
        # print self, 'KI INFO STATUS'

    def KIinfo_cards_moved(self, cards, _from=None, to=None):
        '''gives KI information about cards moved from or to player'''
        # print self, 'KI INFO', ', '.join([str(c) for c in cards]), 'from', _from, 'to', to

        if _from != None:
            for card in cards:
                if card in self.KI_players[_from][1]: self.KI_players[_from][1].remove(card)
        elif to != None:
            self.KI_players[to][1] += cards
        elif to == None:
            self.KI_trashcards += cards

        self.KIforget()

    def KIdo_action(self, durak):
        '''place for KI calculations and actions'''
        return self.KIdo_action_v_1(durak)

    def KIdo_action_v_1(self, durak):
        # simple KI V 1.0
        # actions based on own cards and cards on table, not on brain

        def number_of_open_cards_on_table():
            s = 0
            for a ,c in self.KI_table:
                s += 1 if c == None else 0
            return s

        def forward_possible(card):
            if len(self.KI_table) == 0: return False
            for a, d in self.KI_table:
                if a.get_name() != card.get_name(): return False
            return True

        def test_full_defence(attackcards):
            """return defence cards for given attack cards or false if defence impossible"""
            acards = [ ] +attackcards
            dcards = self.cards + [c[1] for c in self.KI_table]
            finaldcards = []

            for acard in acards:
                ddcard = None
                for dcard in dcards:
                    if dcard is None: continue
                    if (acard.get_color() == dcard.get_color() or dcard.is_trump()) and dcard > acard:
                        if ddcard == None or dcard < ddcard:
                            ddcard = dcard
                if ddcard == None:
                    return False
                dcards.remove(ddcard)
                finaldcards.append(ddcard)
            return finaldcards

        def all_names():
            names = []
            for a ,d in self.KI_table:
                names += [a.get_name()]
                if d != None:
                    names += [d.get_name()]
            return names

        def most_frequent_name():
            names = [c.get_name() for c in self.cards]
            return max(names, key=lambda n: names.count(n))

        # Actions
        if not self.active:
            return

        if hash(self) == self.KI_active_players[1] and len(self.KI_table ) >0:
            # forward attack?
            if not self.KI_isblocked and self.KI_players[self.KI_active_players[2]][0] > number_of_open_cards_on_table():
                for c in self.cards:
                    if forward_possible(c):
                        return [durak.action_play_attack_card, self, c]
            # defence
            dcards = test_full_defence([c[0] for c in self.KI_table])
            if dcards == False: # defence impossible
                return [durak.action_take_or_remove_all_cards, self]
            for a, d in self.KI_table:
                if d is None:
                    for c in self.cards:
                        if c > a and (c.get_color() == a.get_color() or c.is_trump()):
                            return [durak.action_play_defence_card, self, c, a]
            return [durak.action_take_or_remove_all_cards, self]

        elif hash(self) in (self.KI_active_players[0], self.KI_active_players[2]) and len(self.cards) > 0:
            # attack
            if len(self.KI_table ) ==0 and hash(self) == self.KI_active_players[0]: # first attack
                for c in self.cards:
                    if c.get_name() == most_frequent_name() and not c.is_trump():
                        return [durak.action_play_attack_card, self, c]
                return [durak.action_play_attack_card, self, self.cards[0]]
            elif self.KI_players[self.KI_active_players[1]][0] > number_of_open_cards_on_table(): # support attack
                for c in self.cards:
                    if c.get_name() in all_names() and not c.is_trump():
                        return [durak.action_play_attack_card, self, c]


        return
