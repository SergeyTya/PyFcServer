'''
Created on 28 нояб. 2019 г.

@author: sergey
'''
import io

import minimalmodbus
import serial
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIntValidator, QCursor
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QComboBox, QLineEdit, QMenu, QHeaderView
import json

from qtconsole.qt import QtCore, QtGui

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
        self.indicators = []
        self.ylwcells = []
        self.out_tmp = sys.stdout
        sys.stdout = io.StringIO("", newline=None)
        print("aefwsgr")

    def proc(self):
        self.check_holding_table()
            # First int
        if len(self.srv.devices) > 0: self.widget_init()

            # input indicators refresh
            # if len(self.srv.devices[0].inputs) >= len(self.indicators):
            #     for i in range(len(self.indicators)-1):
            #         self.indicators[i].display(self.srv.devices[0].inputs[i+3])

        #stdout read to form
        self.plainTextEdit_consol.textCursor().insertText(sys.stdout.getvalue())
        sys.stdout = io.StringIO("", newline=None)

    # Определяем пользовательский слот
    def btn_connect_push(self):
        self.tableWidget.setRowCount(0)
        self.cmd_list.append("connect /dev/ttyACM0 38400 1")
        self.cmd_list.append("read 0 * 3")
        self.cmd_list.append("read 0 * 4")
        return None

    def slot_slider_moved(self):
        req = "write 0 3 " + str(self.horizontalSlider.value())
        #self.lcd_freqref.display(self.horizontalSlider.value())
        self.cmd_list.append(req)
        pass

    def check_holding_table(self):
        if len(self.ylwcells) > 0:
            formatter = ""
            for i in range(self.tableWidget.rowCount()):
                tmp2 = int(self.tableWidget.cellWidget(i, 1).text())
                if tmp2 != self.srv.devices[0].holdings[i]:
                    formatter="QLineEdit {background-color: Red;}"
                    print("Warning: \n"
                          "Cell wrong value adr=", i, " cell=", tmp2, " dev=", self.srv.devices[0].holdings[i])
                    self.tableWidget.cellWidget(i, 1).setText(str(self.srv.devices[0].holdings[i]))
                else:
                    if i in self.ylwcells:
                        formatter="QLineEdit {background-color: LightGreen;}"
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
        act_save_to_dev.triggered.connect(lambda:  self.cmd_list.append("write 0 0 8"))
        # act_save_to_file = menu.addAction("Сохранить в файл")
        # act_load_from_flash = menu.addAction("Загрузить из памяти МПЧ")
        # act_load_from_default = menu.addAction("Сброс к заводским установкам")
        menu.exec(QCursor.pos())

    def slot_act_load_form_dev(self):
        #self.tableWidget.clear()
        #self.tableWidget.setRowCount(0)
        self.cmd_list.append("read 0 * 3")
        self.ylwcells.append(0)

    def widget_init(self):
        # holding table refresh
        if self.tableWidget.rowCount() != len(self.srv.devices[0].holdings):
            self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            # print device information
            print("holdings count=", len(self.srv.devices[0].holdings))
            print("inputs count=", len(self.srv.devices[0].inputs))
            # reading data from prm.json file
            with open('PRM.json', 'r', encoding='Windows-1251') as fh:  # открываем файл на чтение
                jsdtr = json.load(fh)  # загружаем из файла данные в словарь data
            # set table row value
            self.tableWidget.setRowCount(len(self.srv.devices[0].holdings))
            for x in range(0, len(self.srv.devices[0].holdings)):
                if x < len(jsdtr):
                    # writing parameter name from prm.json data to column 0, 2
                    item = QTableWidgetItem(jsdtr[x][0])
                    # disabling column 0 item changing
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    self.tableWidget.setItem(x, 0, item)
                    # additional combobox control at column 2
                    if len(jsdtr[x]) > 1:
                        self.tableWidget.setCellWidget(x, 2, QComboBox())
                        for item in jsdtr[x][1]:
                            # adding item at combobox
                            self.tableWidget.cellWidget(x, 2).addItem(item)
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
                                        req = "write 0 " + str(self.tableWidget.currentRow()) + " " + \
                                              self.tableWidget.cellWidget(self.tableWidget.currentRow(), 1).text()
                                        self.cmd_list.append(req)
                                except AttributeError: pass

                            # connecting event to combobox
                            self.tableWidget.cellWidget(x, 2).currentIndexChanged.connect(item_indCng)
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
                    self.tableWidget.setItem(x, 2, item)
                    self.tableWidget.setItem(x, 1, item)
                # Set cell value at column 1
                item = QLineEdit(str(self.srv.devices[0].holdings[x]))
                # Only int numbers
                item.setValidator(QIntValidator(-10000, 10000))

                # Cell value changing event
                def cell_pressed():
                    try:
                        # cell current value
                        tmp = int(self.tableWidget.cellWidget(self.tableWidget.currentRow(), 1).text())
                        # check for combobox item count
                        if tmp > self.tableWidget.cellWidget(self.tableWidget.currentRow(), 2).count(): tmp = -1
                        # changing combobox index
                        self.tableWidget.cellWidget(self.tableWidget.currentRow(), 2).setCurrentIndex(tmp)
                    except (ValueError, AttributeError): pass
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
                    except AttributeError: pass

                # connecting event to QLineEdit
                item.returnPressed.connect(cell_pressed)
                item.textChanged.connect(cell_changed)
                self.tableWidget.setCellWidget(x, 1, item)
                self.tableWidget.setColumnWidth(1,50)
