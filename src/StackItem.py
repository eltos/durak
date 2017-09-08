from PyQt4 import QtGui, QtCore


class StackItem(QtGui.QGraphicsItem):
    def __init__(self, parent, stack, size=QtCore.QSize(125, 125)):
        ''''''
        QtGui.QGraphicsItem.__init__(self, parent)

        self.stack = stack
        # self.parentItem() = parent
        self.sett = self.parentItem().sett

        # self.cards = []

        self.box = QtCore.QRect(QtCore.QPoint(-size.width() / 2, -size.height() / 2), size)  # x,y,size
        self.graphic = QtGui.QImage()
        self.set_stack(stack)

    def card_moved(self, card, pos=None):
        if pos != None: pos = self.mapToParent(pos)
        self.parentItem().card_moved(self, card, pos)
        self.update()

    def set_stack(self, stack):
        ''''''
        self.stack = stack
        if self.stack == None:
            self.reset()
        self.update()

    def reset(self):
        ''''''
        # while len(self.cards) > 0:
        #    self.cards[0].hide()
        #    del self.cards[0]
        pass

    def update_cards(self, noanim=False):
        ''''''
        if self.stack == None:
            return

        for i in range(len(self.stack.get_cards())):
            card = self.parentItem().card_Items[self.stack.get_cards()[-1 - i]]
            # self.cards[i].set_card(self.stack.get_cards()[-1-i])
            if noanim: card.animation = False
            card.setParentItem(self)
            card.show()

            if i == 0:
                card.setPos(card.boundingRect().width() / 2. - card.boundingRect().height() / 4., 0)
                card.setRotation(270)
                card.set_visible(True)
            else:
                card.setPos(-card.boundingRect().height() / 4., 0)
                card.setRotation(0)
                card.set_visible(False)
            card.show()
            card.setZValue(i)
            card.setRaised(False)
            if noanim: card.animation = True

        if self.stack.get_trump() != None:
            image = self.parentItem().sett.resources['playing_symbols']
            self.graphic = image.copy((3 - self.stack.get_trump()) * image.width() / 4, 0,
                                      image.width() / 4, image.height())
        else:
            self.graphic = QtGui.QImage()

    def update(self, rect=QtCore.QRectF()):
        ''''''
        self.update_cards()
        self.setZValue(0)
        QtGui.QGraphicsItem.update(self, rect)

    def setSize(self, size):
        ''''''
        self.box = QtCore.QRect(QtCore.QPoint(-size.width() / 2, -size.height() / 2), size)  # x,y,size
        self.update_cards(noanim=True)

    def boundingRect(self):
        ''''''
        return QtCore.QRectF(self.box)

    def paint(self, painter, option, widget=None):
        # painter.setPen(QtCore.Qt.NoPen)
        # painter.setBrush(QtGui.QColor('grey'))
        # painter.drawRect(self.boundingRect())
        painter.setRenderHints(QtGui.QPainter.SmoothPixmapTransform)
        painter.drawImage(self.boundingRect(), self.sett.resources['stack'])
        painter.drawImage(self.boundingRect(), self.graphic)
