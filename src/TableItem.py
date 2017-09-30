from PyQt4 import QtGui, QtCore

TESTING = False


class TableItem(QtGui.QGraphicsItem):
    def __init__(self, parent, table, size=QtCore.QSize(705 ,270)):
        ''''''
        QtGui.QGraphicsItem.__init__(self, parent)

        self.table = table
        # self.parentItem() = parent
        self.sett = self.parentItem().sett

        # self.cards = [] # [[A,D],[A,D],...]

        self.box = QtCore.QRect(QtCore.QPoint(-size.width( ) /2, -size.height( ) /2), size) # x,y,size

        self.set_table(table)

    def card_moved(self, card, pos=None):
        if pos != None: pos = self.mapToParent(pos)
        self.parentItem().card_moved(self, card, pos)
        self.update()

    def set_table(self, table):
        ''''''
        self.table = table
        if self.table == None:
            self.reset()
        self.update()

    def reset(self):
        ''''''
        # while len(self.cards) > 0:
        #    self.cards[0][0].hide()
        #    self.cards[0][1].hide()
        #    del self.cards[0]
        pass

    def update_cards(self, noanim=False):
        ''''''
        if self.table == None:
            return

        # precalc positioning
        n = len(self.table.get_cards())
        if n == 0: return
        card = self.parentItem().card_Items[self.table.get_cards()[0][0]]

        w = self.boundingRect().width()
        h = self.boundingRect().height()
        d0 = max(card.boundingRect().width( ) * 15 /70,
                 card.boundingRect().height( ) * 15 /105)
        d = max(w,  h ) /2
        nx = ny = 0

        # d = max(w, h)

        while nx* ny < n:
            ax = card.boundingRect().width() + d
            ay = card.boundingRect().height() + d

            nx = (w - d) // (ax + d)
            ny = (h - d) // (ay + d)

            if nx * ny < n:
                d -= d0 / 5

        # walk through cards
        for i in range(len(self.table.get_cards())):
            Acard = self.parentItem().card_Items[self.table.get_cards()[i][0]]
            if self.table.get_cards()[i][1] != None:
                Dcard = self.parentItem().card_Items[self.table.get_cards()[i][1]]
            else:
                Dcard = None

            if noanim: Acard.animation = False
            Acard.setParentItem(self)
            Acard.set_visible(True)
            Acard.show()
            if Dcard != None:
                if noanim: Dcard.animation = False
                Dcard.setParentItem(self)
                Dcard.set_visible(True)
                Dcard.show()

            ix = i % nx
            iy = i // nx

            px = ix * ax + (ix + 1) * (w - nx * ax) / (nx + 1.) + ax / 2. - w / 2.
            py = iy * ay + (iy + 1) * (h - ny * ay) / (ny + 1.) + ay / 2. - h / 2.

            Acard.setPos(px - d0 / 2., py - d0 / 2.)
            Acard.setRotation(0)
            Acard.setZValue(i)
            Acard.setRaised(False)
            if noanim: Acard.animation = True
            if Dcard != None:
                Dcard.setPos(px + d0 / 2., py + d0 / 2.)
                Dcard.setRotation(0)
                Dcard.setZValue(n + i)
                Dcard.setRaised(False)
                if noanim: Dcard.animation = True

    def update(self, rect=QtCore.QRectF()):
        ''''''
        self.update_cards()
        self.setZValue(-1)
        QtGui.QGraphicsItem.update(self, rect)

    def setSize(self, size):
        ''''''
        self.box = QtCore.QRect(QtCore.QPoint(-size.width() / 2, -size.height() / 2), size)  # x,y,size
        self.update_cards(noanim=True)

    def boundingRect(self):
        ''''''
        return QtCore.QRectF(self.box)

    def paint(self, painter, option, widget=None):
        painter.setRenderHints(QtGui.QPainter.SmoothPixmapTransform)
        painter.drawImage(self.boundingRect(), self.sett.resources['table'])

        # painter.setBrush(QtCore.Qt.NoBrush)
        # painter.setPen(QtGui.QColor('darkgrey'))
        # painter.drawRect(self.boundingRect())

        if not TESTING: return
        # TESTING:
        painter.setPen(QtGui.QColor('darkgrey'))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(self.boundingRect())

        if self.table == None:
            return
        n = len(self.table.get_cards())
        # n = int(1+(time.time()/3)%20)

        Acard = self.parentItem().card_Items[self.parentItem().card_Items.keys()[0]]
        d = max(Acard.boundingRect().width() * 15 / 70,
                Acard.boundingRect().height() * 15 / 105)
        d0 = d
        nx = ny = 0
        w = self.boundingRect().width()
        h = self.boundingRect().height()

        d = max(w, h)

        while nx * ny < n or nx * ny < 1:
            ax = Acard.boundingRect().width() + d
            ay = Acard.boundingRect().height() + d

            nx = (w - d) // (ax + d)
            ny = (h - d) // (ay + d)

            if nx * ny < n or nx * ny < 1:
                d -= d0 / 5

        for i in range(int(min(nx * ny, 1000))):
            Acard = self.parentItem().card_Items[self.parentItem().card_Items.keys()[0]]

            ix = i % nx
            iy = i // nx

            px = ix * ax + (ix + 1) * (w - nx * ax) / (nx + 1.) + ax / 2. - w / 2.
            py = iy * ay + (iy + 1) * (h - ny * ay) / (ny + 1.) + ay / 2. - h / 2.

            painter.setPen(QtCore.Qt.SolidLine)
            painter.setBrush(QtGui.QColor('blue' if i < n else 'red'))

            painter.drawRect(px - d0 / 2.
                             - Acard.boundingRect().width() / 2,
                             py - d0 / 2.
                             - Acard.boundingRect().height() / 2,
                             Acard.boundingRect().width(), Acard.boundingRect().height())

            painter.setBrush(QtGui.QColor('green' if i < n else 'yellow'))

            painter.drawRect(px + d0 / 2.
                             - Acard.boundingRect().width() / 2,
                             py + d0 / 2.
                             - Acard.boundingRect().height() / 2,
                             Acard.boundingRect().width(), Acard.boundingRect().height())
