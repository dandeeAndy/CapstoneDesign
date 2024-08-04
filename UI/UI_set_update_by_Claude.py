import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime

selected_option = None
pause_clicked = None
option_reset = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.grid_layout = QGridLayout()
        central_widget = QWidget(self)
        central_widget.setLayout(self.grid_layout)
        self.setCentralWidget(central_widget)

        self.setupUI()
        self.setupButtons()
        self.setupLabels()
        
        self.setWindowTitle('Delta_System')
        self.showMaximized()
        
    def setupUI(self):
        # Set up logo, assembly image, etc.
        pass
    
    def setupButtons(self):
        self.option_buttons = [OptionButton(f'opt{i+1}_ON.png', f'opt{i+1}_OFF.png', f'Option{i+1}', self) for i in range(3)]
        button_positions = [(1, 10, 1, 4), (1, 14, 1, 3), (1, 17, 1, 4)]
        for i, option_button in enumerate(self.option_buttons):
            self.grid_layout.addWidget(option_button, *button_positions[i])

        self.pause_button_label = QLabel(self)
        pause_button_pixmap = QPixmap('pause_button.png').scaled(850, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.pause_button_label.setPixmap(pause_button_pixmap)
        self.pause_button_label.mousePressEvent = self.pauseClicked
        self.grid_layout.addWidget(self.pause_button_label, 2, 10, 1, 11)
    
    def setupLabels(self):
        # Set up all the labels and widgets
        pass
    
    def pauseClicked(self, event):
        global pause_clicked
        if pause_clicked is None:
            pause_clicked = "pause"
            QMessageBox.information(self, '알림', '작업이 중지되었습니다.')
            reply = QMessageBox.question(self, '확인', '분류기준을 초기화하시겠습니까?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.resetOptions()
                self.clearLists()
            pause_clicked = None
        else:
            QMessageBox.information(self, '알림', '이미 일시 중지 상태입니다.')
    
    def resetOptions(self):
        global option_reset, pause_clicked
        option_reset = "reset"
        pause_clicked = None
        for button in self.option_buttons:
            if button.is_on:
                button.is_on = False
                button.setScaledPixmap()
    
    def clearLists(self):
        # Clear all list widgets
        pass

class OptionButton(QWidget):
    optionSelected = pyqtSignal(str)
    def __init__(self, on_image_path, off_image_path, opt_text, parent=None):
        super().__init__(parent)
        self.on_pixmap = QPixmap(on_image_path)
        self.off_pixmap = QPixmap(off_image_path)
        self.opt_text = opt_text
        self.is_on = False
        
        self.label = QLabel(self)
        self.setFixedSize(300, 300)
        self.label.setFixedSize(280, 280)
        self.setScaledPixmap()
        
        self.transparent_button = QPushButton(self)
        self.transparent_button.setFlat(True)
        self.transparent_button.clicked.connect(self.button_clicked)
        self.transparent_button.setFixedSize(240, 135)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.transparent_button)
        self.setLayout(layout)
        
    def setScaledPixmap(self):
        pixmap = (self.on_pixmap if self.is_on else self.off_pixmap).scaled(self.label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.label.setPixmap(pixmap)
    
    def button_clicked(self):
        if not any(btn.is_on for btn in self.parent().children() if isinstance(btn, OptionButton) and btn is not self):
            self.toggle()
        else:
            QMessageBox.warning(self, '경고', '다른 옵션이 실행 중입니다.')
    
    def toggle(self):
        global selected_option, pause_clicked
        pause_clicked = None
        self.is_on = not self.is_on
        self.setScaledPixmap()
        if self.is_on:
            selected_option = self.opt_text
            self.optionSelected.emit(selected_option)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("NanumSquare", 9))
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())