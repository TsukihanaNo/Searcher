from PySide import QtCore, QtGui
import sys


class ListDelegate(QtGui.QAbstractItemDelegate):
    def __init__(self, parent = None):
        super(ListDelegate,self).__init__(parent)
        self.parent = parent

    def paint(self,painter,option, index):
        r = QtCore.QRect()
        r = option.rect
        linepen = QtGui.QPen(QtGui.QColor.fromRgb(211,211,211),1,QtCore.Qt.SolidLine)
        lineMarkedPen = QtGui.QPen(QtGui.QColor.fromRgb(0,90,131),1,QtCore.Qt.SolidLine)
        fontPen = QtGui.QPen(QtGui.QColor.fromRgb(5,5,5),1, QtCore.Qt.SolidLine)
        fontPenSmall = QtGui.QPen(QtGui.QColor.fromRgb(5,5,5,180),1,QtCore.Qt.SolidLine)
        fontMarkedPen = QtGui.QPen(QtCore.Qt.white,1,QtCore.Qt.SolidLine)

        if option.state & QtGui.QStyle.State_Selected:
            painter.setBrush(QtGui.QColor.fromRgb(0,0,155,100))
            painter.drawRect(r)

            painter.setPen(lineMarkedPen)
            painter.drawLine(r.topLeft(),r.topRight())
            painter.drawLine(r.topRight(),r.bottomRight())
            painter.drawLine(r.bottomLeft(),r.bottomRight())
            painter.drawLine(r.topLeft(),r.bottomLeft())

            painter.setPen(fontMarkedPen)
        elif option.state & QtGui.QStyle.State_MouseOver:
            painter.setBrush(QtGui.QColor.fromRgb(0,0,155,30))
            painter.drawRect(r)

            painter.setPen(lineMarkedPen)
            painter.drawLine(r.topLeft(),r.topRight())
            painter.drawLine(r.topRight(),r.bottomRight())
            painter.drawLine(r.bottomLeft(),r.bottomRight())
            painter.drawLine(r.topLeft(),r.bottomLeft())

            painter.setPen(fontMarkedPen)

        else:
            if index.row()%2==0:
                painter.setBrush(QtGui.QColor.fromRgb(182,177,177,40))
            else:
                painter.setBrush(QtCore.Qt.white)
            painter.drawRect(r)
            painter.setPen(linepen)
            painter.drawLine(r.topLeft(),r.topRight())
            painter.drawLine(r.topRight(),r.bottomRight())
            painter.drawLine(r.bottomLeft(),r.bottomRight())
            painter.drawLine(r.topLeft(),r.bottomLeft())

        painter.setPen(fontPen)
        desc = index.data(QtCore.Qt.DisplayRole)
        title = index.data(QtCore.Qt.UserRole)
        ic = QtGui.QIcon(index.data(QtCore.Qt.DecorationRole))

        if not ic.isNull():
            ic.paint(painter,r,QtCore.Qt.AlignLeft)

        r = option.rect.adjusted(32,1,1,1)
        if sys.platform=='win32':
            painter.setFont(QtGui.QFont("Lucida",9,QtGui.QFont.Bold))
            painter.drawText(r.left(),r.top(),r.width(),r.height(),QtCore.Qt.AlignLeft,title)

            painter.setPen(fontPenSmall)
            #r = option.rect.adjusted(30,1,1,1)
            painter.setFont(QtGui.QFont("Lucida",7,QtGui.QFont.Normal))
            painter.drawText(r.left(),r.top(),r.width(),r.height(),QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeft,desc)
        elif sys.platform =='darwin':
            painter.setFont(QtGui.QFont("Lucida",12,QtGui.QFont.Bold))
            painter.drawText(r.left(),r.top(),r.width(),r.height(),QtCore.Qt.AlignLeft,title)

            #r = option.rect.adjusted(30,1,1,1)
            painter.setFont(QtGui.QFont("Lucida",9,QtGui.QFont.Normal))
            painter.drawText(r.left(),r.top(),r.width(),r.height(),QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeft,desc)
        else:
            painter.setFont(QtGui.QFont("Lucida",10,QtGui.QFont.Bold))
            painter.drawText(r.left(),r.top(),r.width(),r.height(),QtCore.Qt.AlignLeft,title)

            #r = option.rect.adjusted(30,1,1,1)
            painter.setFont(QtGui.QFont("Lucida",8,QtGui.QFont.Normal))
            painter.drawText(r.left(),r.top(),r.width(),r.height(),QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeft,desc)

    def sizeHint(self,option, index):
        return QtCore.QSize(self.parent.size().width() -25,25)