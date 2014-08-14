# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import sys
import pysrt


class ControlMainWindow(QtGui.QLabel):

    def __init__(self, parent=None):
        super(ControlMainWindow, self).__init__(parent)
        
        # make window frameless, topmost and transparent
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setMinimumSize(800, 80)

        self.setWordWrap(True)
        self.setAlignment(QtCore.Qt.AlignCenter)

        # font config
        font = QtGui.QFont()
        font.setFamily('mono')
        font.setBold(True)
        font.setPointSize(24)
        self.setFont(font)
        self.setText('open srt file by clicking here!')

        # init local vars
        self.offset = 0
        self.moving = False
        self.pos = QtCore.QPoint(0, 0)
        self.subPos = 0

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.onTimeout)
        self.timer.setSingleShot(True)

    @QtCore.pyqtSlot()
    def onTimeout(self):
        '''
        Change to next subtitle item.
        '''
        self.setText(self.subs[self.subPos].text)

        # calc duration
        d = self.subs[self.subPos].end - self.subs[self.subPos].start
        mil = (((d.hours * 60) + d.minutes) * 60 + d.seconds) * \
            1000 + d.milliseconds

        self.subPos += 1
        self.timer.start(mil)

    def openFile(self):
        '''
        Choose srt file and play it.
        '''
        self.timer.stop()
        filename = QtGui.QFileDialog.getOpenFileName(
            self, 'Open File', '~/', '*.srt;;*')
        if not filename:
            return
        self.subs = pysrt.open(unicode(filename), encoding='cp936')
        self.playSrt()

    def findPos(self, startTime):
        '''
        Find out which subtitle item should be displayed at startTime.
        Using binary search method.
        '''
        def fp(a, b):
            c = a + (b - a) / 2
            if a > b:
                return c # return nearest subtitle item if there is no subtitle at startTime
            elif startTime > self.subs[c].end:
                return fp(c + 1, b)
            elif startTime < self.subs[c].start:
                return fp(a, c - 1)
            else:
                return c
        return fp(0, len(self.subs) - 1)

    def playSrt(self, startTime=0):
        if not hasattr(self, 'subs'):
            return
        self.setText('')
        self.timer.stop()
        self.subPos = self.findPos(startTime)
        d = self.subs[self.subPos].start - startTime

        # if already begins, then show it
        if d < 0:
            d = self.subs[self.subPos].end - startTime
            self.setText(self.subs[self.subPos].text)
            self.subPos += 1
            print d

        mil = (((d.hours * 60) + d.minutes) * 60 + d.seconds) * \
            1000 + d.milliseconds
        self.timer.start(mil)

    # def paintEvent(self, event):
    #     painter = QtGui.QPainter(self)
    # painter.setFont(QFont)

    #     painter.setPen(QtGui.QColor(0, 0, 0, 200))
    #     painter.drawText(1, 1, 800, 60, QtCore.Qt.AlignCenter, self.text())

    #     painter.setPen(QtGui.QColor(0, 0, 0))
    #     painter.drawText(0, 0, 800, 60, QtCore.Qt.AlignCenter, self.text())

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.pos = event.globalPos()
            self.offset = event.globalPos() - self.frameGeometry().topLeft()
            self.setCursor(QtCore.Qt.PointingHandCursor)
            self.moving = True

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.moving = False
            if (event.globalPos() - self.pos) == QtCore.QPoint(0, 0):
                self.openFile()

        elif event.button() == QtCore.Qt.RightButton:
            newStartTime, succ = QtGui.QInputDialog.getText(
                self, "Input start time", "", QtGui.QLineEdit.Normal, "00:00:00,000")
            if succ:
                self.playSrt(
                    pysrt.SubRipTime.from_string(unicode(newStartTime)))

    def mouseMoveEvent(self, event):
        if self.moving:
            self.move(event.globalPos() - self.offset)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()


app = QtGui.QApplication(sys.argv)
mySW = ControlMainWindow()
mySW.show()
sys.exit(app.exec_())
