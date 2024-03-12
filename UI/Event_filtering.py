from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QEvent, QObject

class EventFilter(QObject):
    def eventFilter(self, watched, event):
        if event.type() == QEvent.MouseButtonPress:
            print("Mouse pressed on", watched)
            return True  # 이벤트가 처리되었음을 나타냄
        return False

app = QApplication([])
widget = QWidget()
event_filter = EventFilter()
widget.installEventFilter(event_filter)  # 이벤트 필터 설치
widget.show()
app.exec_()
