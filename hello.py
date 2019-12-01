"""
Основной скрипт программы.
Запускает конфигуратор окна, подключает слоты и отображает окно.
"""
# Импортируем системый модуль для корректного закрытия программы
import io
import sys
# Импортируем минимальный набор виджетов
from PyQt5.QtWidgets import QApplication, QWidget
# Импортируем созданный нами класс со слотами
from form_slots import MainWindowSlots
from PyQt5.QtCore import QTimer
import server as srv


# Создаём ещё один класс, наследуясь от класса со слотами
class MainWindow(MainWindowSlots):
    # При инициализации класса нам необходимо выпонить некоторые операции
    def __init__(self, form):
        # Сконфигурировать интерфейс методом из базового класса Ui_Form
        self.setupUi(form)
        # Подключить созданные нами слоты к виджетам
        self.connect_slots()
        self.srv = srv.Server()

    # Подключаем слоты к виджетам
    def connect_slots(self):
        self.pushButton.clicked.connect(self.set_time)
        return None

    def proc(self):
        out_tmp = sys.stdout
        sys.stdout = io.StringIO("", newline=None)

        try:
            if len(self.srv.masters) == 0:
                self.srv.main(inpt="connect * 9600 1")

        except srv.Server.ServerError as e:
            print(e)
        finally:
            self.plainTextEdit.textCursor().insertText(sys.stdout.getvalue())
            sys.stdout = out_tmp

if __name__ == '__main__':
    # Создаём экземпляр приложения
    app = QApplication(sys.argv)
    # Создаём базовое окно, в котором будет отображаться наш UI
    window = QWidget()
    # Создаём экземпляр нашего UI
    server = srv.Server()
    ui = MainWindow(window)
    ui.srv = server
    # сервер
    # timer
    timer = QTimer()
    timer.timeout.connect(ui.proc)
    timer.start(1000);
    # Отображаем окно
    window.show()
    # Обрабатываем нажатие на кнопку окна "Закрыть"
    sys.exit(app.exec_())
    
    
    
    