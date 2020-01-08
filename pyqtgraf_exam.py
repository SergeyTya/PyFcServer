from collections import deque

import PyQt5
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import time

from server import Server


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.PlotWidget()
        #self.graphWidget.setBackground('w')
        self.setCentralWidget(self.graphWidget)
        self.graphWidget.addLegend()
        self.graphWidget.plot([0], [0], name='Axi 1')

        self.srv = Server()
        self.srv.main("connect /dev/ttyACM0 9600 1")
        max_x = 1500
        self.scope_ch0 = deque([0] * max_x, maxlen=max_x)
        self.scope_ch1 = deque([0] * max_x, maxlen=max_x)

    def graf_update(self):
        self.srv.main("read_scope 0")
        self.graphWidget.clear()
        pen = [pg.mkPen(color='r'), pg.mkPen(color='b'), pg.mkPen(color='g'), pg.mkPen(color='y')]

        tmp = len(self.srv.devices[0].scope_fifo)

        for i in range(0, tmp):
            self.graphWidget.plot(
                #range(0, self.srv.devices[0].scope_fifo[i].maxlen),
                self.srv.devices[0].scope_timeline,
                self.srv.devices[0].scope_fifo[i],
                pen=pen[i]
            )

    def get_scope_data(self):
        pass



def main():

    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    timer = QTimer()
    timer.timeout.connect(main.graf_update)
    timer.start(10)

    timer2 = QTimer()
    timer2.timeout.connect(main.get_scope_data)
    timer2.start(100)

    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()