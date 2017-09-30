from PyQt4 import QtGui, QtCore

TESTING = False


class CardItem(QtGui.QGraphicsObject):  # QtGui.QGraphicsItem):
    def __init__(self, parent, card, size=QtCore.QSize(70, 105), visible=True):
        # QtGui.QGraphicsItem.__init__(self, parent)
        QtGui.QGraphicsObject.__init__(self, parent)
        # self.parentItem() = parent
        self.set_visible(visible)
        self.raised = False
        self.moved = None
        self.animation = True

        self.card = card

        # self.box = QtCore.QRect(QtCore.QPoint(-size.width()/2, -size.height()/2), size)
        self.setSize(size)

        # self.setFlag(QtGui.QGraphicsObject.ItemIsMovable)


        # image = self.parentItem().sett.resources['playing_cards']
        # image = image.copy((3-color)*image.width()/4,
        #                   (14-name)*image.height()/13,
        #                   image.width()/4,
        #                   image.height()/13)
        # self.graphic = image


        self.POSanim = QtCore.QPropertyAnimation(self, 'pos', parent=self.scene())
        self.ROTanim = QtCore.QPropertyAnimation(self, 'rotation', parent=self.scene())
        # self.anim = QtCore.QParallelAnimationGroup(self)
        # self.anim.addAnimation(self.POSanim)
        # self.anim.addAnimation(self.ROTanim)
        # QPropertyAnimation(self, 'pos')

    def set_visible(self, visible):
        self.visible = visible or TESTING
        self.setFlag(QtGui.QGraphicsObject.ItemIsMovable, self.visible)
        self.setFlag(QtGui.QGraphicsObject.ItemIsSelectable, self.visible)
        # if not self.visible:

    ##            QtGui.QGraphicsObject.mouseReleaseEvent(self,
    ##                    QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease,
    ##                                      QtCore.QPoint(),
    ##                                      QtCore.Qt.LeftButton,
    ##                                      QtCore.Qt.LeftButton,
    ##                                      QtCore.Qt.NoModifier))
    # self.update()
    # self.parentItem().update()
    # self.update()
    # QtGui.QGraphicsObject.setPos(self, self.pos())

    def boundingRect(self):
        return QtCore.QRectF(self.box)

    def mousePressEvent(self, event):
        self.moved = False

        if not self.visible:  # or self.card == None:
            # event.ignore()
            return
        QtGui.QGraphicsObject.mousePressEvent(self, event)

        self.raised = not self.raised
        self.setZValue(100)
        self.parentItem().setZValue(1)
        self.update()

    def setRaised(self, raised):
        self.raised = raised

    def isRaised(self):
        return self.raised

    def mouseMoveEvent(self, event):
        self.moved = True

        if not self.visible:  # or self.card == None:
            # event.ignore()
            return
        QtGui.QGraphicsObject.mouseMoveEvent(self, event)

        self.raised = False
        self.setZValue(100)
        self.parentItem().setZValue(1)

    def mouseReleaseEvent(self, event):
        process_move = self.moved and \
                       self.POSanim.state() != self.POSanim.Running and \
                       self.ROTanim.state() != self.ROTanim.Running
        self.moved = None
        # if not self.visible:# or self.card == None:
        # event.ignore()
        #    return
        QtGui.QGraphicsObject.mouseReleaseEvent(self, event)

        # self.setZValue(0)
        pos = QtCore.QPointF(0, 0)  # event.pos()
        self.update()
        if process_move:
            self.parentItem().card_moved(self, self.mapToParent(pos))
        self.parentItem().update()

    def mouseDoubleClickEvent(self, event):

        if not self.visible:  # or self.card == None:
            # event.ignore()
            return
        QtGui.QGraphicsObject.mouseDoubleClickEvent(self, event)

        self.raised = True
        # self.setZValue(0)
        self.update()
        self.moved = None
        self.parentItem().card_moved(self)

    def setPos(self, *pos):
        # print time.time(),'posSET'
        # if self.moved != None:
        #    return

        if len(pos) == 1:
            pos = pos[0]
        elif len(pos) == 2:
            pos = QtCore.QPointF(*pos)

        _from = self.pos()
        to = pos

        if self.moved == None:
            QtGui.QGraphicsObject.setPos(self, pos)
            if self.animation and _from != to:
                self.POSanimation(_from, to)
            else:
                self.POSanim.stop()

    def setSize(self, size):
        ''''''
        self.box = QtCore.QRect(QtCore.QPoint(-size.width() / 2, -size.height() / 2),
                                size)  # x,y,size

        image = self.parentItem().sett.resources['playing_cards_back']
        self.graphic_back = image.scaled(self.box.width(), self.box.height(),
                                         transformMode=QtCore.Qt.SmoothTransformation)

        image = self.parentItem().sett.resources['playing_cards']
        image = image.copy((3 - self.card.get_color()) * image.width() / 4,
                           (14 - self.card.get_name()) * image.height() / 13,
                           image.width() / 4,
                           image.height() / 13).scaled(
            self.boundingRect().width(),
            self.boundingRect().height(),
            transformMode=QtCore.Qt.SmoothTransformation)
        self.graphic = image

    def setParentItem(self, parent):
        # print time.time(),'posPARENT'

        P_from = parent.mapFromItem(self.parentItem(), self.pos())
        Pto = self.pos()  # parent.mapToItem(self.parentItem(), self.pos())
        R_from = self.rotation() + self.parentItem().rotation() - parent.rotation()
        Rto = self.rotation()

        # print 'FROM', self.parentItem(), self.parentItem().rotation()
        # print 'TO', parent, parent.rotation()
        # print 'SELBST', self.rotation()
        # print R_from, Rto
        # print


        QtGui.QGraphicsObject.setParentItem(self, parent)
        QtGui.QGraphicsObject.setRotation(self, Rto)
        if self.moved == None and self.animation:
            if P_from != Pto:
                self.POSanimation(P_from, Pto)
            else:
                self.POSanim.stop()
            if R_from != Rto:
                self.ROTanimation(R_from, Rto)
            else:
                self.ROTanim.stop()

                # self.anim.connect(self.anim, QtCore.SIGNAL('finished()'), lambda:\
                # QtGui.QGraphicsObject.setParentItem(self, parent)
                # )

    def setRotation(self, rot):
        _from = self.rotation()
        # print self.parentItem().rotation()
        to = rot
        # print _from, 'to', to

        QtGui.QGraphicsObject.setRotation(self, rot)
        if self.animation and _from != to:
            self.ROTanimation(_from, to)
        else:
            self.ROTanim.stop()

            ##    def setZValue(self, z):
            ##
            ##        if self.animation and \
            ##           (self.ROTanim.state() == QtCore.QAbstractAnimation.Running or \
            ##            self.POSanim.state() == QtCore.QAbstractAnimation.Running):
            ##            QtCore.QTimer.singleShot(100,#self.parentItem().sett.getAnimationDuration()*1.1,
            ##                                     lambda: self.setZValue(z))
            ##        else:
            ##            QtGui.QGraphicsObject.setZValue(self, z)

    def ROTanimation(self, _from, to):
        to %= 360
        _from %= 360
        # turning the shorter way:
        to += ((360 if _from > to else -360) if abs(to - _from) > 180 else 0)

        self.ROTanim.stop()
        self.ROTanim.setEasingCurve(QtCore.QEasingCurve.OutQuart)
        self.ROTanim.setStartValue(_from)
        self.ROTanim.setEndValue(to)
        self.ROTanim.setDuration(self.parentItem().sett.getAnimationDuration())
        self.ROTanim.start()

    def POSanimation(self, _from, to):
        self.POSanim.stop()
        # self.anim = QtCore.QPropertyAnimation(self, 'pos', parent=self.scene()) # 'rotation
        self.POSanim.setEasingCurve(QtCore.QEasingCurve.OutQuart)
        self.POSanim.setStartValue(_from)
        self.POSanim.setEndValue(to)
        self.POSanim.setDuration(self.parentItem().sett.getAnimationDuration())
        # def x():
        #    print time.time(),'FERTIG'
        # z = self.zValue()
        # self.setZValue(100)
        # self.anim.connect(self.anim, QtCore.SIGNAL('finished()'), lambda: self.setZValue(z))

        self.POSanim.start()

    def paint(self, painter, option, widget=None):
        # if self.card == None: return

        # painter.setPen(QtCore.Qt.NoPen)
        painter.setPen(QtGui.QPen(QtGui.QColor('black'), 1.5))
        painter.setBrush(QtGui.QBrush(QtGui.QColor('white' if self.visible else 'black')))
        painter.drawRoundRect(self.boundingRect(),
                              self.boundingRect().width() / 7.0,
                              self.boundingRect().width() / 10.5)
        # painter.drawText(self.boundingRect().bottomLeft().x()+10,
        #                 self.boundingRect().bottomLeft().y()-10,
        #                 str(self.card))
        painter.setRenderHints(QtGui.QPainter.SmoothPixmapTransform)
        painter.drawImage(self.boundingRect(),
                          self.graphic if self.visible else self.graphic_back)
        if option.state & QtGui.QStyle.State_Sunken:
            # mouse pressed when moving
            # print self.setZValue(5)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Multiply)
            painter.setBrush(QtGui.QBrush(QtGui.QColor(200, 200, 200, 150)))
            painter.drawRoundRect(self.boundingRect(),
                                  self.boundingRect().width() / 7.0,
                                  self.boundingRect().height() / 10.5)

        if not TESTING: return
        # TESTING
        if self.POSanim.state() == self.POSanim.Running or \
                        self.ROTanim.state() == self.ROTanim.Running:
            i = ((self.POSanim.currentTime() or \
                  self.ROTanim.currentTime()) // 10) % 2
            # import random
            # i = random.randint(0,1)
            painter.setPen(QtCore.Qt.NoPen)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_Multiply)
            painter.setBrush(QtGui.QBrush(
                QtGui.QColor(255, 255 * i, 255 * (1 - i), 150)))
            painter.drawRoundRect(self.boundingRect(),
                                  self.boundingRect().width() / 7.0,
                                  self.boundingRect().height() / 10.5)

    def update(self, rect=QtCore.QRectF()):
        ''''''

        # QtGui.QGraphicsItem.update(self, rect)
        QtGui.QGraphicsObject.update(self, rect)
