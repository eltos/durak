from PyQt4 import QtGui, QtCore
import time



class Button(QtGui.QGraphicsItem):
    def __init__(self, parent,
                 on_click=lambda: None, size=QtCore.QSize(120, 20)):
        QtGui.QGraphicsItem.__init__(self, parent)
        self.tr = self.parentItem().tr
        self.disabled = False
        self.text = ''
        self.on_click = on_click

        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)

        self.box = QtCore.QRect(QtCore.QPoint(-size.width() / 2, -size.height() / 2), size)  # x,y,size

        self.blinkcount = 0
        self.blinktimer = QtCore.QTimer()
        self.blinktimer.setInterval(200)
        QtCore.QObject.connect(self.blinktimer, QtCore.SIGNAL('timeout()'), self.blinknow)

    def setDisabled(self, disabled=True):
        self.disabled = disabled

    def setText(self, text):
        self.text = text

    def blink(self):
        self.blinkcount = 5
        self.blinknow()

    def blinknow(self):
        if self.blinkcount > 0:
            self.blinkcount -= 0.5
            if not self.blinktimer.isActive():
                self.blinktimer.start()
            self.update()
        else:
            self.blinktimer.stop()

    # def update(self, rect=QtCore.QRectF()):
    #    QtGui.QGraphicsItem.update(self, rect)

    def mousePressEvent(self, event):
        QtGui.QGraphicsItem.mousePressEvent(self, event)
        self.update()

    def mouseReleaseEvent(self, event):
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)
        self.update()
        if not self.disabled and self.boundingRect().contains(event.pos()):
            self.on_click()

    def setSize(self, size):
        self.box = QtCore.QRect(QtCore.QPoint(-size.width() / 2, -size.height() / 2), size)  # x,y,size

    def boundingRect(self):
        return QtCore.QRectF(self.box)

    def paint(self, painter, option, widget=None):
        inBlink = self.blinkcount % 1 >= 0.5 and not self.disabled
        painter.setPen(self.parentItem().sett.colors['button blink' if inBlink else 'font'])
        painter.setBrush(self.parentItem().sett.colors['button'])

        if (option.state & QtGui.QStyle.State_Sunken) and not self.disabled:
            painter.setBrush(self.parentItem().sett.colors['button highlight'])

        painter.drawRect(self.boundingRect())
        painter.setPen(self.parentItem().sett.colors[
                           'font disabled' if self.disabled else 'font'])

        font = painter.font()
        font.setPointSize(max(1, font.pointSize() * self.boundingRect().width() / 120))
        painter.setFont(font)
        painter.drawText(self.boundingRect(), QtCore.Qt.AlignCenter, self.text)


class TimerButton(Button):
    def __init__(self, parent,
                 on_click=lambda: None, size=QtCore.QSize(120, 20),
                 auto_click_delay=float("INF")):
        Button.__init__(self, parent, on_click=on_click, size=size)
        # QtGui.QGraphicsItem.__init__(self, parent)
        # self.tr = self.parentItem().tr
        # self.state = state
        # self.disabled=False
        # self.text = ''
        # self.on_click = on_click

        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        QtCore.QObject.connect(self.timer, QtCore.SIGNAL('timeout()'), self.update)

        self.start_time = time.time()

        # self.time_disabled = False

        # self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable)

        # self.box = QtCore.QRect(QtCore.QPoint(-size.width()/2, -size.height()/2), size) # x,y,size

        # self.state = state
        # self._setStateText()

        self.auto_click_delay = auto_click_delay
        self.auto_click_time = float("INF")

        self.timer.start()

    # def _setStateText(self):
    #    self.text = {1:self.tr('Take cards'),
    #                 2:self.tr('End attack')}[self.state]

    # def setState(self, state=1):
    #    self.state = state
    #    self._setStateText()
    #    #if self.state == 2:
    #    #    self.timer.start()
    #    #else:
    #    #    self.timer.stop()
    #    self.timer.start()
    #
    #    self.update()

    def mouseReleaseEvent(self, event):
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)
        self.update()
        if not self.disabled and self.boundingRect().contains(event.pos()):
            self.disableTimer()
            self.on_click()

    def resetTimer(self):

        self.auto_click_time = time.time() + self.auto_click_delay
        # self.time_disabled = True

    def disableTimer(self):
        self.auto_click_time = float("INF")

    def update(self, rect=QtCore.QRectF()):
        Button.update(self, rect)
        if self.auto_click_time <= time.time() and \
                self.timer.isActive():
            self.disableTimer()
            # self.time_disabled = False
            # self.timer.stop()
            self.on_click()

    def paint(self, painter, option, widget=None):
        inBlink = self.blinkcount % 1 >= 0.5 and not self.disabled
        painter.setPen(self.parentItem().sett.colors['button blink' if inBlink else 'font'])
        painter.setBrush(self.parentItem().sett.colors['button'])

        # if (option.state & QtGui.QStyle.State_Sunken) and not self.disabled:
        #    painter.setBrush(self.parentItem().sett.colors['button highlight'])

        painter.drawRect(self.boundingRect())
        painter.setPen(self.parentItem().sett.colors[
                           'font disabled' if self.disabled or self.parentItem().end_attack_time > time.time() else 'font'])

        font = painter.font()
        font.setPointSize(max(1, font.pointSize() * self.boundingRect().width() / 120))
        painter.setFont(font)

        add = ""
        if self.auto_click_time > time.time() and \
                        self.auto_click_time != float("INF") and \
                not self.parentItem().end_attack_time > time.time():
            add = " - %.0f" % round(self.auto_click_time - time.time() + 0.5)

        painter.drawText(self.boundingRect(), QtCore.Qt.AlignCenter, self.text + add)

        if self.parentItem().end_attack_time > time.time():
            font.setBold(True)
            # font.setPointSize(font.pointSize()*self.boundingRect().width()/120)
            painter.setFont(font)
            painter.setPen(self.parentItem().sett.colors['font'])
            painter.drawText(self.boundingRect(), QtCore.Qt.AlignCenter,
                             str(int(self.parentItem().end_attack_time - time.time() + 1)))
















