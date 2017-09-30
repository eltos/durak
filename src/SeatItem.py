from PyQt4 import QtGui, QtCore

class SeatItem(QtGui.QGraphicsItem):
    def __init__(self, parent, player=None, size=QtCore.QSize(320 ,90)):
        ''''''
        QtGui.QGraphicsItem.__init__(self, parent)

        # self.parentItem() = parent
        self.sett = self.parentItem().sett
        # self.cards = []

        self.box = QtCore.QRect(QtCore.QPoint(-size.width( ) /2, -size.height( ) /2), size) # x,y,size

        self.set_player(player)

        self.setSize(size)
        #





    def card_moved(self, card, pos=None, DblClick=False):
        if pos != None:
            pos = self.mapToParent(pos)
        self.parentItem().card_moved(self, card, pos)
        # card.setRaised(False)

        for card in self.player.get_cards()[:]:
            if self.parentItem().card_Items[card].isRaised():
                self.parentItem().card_Items[card].setRaised(False)
                self.parentItem().card_moved(self, self.parentItem().card_Items[card], pos)

        self.update()

    def set_player(self, player):
        ''''''
        self.player = player
        self.setToolTip('')
        if self.player == None:
            self.reset()
        elif not player.visible:
            self.setToolTip(self.player.name)
        self.update()

    def reset(self):
        ''''''
        # while len(self.cards) > 0:
        #    self.cards[0].hide()
        #    del self.cards[0]
        pass

    def update_cards(self, noanim=False):
        ''''''
        if self.player == None:
            return

        cards = self.player.get_cards()
        for i in range(len(cards)):
            card = self.parentItem().card_Items[cards[i]]

            card.setParentItem(self)
            card.set_visible(self.player.visible)
            # card.show()
            # 0...1
            d = self.boundingRect().height( ) -card.boundingRect().height()
            f_max = i* (card.boundingRect().width() + d / 2) / (
            self.boundingRect().width() - card.boundingRect().width() - d)
            f = min(i * 1. / max(len(cards) - 1, 1), f_max) - 0.5
            if noanim: card.animation = False
            card.setPos(f * (self.boundingRect().width() - card.boundingRect().width() - d),
                        -0.15 * card.boundingRect().height() if card.isRaised() else 0)
            card.setRotation(0)
            card.setZValue(i)
            if noanim: card.animation = True
            card.show()

    def update(self, rect=QtCore.QRectF()):
        ''''''
        self.update_cards()
        self.setZValue(0)

        QtGui.QGraphicsItem.update(self, rect)

    def boundingRect(self):
        ''''''
        return QtCore.QRectF(self.box)

    def setSize(self, size):
        ''''''
        self.box = QtCore.QRect(QtCore.QPoint(-size.width() / 2, -size.height() / 2), size)  # x,y,size

        if abs(self.boundingRect().width() / self.boundingRect().height() - self.sett.resources['seats'].width() * 4.0 /
                self.sett.resources['seats'].height()) < \
                abs(self.boundingRect().width() / self.boundingRect().height() - self.sett.resources[
                    'seats_large'].width() * 4.0 / self.sett.resources['seats_large'].height()):
            image = self.parentItem().sett.resources['seats']
        else:
            image = self.parentItem().sett.resources['seats_large']
        self.graphics = []
        for i in range(4):
            self.graphics.append(image.copy(0, image.height() * i / 4.,
                                            image.width(), image.height() / 4.).scaled(self.boundingRect().width(),
                                                                                       self.boundingRect().height(),
                                                                                       transformMode=QtCore.Qt.SmoothTransformation))

        self.update_cards(noanim=True)
        # self.new_layout()

    def paint(self, painter, option, widget=None):
        if self.player == None: return

        i = 0
        if self.player == self.parentItem().attacking_player:
            i = 2
        elif self.player == self.parentItem().next_attacking_player():
            i = 1
        elif self.player == self.parentItem().next_attacking_player(+1):
            i = 3

        painter.setPen(QtCore.Qt.NoPen)
        painter.setRenderHints(QtGui.QPainter.SmoothPixmapTransform)
        painter.drawImage(self.boundingRect(), self.graphics[i])

        ##        color = QtGui.QColor('darkgrey') #QtCore.Qt.NoBrush
        ##        if self.player == None:
        ##            color = QtGui.QColor(0,0,0,0)
        ##        elif self.player == self.parentItem().attacking_player:
        ##            color = QtGui.QColor('green')
        ##        elif self.player == self.parentItem().next_attacking_player():
        ##            color = QtGui.QColor('red')
        ##        elif self.player == self.parentItem().next_attacking_player(+1):
        ##            color = QtGui.QColor('yellow')
        ##        painter.setBrush(color)
        ##        painter.setPen(QtGui.QColor('black'))
        ##        painter.drawEllipse(self.boundingRect().center().x()-5, self.boundingRect().top()-5, 10, 10)
        ##
        ##        painter.drawText(self.boundingRect(), QtCore.Qt.AlignTop, str(self.player))
        if self.player != None:
            if self.player.score[2] != None and not self.player.active:
                painter.setPen(QtGui.QColor('gold'))
                font = painter.font()
                font.setPointSize(max(1, 0.5 * self.boundingRect().height()))
                painter.setFont(font)
                painter.rotate(-self.rotation())
                painter.drawText(self.boundingRect(), QtCore.Qt.AlignCenter, str(self.player.score[2]))
                painter.rotate(self.rotation())
