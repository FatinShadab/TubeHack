import os
import random
import requests
import threading
from urllib.parse import urlparse

import youtube_dl

from PyQt5.QtWidgets import * 
from PyQt5 import uic, QtCore, QtWidgets


class QLogger(QtCore.QObject):
    messageChanged = QtCore.pyqtSignal(str)

    def debug(self, msg):
        self.messageChanged.emit(msg)

    def warning(self, msg):
        self.messageChanged.emit(msg)

    def error(self, msg):
        self.messageChanged.emit(msg)


class QHook(QtCore.QObject):
    infoChanged = QtCore.pyqtSignal(dict)

    def __call__(self, d):
        self.infoChanged.emit(d.copy())


class QYoutubeDL(QtCore.QObject):
    def download(self, urls, options):
        threading.Thread(
            target=self._execute, args=(urls, options), daemon=True
        ).start()

    def _execute(self, urls, options):
        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download(urls)
        for hook in options.get("progress_hooks", []):
            if isinstance(hook, QHook):
                hook.deleteLater()
        logger = options.get("logger")
        if isinstance(logger, QLogger):
            logger.deleteLater()


class TUBEHACK(QMainWindow):
    def __init__(self):
        super(TUBEHACK, self).__init__()
        uic.loadUi("tubehack.ui", self)
        self.downloader = QYoutubeDL()
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.status_label.setVisible(False)
        self.show()

        # buttons
        self.close_button.clicked.connect(lambda: self.shutDown())
        self.path_button.clicked.connect(lambda: self.getDownloadPath())
        self.dl_button.clicked.connect(lambda: self.download())

    def _active_net_con(self):
        try:
            _ = requests.head('http://www.google.com/', timeout=5)
            return True
        except requests.ConnectionError:
            return False

    def _is_vaild_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def _get_res(self):
        res = []

        if self.hd_720.isChecked():
            res.append(True)
            res.append('best')
        elif self.only_720.isChecked():
            res.append(True)
            res.append('best[height<=720]')
        elif self.low_480.isChecked():
            res.append(True)
            res.append('best[height<=480]')
        else:
            res.append(False)

        return res

    def _download(self, url, path, res):
        qhook = QHook()
        qlogger = QLogger()
        options = {
            "format": res,
            "noplaylist": True,
            'output': path,
            "noprogress": True,
            "logger": qlogger,
            "progress_hooks": [qhook],
        }
        self.downloader.download([url], options)
        qhook.infoChanged.connect(self.handle_info_changed)
        #qlogger.messageChanged.connect(self.log_edit.appendPlainText)

    def handle_info_changed(self, d):
        if d["status"] == "downloading":
            self.path_button.setEnabled(False)
            self.dl_button.setEnabled(False)
            self.status_label.setVisible(True)
            total = d["total_bytes"]
            downloaded = d["downloaded_bytes"]
            self.status_label.setText(f"Downloading .{'.'*random.choice((0, 1, 2))}")

        if d["status"] == "finished":
            self.status_label.setVisible(False)
            file_tuple = os.path.split(os.path.abspath(d['filename']))
            QMessageBox.information(self, 'TubeHack', f'{file_tuple[1]} Downloaded.', QMessageBox.Ok)
            self.video_url.clear()
            self.path.clear()
            self.hd_720.setChecked(False)
            self.only_720.setChecked(False)
            self.low_480.setChecked(False)
            self.path_button.setEnabled(True)
            self.dl_button.setEnabled(True)
            
    def shutDown(self):
        reply = QMessageBox.question(self, 'TubeHack', 'Are you sure you want to close the window?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.close()

    def getDownloadPath(self):
        path = QFileDialog.getExistingDirectory()
        self.path.setText(path)

    def download(self):
        if len(self.video_url.text()) > 0 and len(self.path.text()) > 0 and self._get_res()[0]:
            if self._is_vaild_url(self.video_url.text()):
                if os.path.isdir(self.path.text()):
                    if self._active_net_con():
                        self._download(self.video_url.text(), self.path.text(), self._get_res()[1])
                    else:
                        reply = QMessageBox.warning(self, 'TubeHack', f'No Internet Connection !', QMessageBox.Ok)
                else:
                    reply = QMessageBox.warning(self, 'TubeHack', f'Invalid PATH: {self.path.text()}!!', QMessageBox.Ok)
            else:
                reply = QMessageBox.warning(self, 'TubeHack', f'Invalid URL: {self.video_url.text()}!!', QMessageBox.Ok)
        else:
            reply = QMessageBox.information(self, 'TubeHack', 'Fill Up the filds first !!', QMessageBox.Ok)


def main():
    app = QApplication([])
    window = TUBEHACK()
    app.exec_()


if __name__ == "__main__":
    # https://www.youtube.com/watch?v=VVaP9JA3oho&list=PLe247iZvb63Jzvs2gkmu9Lrl9w9rEquSN&index=6
    # https://www.youtube.com/watch?v=X7jWB6NMB74
    main()