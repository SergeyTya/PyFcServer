from collections import deque

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QMainWindow
from pyqtgraph import PlotWidget


class LoggerWindow(QMainWindow):

    @staticmethod
    def gen(max, val=0):
        while val <= max:
            val += 1
            if val == max: val = 0
            yield val

    def __init__(self, title="", update_time=300, *args,  **kwargs, ):
        super(LoggerWindow, self).__init__(*args, **kwargs)
        self.graphWidget = PlotWidget()
        self.setCentralWidget(self.graphWidget)
        self.setWindowTitle(title)
        max_x = 10000
        self.log = [deque([0] * max_x, maxlen=max_x), deque([0] * max_x, maxlen=max_x)]
        t0 = 0
        period = 1

        rng = range(0, max_x)
        rng = map(lambda x: t0 + x * period * 0.001, rng)

       # self.log[0].extend(range(0, max_x))
        self.log[0].extend(rng)
        self.gnr = self.gen(len(self.log[0]))
        self.timer = QTimer()
        self.timer.timeout.connect(self.updater)
        self.timer.start(update_time)



    def updater(self):
        if self.isHidden(): return
        self.graphWidget.clear()
        self.graphWidget.plot(self.log[0], self.log[1])


    def logValue(self, value):
        cnt = next(self.gnr)
        self.log[1][cnt] = value



