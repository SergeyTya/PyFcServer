"""
Основной скрипт программы.
Запускает конфигуратор окна, подключает слоты и отображает окно.
"""
# Импортируем системый модуль для корректного закрытия программы
import io
# Импортируем минимальный набор виджетов
import termios

import minimalmodbus
import serial
from PyQt5.QtGui import QDoubleValidator, QValidator, QIntValidator
from PyQt5.QtWidgets import QApplication, QWidget, QSlider, QAbstractSlider, QMessageBox, QMainWindow
# Импортируем созданный нами класс со слотами
# from qtpy import QtCore
from PyQt5.uic.properties import QtWidgets

from form_slots import MainWindowSlots
from PyQt5.QtCore import QTimer, QObject, QThread, pyqtSlot, QEventLoop
from PyQt5 import QtCore
import server as srv
import sys
import pyqtgraph as pg
import LogerGraf


# Создаём ещё один класс, наследуясь от класса со слотами
class MainWindow(QMainWindow, MainWindowSlots):

    def __init__(self, app, srv, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self) # form config
        self.app = app # application
        self.srv = srv # modbus server
        # graphs
        self.graphWidget = pg.PlotWidget()
        self.indicators = [
            self.lineEdit_freq,
            self.lineEdit_vout, self.lineEdit_vbus,
            self.lineEdit_vgrd, self.lineEdit_curr,
            self.lineEdit_tfrc, self.lineEdit_pmtr,
            self.lineEdit_tmtr
        ]

        self.labels = [
            self.label_freq,
            self.label_vout, self.label_vbus,
            self.label_vgrd, self.label_curr,
            self.label_tfrc, self.label_pmtr,
            self.label_tmtr
        ]
        self.loggers = [0] * len(self.indicators)
        # Подключить созданные нами слоты к виджетам
        self.connect_slots()
        self.prodseninit()

    # Подключаем слоты к виджетам
    def connect_slots(self):
        #self.pushButton_Scan.clicked.connect(self.btn_connect_push)
        # setup table ContextMenu
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.signal_qtable_contmenu)
        self.horizontalSlider.sliderReleased.connect(self.signal_slider_moved)
        self.horizontalSlider.valueChanged.connect(self.signal_slider_changed)
        self.pushButton_Start.clicked.connect(lambda: self.cmd_list.append("write 0 0 1"))
        self.pushButton_Stop.clicked.connect(lambda: self.cmd_list.append("write 0 0 2"))
        self.pushButton_Reset.clicked.connect(lambda: self.cmd_list.append("write 0 0 4"))

        # self.pushButton_Revers.clicked.connect(lambda: self.cmd_list.append("write 0 4 4"))
        tvl = QDoubleValidator()
        tvl.setRange(0, 10000, 8)
        self.lineEdit_freqref.setValidator(tvl)
        self.lineEdit_freqref.returnPressed.connect(self.signal_lineedit_freref_pressed)
        self.lineEdit_freqref.textChanged.connect(self.signal_lineedit_freqref_changed)

        # connect open logger function to lineedit
        def fo(x): return lambda: self.loggers[x].show() # function producing lambda
        for i, el in enumerate(self.indicators):
            log_name = self.labels[i].text() + ", " + self.indicators[i].toolTip()
            self.loggers[i] = LogerGraf.LoggerWindow(log_name)
            el.returnPressed.connect(fo(i))

        # menu bar connect
        self.action_search.triggered.connect(lambda : self.signal_search(Param=False))
        self.action_searchparam.triggered.connect(lambda: self.signal_search(Param=True))

    def closeEvent(self, *args, **kwargs):
        super().close()
        self.app.exit()


if __name__ == '__main__':
    # Создаём экземпляр нашего UI
    ui = MainWindow(QApplication(sys.argv), srv.Server())
    # Отображаем окно
    ui.show()
    # поток
    timer = QTimer()
    timer.timeout.connect(ui.proc)
    timer.start(200)

    # thread in timer to process serial communication
    class ServerProcTread(QThread):

        def __init__(self, ui, *args, **kwargs, ):
            QThread.__init__(self, *args, **kwargs)
            self.ui = ui
            self.srv = ui.srv

        def run(self):
            try:
                try:

                    # while len(self.cmd_list) != 0: self.srv.main(inpt=self.cmd_list.pop(0))
                    while len(self.ui.cmd_list) != 0:
                        try:
                            self.srv.main(inpt=self.ui.cmd_list[0])
                            self.ui.send_total += 1;
                        except ValueError: pass
                        self.ui.cmd_list.pop(0)
                except (
                        termios.error,
                        serial.serialutil.SerialException,
                        srv.ServerError,
                ) as e:
                    print(e)
                    self.srv.main(inpt="close")
                    self.ui.cmd_list.clear()
            except (
                    minimalmodbus.NoResponseError,
                    minimalmodbus.InvalidResponseError,
            ) as e:
                print(e)
                self.ui.send_err += 1


    th = ServerProcTread(ui)
    timer2 = QTimer()
    timer2.timeout.connect(lambda: th.start())
    timer2.start(20)
    # Обрабатываем нажатие на кнопку окна "Закрыть"

    sys.exit(ui.app.exec_())
