'''
Created on 28 нояб. 2019 г.

@author: sergey
'''
import ctypes
import io

import minimalmodbus
import serial
from PyQt5.QtCore import pyqtSlot, QTimer
from PyQt5.QtGui import QIntValidator, QCursor, QTextCursor, QDoubleValidator
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QComboBox, QLineEdit, QMenu, QHeaderView, QScrollBar, \
    QPushButton, QSizePolicy
import json
import ProdSensEmu

# from qtconsole.qt import QtCore, QtGui
from PyQt5 import QtCore

"""
Пользовательские слоты для виджетов.
"""
# Импортируем класс интерфейса из созданного конвертером модуля
from form_ui import Ui_Form

import server as srv
import sys


# Создаём собственный класс, наследуясь от автоматически сгенерированного
class MainWindowSlots(Ui_Form):

    def __init__(self):
        self.cmd_list = []
        self.srv = srv.Server()
        self.ylwcells = []
        self.out_tmp = sys.stdout
        sys.stdout = io.StringIO("", newline=None)
        self.jsdtr = None
        self.loggers = [0] * 10
        print("aefwsgr")

    def proc(self):

        # First int
        if len(self.srv.devices) > 0: self.widget_init()
        self.check_holding_table()

        # input indicators refresh
        if len(self.srv.devices) > 0:
            self.cmd_list.append("read 0 * 4")
            if len(self.srv.devices[0].inputs) >= len(self.indicators):
                for i in range(len(self.indicators) - 1):
                    tmp = ctypes.c_int16(self.srv.devices[0].inputs[i + 3])
                    self.indicators[i].setText(str(tmp.value / 10))
                self.label_DevStatus.setText(str(hex(self.srv.devices[0].inputs[2])))

        # prodsens emulator controls
        if len(self.srv.devices) > 0:
            if len(self.srv.devices[0].inputs) > 0:
                try:
                    tmp = float(self.lineEdit_EmuOut_gain.text())
                    self.pse.setOutpuGain(tmp)
                except ValueError: pass
                self.pse.setFreqValue(float(self.srv.devices[0].inputs[3]/10))
                #self.lineEdit_EmuOut.setText(str(self.pse.pse_float_value).format("f%2"))
                self.lineEdit_EmuOut.setText('{0: >#016.2f}'.format(self.pse.pse_float_value))
        if len(self.srv.devices) > 0:
            if len(self.srv.devices[0].inputs) > 0:
                for i in range(len(self.indicators)):
                    self.loggers[i].logValue(self.srv.devices[0].inputs[i+3])

        # stdout read to form
        tmp = sys.stdout.getvalue()
        if len(tmp) > 0:
            textCursor = self.plainTextEdit_consol.textCursor()
            textCursor.movePosition(QTextCursor.End, QTextCursor.MoveAnchor, 1)
            self.plainTextEdit_consol.setTextCursor(textCursor)
            self.plainTextEdit_consol.textCursor().insertText(tmp)
            self.plainTextEdit_consol.verticalScrollBar().setValue(
                self.plainTextEdit_consol.verticalScrollBar().maximum()
            )
            sys.stdout = io.StringIO("", newline=None)

    # production sensor
    def prodseninit(self):

        self.lineEdit_EmuPort.setText("/dev/ttyUSB0")
        self.lineEdit_EmuSpeed.setText("38400")

        def pse_con_lstn():
            try:
                spd = int(self.lineEdit_EmuSpeed.text())
            except ValueError:
                return
            self.timer3 = None
            self.pse = ProdSensEmu.ProdSensEmu(self.lineEdit_EmuPort.text(), spd)
            self.lineEdit_EmuOut.returnPressed.connect(lambda: self.pse.logger.show())


            if self.pse.port is None: return
            self.timer3 = QTimer()
            self.timer3.timeout.connect(lambda: self.pse.start())
            self.timer3.start(5)

        pse_con_lstn()
        self.pushButton_EmuPortOpen.clicked.connect(pse_con_lstn)

    # Определяем пользовательский слот
    def btn_connect_push(self):
        self.tableWidget.setRowCount(0)
        self.cmd_list.append("connect /dev/ttyACM0 9600 1")
        self.cmd_list.append("read 0 * 3")
        self.cmd_list.append("read 0 * 4")
        return None

    def slot_slider_moved(self):
        if len(self.srv.devices) == 0: return
        value = int(self.horizontalSlider.value()*self.srv.devices[0].holdings[5]/self.horizontalSlider.maximum())
        self.tableWidget.cellWidget(3, 1).setText(str(value))
        self.marking_cell(3)
        req = "write 0 3 " + str(value)
        self.lineEdit_freqref.setText(str(value/10).replace(".", ","))
        self.cmd_list.append(req)
        pass

    def slot_slider_changed(self):
        if len(self.cmd_list) > 1: return
        if len(self.srv.devices) == 0: return
        value = int(self.horizontalSlider.value()*self.srv.devices[0].holdings[5]/self.horizontalSlider.maximum())
        req = "write 0 3 " + str(value)
        self.cmd_list.append(req)
        self.marking_cell(3)
        self.tableWidget.cellWidget(3, 1).setText(str(value))
        self.lineEdit_freqref.setText(str(value/10).replace(".", ","))

    def slot_lineedit_freref_pressed(self):
        if len(self.srv.devices) == 0: return
        try:
            tmp = self.lineEdit_freqref.text()
            if ',' in tmp:
                tmp = tmp.replace(',', '.')
               # self.lineEdit_freqref.setText(tmp)
            tmp = float(tmp)
        except ValueError as e:
            self.lineEdit_freqref.clear()
        else:
            if self.srv.devices[0].holdings[5] > 0:
                tmp = self.horizontalSlider.maximum() * 10 * tmp/self.srv.devices[0].holdings[5]
            else: tmp = 0
            self.horizontalSlider.setValue(tmp)
            self.slot_slider_moved()

    def slot_lineedit_freqref_changed(self):
        pass


    def check_holding_table(self):
        if (len(self.cmd_list) == 0) & (len(self.ylwcells) > 0):
            formatter = ""
            for i in range(self.tableWidget.rowCount()):
                tmp2 = int(self.tableWidget.cellWidget(i, 1).text())
                if tmp2 != self.srv.devices[0].holdings[i]:
                    formatter = "QLineEdit {background-color: Red;}"
                    print("Warning: \n"
                          "Cell wrong value adr=", i, " cell=", tmp2, " dev=", self.srv.devices[0].holdings[i])
                    self.tableWidget.cellWidget(i, 1).setText(str(self.srv.devices[0].holdings[i]))
                else:
                    if i in self.ylwcells:
                        formatter = "QLineEdit {background-color: LightGreen;}"
                    else:
                        formatter = "QLineEdit {background-color: White;}"
                self.tableWidget.cellWidget(i, 1).setStyleSheet(formatter)
            self.ylwcells.clear()

    def marking_cell(self, row):
        ##
        # Marking holding table cells tobe checked
        # ##
        self.tableWidget.cellWidget(row, 1).setStyleSheet("QLineEdit {background-color: yellow;}")
        self.ylwcells.append(row)

    def slot_qtable_contmenu(self):
        menu = QMenu()
        act_load_from_dev = menu.addAction("Обновить в программе")
        act_load_from_dev.triggered.connect(self.slot_act_load_form_dev)
        # act_load_to_dev = menu.addAction("Обновить на устройстве")
        act_save_to_dev = menu.addAction("Сохранить в память МПЧ")
        act_save_to_dev.triggered.connect(lambda: self.cmd_list.append("write 0 0 8"))
        # act_save_to_file = menu.addAction("Сохранить в файл")
        # act_load_from_flash = menu.addAction("Загрузить из памяти МПЧ")
        # act_load_from_default = menu.addAction("Сброс к заводским установкам")
        menu.exec(QCursor.pos())

    def slot_act_load_form_dev(self):
        # self.tableWidget.clear()
        # self.tableWidget.setRowCount(0)
        self.cmd_list.append("read 0 * 3")
        self.ylwcells.append(0)

    def widget_init(self):
        # holding table refresh
        if self.tableWidget.rowCount() != len(self.srv.devices[0].holdings):
            # print device information
            print("holdings count=", len(self.srv.devices[0].holdings))
            print("inputs count=", len(self.srv.devices[0].inputs))
            # reading data from prm.json file
            with open('PRM.json', 'r', encoding='Windows-1251') as fh:  # открываем файл на чтение
                self.jsdtr = json.load(fh)  # загружаем из файла данные в словарь data
            # set table row value
            self.tableWidget.setRowCount(len(self.srv.devices[0].holdings))
            for x in range(0, len(self.srv.devices[0].holdings)):
                if x < len(self.jsdtr):
                    # writing parameter name from prm.json data to column 0, 2
                    item = QTableWidgetItem(self.jsdtr[x][0])
                    # disabling column 0 item changing
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.tableWidget.setItem(x, 0, item)
                    # additional combobox and button control at column 2 and 3
                    if len(self.jsdtr[x]) > 1:
                        tbtn = QPushButton()
                        tbtn.setMaximumSize(100, 75)
                        tbtn.setText("Задать")
                        self.tableWidget.setCellWidget(x, 3, tbtn)
                        self.tableWidget.setCellWidget(x, 2, QComboBox())
                        for item in self.jsdtr[x][1]:
                            # adding item at combobox
                            self.tableWidget.cellWidget(x, 2).addItem(item[0])
                            # Switch combobox to current value
                            if self.srv.devices[0].holdings[x] < self.tableWidget.cellWidget(x, 2).count():
                                self.tableWidget.cellWidget(x, 2).setCurrentIndex(self.srv.devices[0].holdings[x])
                            else:
                                self.tableWidget.cellWidget(x, 2).setCurrentIndex(-1)

                            # Combobox index changing event
                            def item_indCng():
                                try:
                                    # combobox current index
                                    tmp = self.tableWidget.cellWidget(self.tableWidget.currentRow(), 2).currentIndex()
                                    if tmp == -1: return
                                    # holding cell value
                                    tmp2 = int(self.tableWidget.cellWidget(self.tableWidget.currentRow(), 1).text())
                                    if tmp != tmp2:
                                        # cell value changing
                                        self.tableWidget.cellWidget(self.tableWidget.currentRow(), 1).setText(str(tmp))
                                        # marking cell
                                        self.marking_cell(self.tableWidget.currentRow())
                                        # request for server to write value
                                        if len(self.jsdtr[self.tableWidget.currentRow()]) > 1:
                                            if len(self.jsdtr[self.tableWidget.currentRow()][1][tmp]) == 2:
                                                # get cell value from json structure
                                                tmp = self.jsdtr[self.tableWidget.currentRow()][1][tmp][1]
                                        req = "write 0 " + str(self.tableWidget.currentRow()) + " " + str(tmp)
                                        self.cmd_list.append(req)
                                except AttributeError:
                                    pass

                            # connecting event to combobox
                            # self.tableWidget.cellWidget(x, 2).currentIndexChanged.connect(item_indCng)
                            # connecting event to button
                            self.tableWidget.cellWidget(x, 3).clicked.connect(item_indCng)
                    # if no additional combobox
                    else:
                        # disabling cell changing at column 2
                        item = QTableWidgetItem("")
                        item.setFlags(QtCore.Qt.ItemIsEnabled)
                        self.tableWidget.setItem(x, 2, item)
                # if no data at prm.json
                else:
                    # disabling cell changing at column 0,2
                    item = QTableWidgetItem("")
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    # self.tableWidget.setItem(x, 2, item)
                    self.tableWidget.setItem(x, 0, item)
                # Set cell value at column 1
                item = QLineEdit(str(self.srv.devices[0].holdings[x]))
                item.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
                item.setMaximumSize(75, 75)
                # Only int numbers
                item.setValidator(QIntValidator(-65536, 65536))

                # Cell value changing event
                def cell_pressed():
                    try:
                        # cell current value
                        tmp = int(self.tableWidget.cellWidget(self.tableWidget.currentRow(), 1).text())
                        # check for combobox item count
                        if tmp > self.tableWidget.cellWidget(self.tableWidget.currentRow(), 2).count(): tmp = -1
                        # changing combobox index
                        self.tableWidget.cellWidget(self.tableWidget.currentRow(), 2).setCurrentIndex(tmp)
                    except (ValueError, AttributeError) as e:
                        print(e)
                    # marking cell
                    self.marking_cell(self.tableWidget.currentRow())
                    # request for holding register changing
                    req = "write 0 " + str(self.tableWidget.currentRow()) + " " + \
                          self.tableWidget.cellWidget(self.tableWidget.currentRow(), 1).text()
                    self.cmd_list.append(req)

                def cell_changed():
                    try:
                        self.tableWidget.cellWidget(self.tableWidget.currentRow(), 1).setStyleSheet(
                            "QLineEdit {background-color: Pink;}"
                        )
                    except AttributeError:
                        pass

                # connecting event to QLineEdit
                item.returnPressed.connect(cell_pressed)
                item.textChanged.connect(cell_changed)
                self.tableWidget.setCellWidget(x, 1, item)
            # self.tableWidget.setColumnWidth(1,50)
            self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
