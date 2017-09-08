from PyQt4 import QtGui, QtCore


class TrashItem(QtGui.QGraphicsItem):
    def __init__(self, parent, trash):
        ''''''
        QtGui.QGraphicsItem.__init__(self, parent)

        self.trash = trash
        self.sett = self.parentItem().sett

        self.set_trash(trash)

    def card_moved(self, card, pos=None):
        if pos != None: pos = self.mapToParent(pos)
        self.parentItem().card_moved(self, card, pos)
        self.update()

    def set_trash(self, trash):
        ''''''
        self.trash = trash
        self.update()

    def update_cards(self, noanim=False):
        ''''''
        if self.trash == None:
            return

        for i in range(len(self.trash.get_cards())):
            card = self.parentItem().card_Items[self.trash.get_cards()[-1 - i]]
            # self.cards[i].set_card(self.stack.get_cards()[-1-i])
            if noanim: card.animation = False
            card.setParentItem(self)
            card.show()
            card.setPos(0, 0)
            card.set_visible(True)
            card.setZValue(i)
            card.setRaised(False)
            QtCore.QTimer.singleShot(card.POSanim.duration(), card.hide)
            if noanim: card.animation = True

    def update(self, rect=QtCore.QRectF()):
        self.update_cards()
        self.setZValue(0)
        QtGui.QGraphicsItem.update(self, rect)


    def boundingRect(self):
        return QtCore.QRectF(0,0,0,0)


    def paint(self, painter, option, widget=None):
        pass