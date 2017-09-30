#!/usr/bin/python
# -*- coding: cp1252 -*-

# Copyright 2017 Philipp Niedermayer (github.com/eltos)
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os, pickle, time, sys
import webbrowser
from PyQt4 import QtGui, QtCore
from src import *



def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

SCORE_FILE = 'score.sav'
TRANSLATIONS_DIR = resource_path('translations')
ICON_FILE = resource_path('D.png')
Settings.THEME_DIR = resource_path('themes')
Settings.SETTINGS_FILE = 'settings.sav'


class Durak(QtGui.QGraphicsItem):

    KI_INTERVAL = 1500 # ms
    END_ATTACK_DELAY = 5 # s
    ANIMATION_DURATION = 500 # ms
    FAST_FORWARD_FACTOR = 0.05 # for KI only gameplay

    def __init__(self, parent=None):
        QtGui.QGraphicsItem.__init__(self, parent)
        self.parent = parent

        self.boundingrect = QtCore.QRectF(0, 0, 960, 540)

        self.sett = Settings()
        self.sett.setAnimationDuration(self.ANIMATION_DURATION)

        self.view = None

        self.stack = Stack()
        self.trash = Trash()
        self.table = Table()
        # self.players = []
        self.attacking_player = None
        self.blocked = False
        self.first_player_in_round = None
        self.winners = []
        self.end_attack_time = time.time()
        self.paused = False

        self.first_selected_card = None
        self.last_selected_card = None

        self.KIaktuell = 0
        self.KItimer = QtCore.QTimer()
        self.KItimer.setInterval(self.KI_INTERVAL)
        QtCore.QObject.connect(self.KItimer, QtCore.SIGNAL('timeout()'), self.KIinterval)


        self.qtTranslator = QtCore.QTranslator()
        if self.qtTranslator.load('durak_' + QtCore.QLocale.system().name(), TRANSLATIONS_DIR):
            self.tr = lambda s: self.qtTranslator.translate('Durak', s)
        else:
            self.tr = lambda s: QtCore.QString(s)

        # load self player
        try:
            f = open(SCORE_FILE, 'r')
            player = pickle.load(f)
            f.close()
        except:
            player = Player(self.tr('You'), True)

        if False:
            # To set yourselve as a KI. Be aware that this will be saved,
            # and you have to delete the score file to disable it again!
            player = PlayerKI(self.tr('You'))

        self.players = [player]
        self.KIinfo_players(self.players)

        # CREATE ITEMS

        # CARD ITEMS and VIRTUALS
        self.card_Items = {}
        for color in range(4):
            for name in range(2, 15):
                card = Card(color, name)
                self.trash.add_cards([card])
                self.card_Items.update({card: CardItem(self, card, size=QtCore.QSize(70, 105))})
                self.card_Items[card].hide()


        # SEATS
        self.seat_Items = []
        for i in range(6):
            self.seat_Items += [SeatItem(self, None)]
        self.seat_Items[0].set_player(self.players[0])

        # TABLE
        self.table_Item = TableItem(self, self.table)
        self.table_Item.setZValue(10)

        # STACK
        self.stack_Item = StackItem(self, self.stack)
        self.stack_Item.setZValue(0)

        # TRASH
        self.trash_Item = TrashItem(self, self.trash)
        self.trash_Item.setZValue(0)

        # BUTTONS
        self.cardbutton = TimerButton(self, on_click=self.action_take_or_remove_all_cards) # auto_click_delay = 20,
        self.cardbutton.setDisabled(True)
        self.pausebutton = Button(self, on_click=self.new_game)
        self.pausebutton.setText(self.tr('New game'))
        self.menubutton = Button(self, on_click=self.show_menu)
        self.menubutton.setText(self.tr('Menu'))

    
    def toggle_pause(self, paused=None):
        self.paused = not self.paused if paused == None else paused
        self.pausebutton.setText(self.tr('Continue') if self.paused else self.tr('Pause'))
        if self.paused:
            self.end_attack_time = 0
            self.cardbutton.disableTimer()
        else:
            self.reset_timer()
        self.update()

    def reset_timer(self):
        if len(self.table.get_cards()) > 0:
            self.cardbutton.resetTimer()
        if len(self.table.get_cards()) > 0 and None not in self.table.get_defence_cards():
            if self.next_attacking_player().number_of_cards() == 0 or \
                                    self.attacking_player.number_of_cards() == 0 and \
                                    self.next_attacking_player(+1).number_of_cards() == 0:
                self.end_attack_time = time.time()
            else:
                # time, when attack can be terminated
                if self.only_KIs_left():
                    self.end_attack_time = time.time() + self.END_ATTACK_DELAY*self.FAST_FORWARD_FACTOR
                else:
                    self.end_attack_time = time.time() + self.END_ATTACK_DELAY
        else:
            self.end_attack_time = time.time()

    def resize(self, width, height):
        self.boundingrect = QtCore.QRectF(0, 0, width, height)
        s = min(width / 960., height / 540.)

        d = max(width * 15 / 960, height * 15 / 540)

        ratio_a_b = 2.  # a = width_of_seat; b = height_of_seat
        max_a_h = 0.5  # a <= max_a_h*height_of_window

        if width > (2. / ratio_a_b + 3) * max_a_h * height:
            a = max_a_h * height
        else:
            a = width / (2 / ratio_a_b + 3)
        b = a / ratio_a_b

        # C A R D S
        for card in self.card_Items.keys():
            self.card_Items[card].setSize(QtCore.QSize(max(1, (b - d) * 70 / 105), max(1, (b - d))))

        # S E A T
        for i, x, y, dx, dy, r in ((0, width / 2., height - b / 2., 2 * a, b, 0),  # player 0
                                   (1, b / 2., a / 2., a, b, 90),
                                   (2, (width + 2 * b - a) / 4., b / 2., a, b, 180),
                                   (3, width / 2., b / 2., a, b, 180),
                                   (4, (3 * width - 2 * b + a) / 4., b / 2., a, b, 180),
                                   (5, width - b / 2., a / 2., a, b, 270)):
            self.seat_Items[i].setPos(x, y)
            self.seat_Items[i].setRotation(r)
            self.seat_Items[i].setSize(QtCore.QSize(max(1, dx), max(1, dy)))

        # T A B L E
        self.table_Item.setPos(self.boundingRect().center())
        self.table_Item.setSize(QtCore.QSize(max(1, width - 2.2 * b), max(1, height - 2.2 * b)))

        # S T A C K
        self.stack_Item.setPos(75 * s, height - 75 * s)
        self.stack_Item.setSize(QtCore.QSize(max(1, 150 * s), max(1, 150 * s)))

        # T R A S H
        self.trash_Item.setPos(width*1.2, height*1.2)

        # B U T T O N S
        self.cardbutton.setPos(width - 80 * s, height - 90 * s)
        self.cardbutton.setSize(QtCore.QSize(max(1, 120 * s), max(1, 20 * s)))
        self.pausebutton.setPos(width - 80 * s, height - 60 * s)
        self.pausebutton.setSize(QtCore.QSize(max(1, 120 * s), max(1, 20 * s)))
        self.menubutton.setPos(width - 80 * s, height - 30 * s)
        self.menubutton.setSize(QtCore.QSize(max(1, 120 * s), max(1, 20 * s)))

        self.update()

    def update(self, rect=QtCore.QRectF()):

        for seat in self.seat_Items:
            seat.update()
        self.table_Item.update()
        self.stack_Item.update()
        self.trash_Item.update()

        if None in self.table.get_defence_cards() or len(self.table.get_cards()) == 0:
            self.cardbutton.setText(self.tr('Take cards'))
            self.reset_timer()
        else:
            self.cardbutton.setText(self.tr('End attack'))
        self.cardbutton.setDisabled(self.players[0] != self.next_attacking_player() or
                                    len(self.table.get_cards()) == 0 or self.paused)

        if self.players[0] == self.next_attacking_player() and not self.can_fight_attack():
            self.cardbutton.blink()


        self.KIinfo_status()

        for player in self.players:
            if player.number_of_cards() == 0 and player not in self.winners:
                self.winners += [player]

        QtGui.QGraphicsItem.update(self, rect)

    def KIinterval(self):
        if self.paused: return

        actions = []
        # for player in self.players:
        self.KIaktuell += 1
        self.KIaktuell %= 2
        other = (self.attacking_player, self.next_attacking_player(+1))[self.KIaktuell]
        # for player in self.players:
        for player in (other, self.next_attacking_player()):
            if player.get_type() == Player.KI:
                action = player.KIdo_action(self)
                if action is not None:
                    actions.append(player.KIdo_action(self))
            elif player.get_type() == Player.HUMAN:
                if None not in self.table.get_defence_cards():  # auto remove cards
                    actions.append([self.action_take_or_remove_all_cards, player])
        actions.reverse()
        for action in actions:
            action[0](*action[1:])

    def KIinfo_players(self, players):
        for player in self.players:
            if player.get_type() == Player.KI:
                player.KIinfo_players([hash(p) for p in players])

    def KIinfo_cards_moved(self, cards, _from=None, to=None):
        if _from is not None: _from = hash(_from)
        if to is not None: to = hash(to)
        for player in self.players:
            if player.get_type() == Player.KI:
                player.KIinfo_cards_moved(cards, _from, to)

    def KIinfo_status(self):
        pnc = {}
        for player in self.players:
            pnc.update({hash(player): player.number_of_cards()})
        for player in self.players:
            if player.get_type() == Player.KI:
                player.KIinfo_status(pnc, self.table.get_cards(), hash(self.attacking_player),
                                     hash(self.next_attacking_player()),
                                     hash(self.next_attacking_player(+1)),
                                     bool(self.blocked))

    def set_player_number(self, n):
        """Adds player to game"""
        if not 2 <= n <= 6:
            raise Exception(self.tr('%1 Players not in range 2 to 6!').arg(n))

        p = []
        for i in range(n):
            if i < len(self.players):
                p += [self.players[i]]
            else:
                p += [PlayerKI(self.tr('Player %1').arg(i))]
        self.players = p

        self.KIinfo_players(self.players)

        places = {1: (0,), 2: (0,3), 3: (0,2,4), 4: (0,2,3,4), 5: (0,1,2,4,5), 6: (0,1,2,3,4,5)}[len(self.players)]
        for i in range(len(self.seat_Items)):
            if i in places:
                self.seat_Items[i].set_player(self.players[places.index(i)])
            else:
                self.seat_Items[i].set_player(None)

    def on_exit(self):
        self.players[0].reset()
        f = open(SCORE_FILE, 'w')
        pickle.dump(self.players[0], f)
        f.close()
        self.sett.save()
        print(self.tr('Bye'))

    def new_game(self):
        """Starts new game"""
        waspaused = self.paused
        self.paused = True

        # input dialog
        lst = [self.tr('%1 player').arg(i) for i in range(2, 7)]
        a = QtGui.QInputDialog.getItem(self.scene().views()[0],
                                       self.scene().views()[0].windowTitle(), self.tr('New game:'),
                                       lst, current=(len(self.players) - 1 or 2) - 1, editable=False,
                                       flags=QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowSystemMenuHint | \
                                             QtCore.Qt.FramelessWindowHint)
        if a[1]:  # ok
            n = 2 + lst.index(a[0])
        else:  # cancel
            self.paused = waspaused
            self.reset_timer()
            return

        self.pausebutton.setDisabled(True)

        self.attacking_player = None
        self.blocked = False
        self.first_player_in_round = None
        self.winners = []

        self.sett.setAnimationDuration(self.ANIMATION_DURATION)
                

        # collect cards
        self.trash.add_cards(self.stack.take_all_cards())
        self.trash.add_cards(self.table.take_all_cards())
        for player in self.players:
            player.set_active(True)
            while len(player.get_cards()) > 0:
                self.trash.add_cards([player.play_card(player.get_cards()[0])])

        self.stack.add_cards(self.trash.take_cards(deck=Trash.DECK52 if self.sett.isFullDeck() else Trash.DECK36))

        for card, item in self.card_Items.iteritems():
            item.setRaised(False)

        # edit player number
        self.set_player_number(n)

        # shuffle
        self.stack.shuffle()
        self.stack.set_value_by_trump()

        self.update()

        QtCore.QTimer.singleShot(self.sett.getAnimationDuration() * 1.5, self.start_new_game)

    def start_new_game(self):
        print('neues Spiel\n===========')
        print(self.stack)

        # distribute
        self.distribute()
        self.attacking_player = self.start_player()
        self.first_player_in_round = self.players.index(self.attacking_player)
        self.winners = []
        self.blocked = False

        self.KIinfo_status()
        self.KItimer.setInterval(self.KI_INTERVAL)
        self.KItimer.start()

        self.pausebutton.on_click = self.toggle_pause
        self.pausebutton.setDisabled(False)
        self.toggle_pause(False)

        self.update()  # //#

    def count_active_players(self):
        i = 0
        for p in self.players:
            if p.active: i += 1
        return i

    def only_KIs_left(self):
        return True not in [player.get_type() == Player.HUMAN and player not in self.winners for player in self.players]

    def new_round(self, skip_player=False):
        self.distribute_missing()

        i = 0
        while i < len(self.winners):  # clear winner list
            if self.winners[i].number_of_cards() > 0:
                self.winners.remove(self.winners[i])
            else:
                i += 1

        for player in self.winners:
            if player.active:
                player.set_active(False)
                player.score[0] += (len(self.players) - self.winners.index(player) - 1) / (len(self.players) - 1.)
                player.score[1] += 1
                player.score[2] = self.winners.index(player) + 1

        # check weather any human players are left, otherwise increase speed
        if self.only_KIs_left():
            self.KItimer.setInterval(self.KI_INTERVAL*self.FAST_FORWARD_FACTOR)
            self.sett.setAnimationDuration(self.ANIMATION_DURATION*self.FAST_FORWARD_FACTOR)


        self.blocked = False
        self.attacking_player = self.next_attacking_player(skip=int(skip_player))
        if self.attacking_player is None:  # end of game
            for player in self.players:
                if player not in self.winners:
                    self.winners += [player]
                    player.set_active(False)
                    player.score[0] += (len(self.players) - self.winners.index(player) - 1) / (len(self.players) - 1.)
                    player.score[1] += 1
                    player.score[2] = self.winners.index(player) + 1

            self.game_end()
        else:
            self.first_player_in_round = self.players.index(self.attacking_player)
        self.cardbutton.disableTimer()
        self.update()  # //#

    def game_end(self):
        self.trash.add_cards(self.table.take_all_cards())
        self.trash.add_cards(self.stack.take(self.stack.size()))
        for player in self.players:
            while len(player.get_cards()) > 0:
                self.trash.add_cards([player.play_card(player.get_cards()[0])])
        self.KItimer.stop()
        self.pausebutton.on_click = self.new_game
        self.pausebutton.setText(self.tr('New game'))
        self.cardbutton.disableTimer()
        self.update()
        print('\n' + self.tr('Game finished') + '\n' + '=' * len(self.tr('Game finished')))
        for p in self.winners:
            print('%i.\t%s\t(%.2f%%)' % (p.score[2], p.name, p.score[0] / p.score[1] * 100))

        self.new_game()

    def distribute(self):
        """Distributes 6 cards to each player"""
        for i in range(6):
            for player in self.players:
                cards = self.stack.take()
                player.add_cards(cards)
                if self.stack.size() == 0:  # Only if it's the visible card
                    self.KIinfo_cards_moved(cards, to=player)
        self.update()  # //#

    def distribute_missing(self):
        """Distributes up to 6 cards to each player"""
        for player in self.players[self.first_player_in_round:] + self.players[:self.first_player_in_round]:
            while player.number_of_cards() < 6 and self.stack.size() > 0:
                cards = self.stack.take()
                player.add_cards(cards)
                if self.stack.size() == 0: # Only if it's the visible card
                    self.KIinfo_cards_moved(cards, to=player)
        self.update()  # //#

    def start_player(self):
        """returns Player with lowest trump or first player, if no one has trump"""
        pt = {}
        for player in self.players:
            trump = []
            for card in player.get_cards():
                if card.color == self.stack.get_trump():
                    trump += [card]
            if len(trump) > 0:
                pt.update({min(trump): player})
        if len(pt) > 0:
            return pt[min(pt)]
        else:
            return self.players[0]

    def next_attacking_player(self, skip=0):
        """returns next attacked (active) player by skipping x players"""
        if self.attacking_player is None: return None
        player = []
        i = self.players.index(self.attacking_player)
        for p in self.players[i:] + self.players[:i]:
            if p.active: player += [p]
        if len(player) <= 1: return None
        next_player = player[((1 if self.attacking_player in player or skip < 0 else 0) + skip) % len(player)]
        return next_player

    def last_attacking_player(self, skip=0):
        raise NotImplementedError
        return self.next_attacking_player(skip=-2 - skip)

    def can_fight_attack(self):
        player = self.next_attacking_player()  # attacked player

        attack = self.table.get_attack_cards()
        defence = self.table.get_defence_cards() + player.get_cards()

        # can forward attack?
        if not self.blocked and 0 < len(attack) < self.next_attacking_player(+1).number_of_cards():
            name = attack[0].get_name()
            for dcard in defence:
                if dcard == None: continue
                if dcard.get_name() == name:
                    return True

        # can defence?
        for acard in attack:
            ddcard = None
            for dcard in defence:
                if dcard == None: continue
                if (acard.get_color() == dcard.get_color() or dcard.is_trump()) and dcard > acard:
                    if ddcard == None or dcard < ddcard:
                        ddcard = dcard
            if ddcard == None:
                return False
            defence.remove(ddcard)
        return True

    def action_take_or_remove_all_cards(self, player=None):
        if self.paused: return

        if player is None: player = self.next_attacking_player()
        if player != self.next_attacking_player(): return
        if len(self.table.get_cards()) == 0: return
        if None in self.table.get_defence_cards():  # take
            res = self.table.take_all_cards()
            player.add_cards(res)
            self.KIinfo_cards_moved(res, to=player)
            self.new_round(skip_player=True)
        elif self.end_attack_time <= time.time():  # remove
            res = self.table.remove_cards()
            if res is not False:
                self.trash.add_cards(res)
                self.KIinfo_cards_moved(res, to=None)
                self.new_round()
        self.update()  # //#

    def action_take_defence_card(self, player, card):
        if player != self.next_attacking_player(): return
        res = self.table.take_defence_card(card)
        if res is not False:
            self.KIinfo_cards_moved([card], to=player)
            player.add_cards([card])
            self.reset_timer()
        self.update()  # //#

    def action_play_attack_card(self, player, card):
        if len(self.table.get_cards()) == 0 and player != self.attacking_player \
                or player not in (self.attacking_player, self.next_attacking_player(), self.next_attacking_player(+1)):
            return

        card = player.play_card(card)
        res = card
        if player == self.next_attacking_player() and not self.blocked:
            # forward attack?
            res = self.table.add_attack_card(card, self.next_attacking_player(+1).number_of_cards())
            if res == True:
                self.attacking_player = self.next_attacking_player()

        elif player in (self.attacking_player, self.next_attacking_player(+1)):
            res = self.table.add_attack_card(card, self.next_attacking_player().number_of_cards())
            if res == True and player == self.next_attacking_player(+1) and player != self.attacking_player:
                self.blocked = True

        if res is not True:
            player.add_cards([res])
        else:
            self.KIinfo_cards_moved([card], _from=player)
            self.reset_timer()
        self.update()  # //#

    def action_play_defence_card(self, player, card, on_card):
        if player != self.next_attacking_player(): return
        card = player.play_card(card)
        res = self.table.add_defence_card(card, on_card)
        if res is not True:
            player.add_cards([res])
        else:
            self.KIinfo_cards_moved([card], _from=player)
            self.blocked = True
            self.reset_timer()
        self.update()  # //#

    def action_move_defence_card(self, card, on_card):
        from_card = self.table.take_defence_card(card)
        res = self.table.add_defence_card(card, on_card)
        if res is not True:
            res = self.table.add_defence_card(res, from_card)
            if res is not True:
                self.next_attacking_player().add_cards([res])
                self.KIinfo_cards_moved([res], to=self.next_attacking_player())
        if res is True:
            self.reset_timer()
        self.update()  # //#

    def card_moved(self, _from, card_Item, pos=None):
        if self.paused: return

        card = card_Item.card

        to = None
        if pos is None:
            to = self.table_Item
        else:
            for item in self.seat_Items + [self.table_Item]:
                if item.boundingRect().contains(self.mapToItem(item, pos)):
                    to = item
                    break

        if to == self.table_Item:
            # -> table
            onto = None
            if pos is None:  # guess
                if _from.player == self.next_attacking_player():
                    # guess forward or defence card
                    if self.blocked or len(self.table.get_attack_cards()) >= self.next_attacking_player(+1).number_of_cards():
                        can_forward = False
                    else:
                        can_forward = True
                        common_name = None
                        for attack_card, defence_card in self.table.get_cards():
                            if common_name is None:
                                common_name = attack_card.get_name()
                            if defence_card is not None or card.get_name() != common_name or \
                                            attack_card.get_name() != common_name:
                                can_forward = False
                                break

                    if not can_forward:  # auto find adequate attack card if no forward possible
                        for attack_card, defence_card in self.table.get_cards():
                            if defence_card is None and card > attack_card and \
                                    (attack_card.color == card.color or card.is_trump()):
                                if onto is None:
                                    onto = attack_card
                                elif attack_card > onto:
                                    onto = attack_card

                else:
                    onto = None # contribute in attack

            else:  # get onto card by position
                for attack_card, defence_card in self.table.get_cards():
                    if self.card_Items[attack_card].boundingRect().contains(
                            self.mapToItem(self.card_Items[attack_card], pos)):
                        onto = attack_card
                        break

            if _from in self.seat_Items:  # player -> table
                if _from.player == self.next_attacking_player() and \
                                _from.player == self.players[0] and onto is not None:
                    self.action_play_defence_card(_from.player, card, onto)

                elif _from.player == self.players[0]:
                    self.action_play_attack_card(_from.player, card)

            elif _from == self.table_Item:  # table -> table
                if self.next_attacking_player() == self.players[0] and \
                                card in self.table.get_defence_cards() and onto is not None:
                    self.action_move_defence_card(card, onto)
        elif to in self.seat_Items:
            # -> player
            if to.player == self.next_attacking_player() and to.player == self.players[0]:
                self.action_take_defence_card(to.player, card)


    def select_card(self, shift=False, d=1):
        if len(self.players[0].get_cards()) == 0: return

        cards = self.players[0].get_cards()

        first_index = None
        last_index = None
        try:
            first_index = cards.index(self.first_selected_card)
        except ValueError:
            first_index = None
        try:
            last_index = cards.index(self.last_selected_card)
        except ValueError:
            last_index = first_index

        if first_index is None:
            # select first
            self.first_selected_card = cards[0 if d > 0 else -1]
            self.last_selected_card = None

        elif not shift:
            # select single card
            self.first_selected_card = cards[(last_index+d)%len(cards)]
            self.last_selected_card = None

        else:
            # expand selection
            if last_index is None: last_index = first_index+d
            self.last_selected_card = cards[(last_index+d)%len(cards)]

        self.update_raised_cards()
        self.update()

    def update_raised_cards(self):
        # set selection
        cards = self.players[0].get_cards()
        try:
            a = cards.index(self.first_selected_card)
        except ValueError:
            a = -1
        try:
            b = cards.index(self.last_selected_card)
        except ValueError:
            b = a
        for i in range(len(cards)):
            self.card_Items[cards[i]].setRaised(
                a <= i <= b or b <= i <= a
            )

    def raise_all_cards(self):
        if len(self.players[0].get_cards()) > 0:
            self.first_selected_card = self.players[0].get_cards()[0]
            self.last_selected_card = self.players[0].get_cards()[-1]
        self.update_raised_cards()

    def unraise_all_cards(self):
        self.first_selected_card = None
        self.last_selected_card = None
        self.update_raised_cards()

    def key_ctrl_a(self):
        self.raise_all_cards()
        self.update()

    def key_up(self):
        for card in self.players[0].get_cards()[:]:
            cardItem = self.card_Items[card]
            if cardItem.isRaised():
                self.card_moved(self.seat_Items[0], cardItem)
        self.unraise_all_cards()
        self.update()

    def key_down(self):
        # unraise all cards
        for card in self.players[0].get_cards():
            if self.card_Items[card].isRaised():
                self.unraise_all_cards()
                self.update()
                return
        # take defence cards first
        take_all = True
        for card in self.table.get_defence_cards()[:]:
            if card is not None:
                take_all = False
                self.action_take_defence_card(self.players[0], card)

        if take_all:
            self.action_take_or_remove_all_cards(self.players[0])

    def show_menu(self):
        waspaused = self.paused
        self.paused = True
        self.end_attack_time = 0
        self.update()

        window = QtGui.QDialog(self.scene().views()[0],
                               flags=QtCore.Qt.WindowTitleHint|QtCore.Qt.MSWindowsFixedSizeDialogHint)
        window.setWindowTitle(self.scene().views()[0].windowTitle() + ' - ' + self.tr('Menu'))
        window.setMinimumSize(200, 100)

        closebutton = QtGui.QPushButton(self.tr('Close'), parent=window)
        closebutton.setDefault(True)
        closebutton.connect(closebutton, QtCore.SIGNAL('clicked()'), window.close)

        actionsbox = QtGui.QGroupBox('', parent=window)
        if actionsbox:
            actionsbox_layout = QtGui.QVBoxLayout(actionsbox)

            new_game = QtGui.QPushButton(self.tr('Start new game'), parent=actionsbox)
            new_game.connect(new_game, QtCore.SIGNAL('clicked()'), lambda: (window.close(), self.new_game()))

            def show_score_window():
                msgBox = QtGui.QMessageBox(window)
                msgBox.setWindowTitle(self.tr('Score'))
                msgBox.setText(QtCore.QStringList([
                    self.tr('Played games:\t\t%1').arg(self.players[0].score[1]),
                    self.tr('Score:\t\t\t%1 %').arg('-' if not self.players[0].score[1] else round(
                        100 * self.players[0].score[0] / self.players[0].score[1], 2)),
                    self.tr('Last place:\t\t%1').arg(self.players[0].score[2] or '-')]).join('\n'))
                msgBox.setStandardButtons(QtGui.QMessageBox.Close | QtGui.QMessageBox.Reset)
                msgBox.setDefaultButton(QtGui.QMessageBox.Close)
                result = msgBox.exec_()
                if result == QtGui.QMessageBox.Reset:
                    self.players[0].reset_score()
                    show_score_window()

            show_score = QtGui.QPushButton(self.tr('Show score'), parent=actionsbox)
            show_score.connect(show_score, QtCore.SIGNAL('clicked()'), show_score_window)
            toggle_F11 = QtGui.QPushButton(self.tr('Toggle fullscreen'), parent=actionsbox)
            toggle_F11.connect(toggle_F11, QtCore.SIGNAL('clicked()'), self.toggle_fullscreen)

            about = QtGui.QPushButton(self.tr('Help and About'), parent=actionsbox)
            about.connect(about, QtCore.SIGNAL('clicked()'), lambda: webbrowser.open("https://github.com/eltos/durak"))

            seperator = QtGui.QFrame(actionsbox)
            seperator.setFrameShape(QtGui.QFrame.HLine)
            seperator.setFrameShadow(QtGui.QFrame.Sunken)

            exit_game = QtGui.QPushButton(self.tr('Exit'), parent=actionsbox)
            exit_game.connect(exit_game, QtCore.SIGNAL('clicked()'),
                              lambda: (window.close(), self.scene().views()[0].close()))

            actionsbox_layout.addWidget(new_game)
            actionsbox_layout.addWidget(show_score)
            actionsbox_layout.addWidget(toggle_F11)
            actionsbox_layout.addWidget(about)
            actionsbox_layout.addWidget(seperator)
            actionsbox_layout.addWidget(exit_game)


        settingsbox = QtGui.QGroupBox(self.tr('Settings'), parent=window)
        if settingsbox:
            settingsbox_layout = QtGui.QGridLayout(settingsbox)

            themechooserlabel = QtGui.QLabel(settingsbox, text=self.tr('Theme:'))
            themechooser = QtGui.QComboBox(settingsbox)

            themesdir = QtCore.QDir(self.sett.THEME_DIR)
            themes = themesdir.entryList(filters=QtCore.QDir.AllDirs)
            themes.removeAt(themes.indexOf('.'))
            themes.removeAt(themes.indexOf('..'))
            themechooser.addItems(themes)
            themechooser.setCurrentIndex(themes.indexOf(self.sett.getTheme()))

            def onThemeChange(theme):
                self.sett.setTheme(theme)
                self.sett.load_resources()
                # to force reinitialisation of resources in item objects:
                self.resize(self.boundingRect().width(), self.boundingRect().height())

            themechooser.connect(themechooser, QtCore.SIGNAL('currentIndexChanged(const QString&)'), onThemeChange)
            settingsbox_layout.addWidget(themechooserlabel, 0, 0, alignment=QtCore.Qt.AlignLeft)
            settingsbox_layout.addWidget(themechooser, 0, 1, alignment=QtCore.Qt.AlignLeft)


            deckchooserlabel = QtGui.QLabel(settingsbox, text=self.tr("Card deck:"))
            deckchooser = QtGui.QComboBox(settingsbox)
            deckchooser.addItems([self.tr('36 cards'),self.tr('52 cards')])
            deckchooser.setCurrentIndex(1 if self.sett.isFullDeck() else 0)
            def onDeckChange(deck):
                self.sett.setFullDeck(deck)
            deckchooser.connect(deckchooser, QtCore.SIGNAL('currentIndexChanged(const int)'), onDeckChange)

            settingsbox_layout.addWidget(deckchooserlabel, 1, 0, alignment=QtCore.Qt.AlignLeft)
            settingsbox_layout.addWidget(deckchooser, 1, 1, alignment=QtCore.Qt.AlignLeft)



        layout = QtGui.QGridLayout(window)
        layout.addWidget(actionsbox, 0, 0)
        layout.addWidget(settingsbox, 2, 0)
        layout.addWidget(closebutton, 4, 0, alignment=QtCore.Qt.AlignRight)


        def close(event=None):
            self.paused = waspaused
            if not self.paused:
                self.reset_timer()
            self.update()

        window.finished.connect(close)
        window.closeEvent = close
        window.open()

    def boundingRect(self):
        return self.boundingrect

    def paint(self, painter, option, widget=None):
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor('grey'))
        painter.drawImage(self.boundingRect(), self.sett.resources['background'])


    def toggle_fullscreen(self, disable=None):
        if self.view is None: return

        if disable or self.view.windowState() == QtCore.Qt.WindowFullScreen:
            self.view.setWindowState(QtCore.Qt.WindowNoState)
            self.sett.setFullscreen(False)

        else:
            self.view.setWindowState(QtCore.Qt.WindowFullScreen)
            self.sett.setFullscreen(True)


    def init_view(self, view):

        self.view = view

        view.scene()

        view.setWindowTitle(self.tr('Durak'))

        view.setWindowIcon(QtGui.QIcon(ICON_FILE))

        view.setRenderHint(QtGui.QPainter.Antialiasing)
        view.setMinimumSize(0.5 * 960, 0.5 * 540)
        view.setBackgroundBrush(QtGui.QBrush(self.sett.resources['background']))
        view.resize(view.sceneRect().width(), view.sceneRect().height())


        # shortcuts
        shortcuts = {
            "F11":          self.toggle_fullscreen,
            "escape":       lambda: self.toggle_fullscreen(disable=True),
            "space":        lambda: self.pausebutton.on_click(),  # on_click method changes
            "M":            self.menubutton.on_click,
            "ctrl+N":       self.new_game,
            "left":         lambda: self.select_card(False, -1),
            "right":        lambda: self.select_card(False, +1),
            "shift+left":   lambda: self.select_card(True, -1),
            "shift+right":  lambda: self.select_card(True, +1),
            "up":           self.key_up,  # auto play selected
            "down":         self.key_down,  # take / take all
            "ctrl+A":       self.key_ctrl_a  # select all cards
        }

        for key in shortcuts:
            hotkey = QtGui.QShortcut(QtGui.QKeySequence(key), view)
            QtCore.QObject.connect(hotkey, QtCore.SIGNAL('activated()'), shortcuts[key])


        def resize(event=None):
            self.resize(view.width(), view.height())
            # prevent scrollbars (-2)
            view.setSceneRect(0, 0, self.sceneBoundingRect().width() - 2, self.sceneBoundingRect().height() - 2)

        view.closeEvent = lambda event: self.on_exit()
        view.resizeEvent = resize

        if self.sett.isFullscreen():
            view.setWindowState(QtCore.Qt.WindowFullScreen)
            



def main():
    """Start the game..."""
    app = QtGui.QApplication(sys.argv)

    qtTranslator = QtCore.QTranslator()
    if qtTranslator.load("qt_" + QtCore.QLocale.system().name(),
                QtCore.QLibraryInfo.location(QtCore.QLibraryInfo.TranslationsPath)):
        app.installTranslator(qtTranslator)
       

    spiel = Durak()

    scene = QtGui.QGraphicsScene(0, 0, spiel.sceneBoundingRect().width(),
                                 spiel.sceneBoundingRect().height())
    scene.addItem(spiel)

    view = QtGui.QGraphicsView(scene)

    spiel.init_view(view)




    view.show()

    spiel.new_game()

    sys.exit(app.exec_())



if __name__ == '__main__':
    main()
