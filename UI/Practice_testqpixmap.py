import os

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.QtCore import Qt


class ThumbnailView(QMainWindow):

    def __init__(self):
        super().__init__()

        self.resize(1000, 500)
        self.main_img = QLabel()
        self.setCentralWidget(self.main_img)

        front_image = '123층_1.jpg'

        # Check gugu.jpg file
        if os.path.isfile(front_image):
            self.main_img.setPixmap(QPixmap(front_image).scaled(self.width(), self.height(), Qt.KeepAspectRatio))
        else:
            print('no file')


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = ThumbnailView()
    window.show()
    sys.exit(app.exec_())