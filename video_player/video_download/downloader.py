from PyQt5.QtCore import pyqtSignal, QObject


class Downloader(QObject):
    download_progress = pyqtSignal(float)
    download_finished = pyqtSignal(str)
    download_warning = pyqtSignal(str)
    download_error = pyqtSignal(str)

    def is_downloading(self):
        pass

    def stop_download(self):
        pass

    def start_download(self, url: str, file_name: str):
        pass

    def get_name(self, url):
        pass
