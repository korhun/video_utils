import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QLineEdit, QDialogButtonBox, QFormLayout, QApplication

if __name__ == '__main__' or __name__ == 'dialogs.download_video_dialog':
    from utils import file_helper
else:
    from labelme.video_player.utils import file_helper


class DownloadVideoDialog(QDialog):
    def __init__(self, parent_app, parent_window=None, default_font=None):
        super().__init__(parent=parent_window)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        translator = QtCore.QTranslator()
        qm_file = file_helper.path_join(current_dir, 'video_player-tr.qm')
        translator.load(qm_file)
        parent_app.installTranslator(translator)

        self.first = QLineEdit(self)
        self.second = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout = QFormLayout(self)
        layout.addRow("First text", self.first)
        layout.addRow("Second text", self.second)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return self.first.text(), self.second.text()


def show_download_video_dialog(parent_app, parent_window=None, default_font=None):
    dialog = DownloadVideoDialog(parent_app, parent_window, default_font)
    if dialog.exec():
        return dialog.getInputs()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    print(show_download_video_dialog(app))
    exit(0)
