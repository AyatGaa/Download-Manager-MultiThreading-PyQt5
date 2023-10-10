import time
import urllib.request
from urllib.request import urlopen
import os
import sys
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#live sync nw ui and py files
from PyQt5.uic import loadUiType
from pytube import YouTube
from pytube import Playlist
import re

form_class, _ = loadUiType(os.path.join(os.path.dirname(__file__), 'mainPage.ui'))

class Download_worker_1(QThread):
    update_progress_1 = pyqtSignal(int)  # for current value
    success = pyqtSignal()

    def __init__(self, parent, url, loc):
        """Constructor"""
        QThread.__init__(self)
        self.url = url
        self.loc = loc
        self.parent = parent
        self.start() # to start thread while create object !

    def run(self):
        # filename = os.path.basename(self.url)
        loc = self.loc
        urllib.request.urlretrieve(self.url, loc, self.reportBock)
        self.success.emit()

    def reportBock(self, blockchunck, blocksize, totalsize):
        reads = blocksize * blockchunck
        if totalsize > 0:
            percent = int((reads / totalsize) * 100)
            self.update_progress_1.emit(percent)

class Download_worker_2(QThread):
    update_progress_2 = pyqtSignal(int)
    done = pyqtSignal()
    wrong = pyqtSignal()

    def __init__(self, parent, url, loc, quality):
        QThread.__init__(self)
        self.url = url
        self.parent = parent
        self.loc = loc
        self.quality = quality
        self.start()

    def run(self):
        loc = self.loc
        yt = YouTube(self.url, on_progress_callback=self.reportBook)
        st = yt.streams.filter(type="video", progressive=True, file_extension='mp4')
        try:
            st[self.quality].download(loc)
            self.done.emit()
        except Exception:
            self.wrong.emit()

    def reportBook(self, stream, chunk:bytes,  bytes_remaining:int):
        totalsize = stream.filesize
        bytes_ddown = totalsize - bytes_remaining
        if totalsize > 0:
            progress = (float(abs(bytes_remaining - totalsize) / totalsize)) * float(100)
            self.update_progress_2.emit(int(progress))


class Download_worker_3(QThread):
    update_progress_3 = pyqtSignal(int)
    done_2 = pyqtSignal()
    wrong_2 = pyqtSignal()
    whole_down_fin = pyqtSignal()
    remain_vid = pyqtSignal(int)

    def __init__(self, parent, palylist_url, loc, quality):
        QThread.__init__(self)
        self.palylist_url = palylist_url
        self.parent = parent
        self.loc = loc
        self.quality = quality
        self.start()


    def run(self):
        down_playlist = Playlist(self.palylist_url)
        pre = 1
        all_vid = int(len(down_playlist.video_urls))
        for video in down_playlist.videos:
            if self.quality == 2: # 2 == qulaity_low
                video.register_on_progress_callback(self.progress_function_pl)
                video.streams.filter(type="video", progressive=True, file_extension='mp4').get_lowest_resolution().download(
                    filename_prefix=pre, output_path=self.loc)
                self.done_2.emit()
                rem = all_vid-1
            else:
                video.register_on_progress_callback(self.progress_function_pl)
                video.streams.filter(type="video", progressive=True, file_extension='mp4').get_highest_resolution().download(
                    filename_prefix=pre, output_path=self.loc)
                self.done_2.emit()
                rem = all_vid - 1
            self.remain_vid.emit(rem)
            pre += 1
            all_vid -= 1
        self.whole_down_fin.emit()

    def progress_function_pl(self, stream, chunk: bytes, bytes_remaining: int):
        totalsize = stream.filesize
        progress = (float(abs(bytes_remaining - totalsize) / totalsize)) * float(100)
        self.update_progress_3.emit(int(progress))


# init ui file
class MainApp(QMainWindow, form_class):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.handel_ui()
        self.handel_Buttons()
        icon = QIcon()
        icon.addPixmap(QPixmap("download.png"), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)

    def handel_ui(self):
        self.setWindowTitle('Video Downloader')
        # self.setFixedSize(1045, 645)
        self.titleLabel_2.setHidden(True)
        self.titleLabel.setHidden(True)

    def handel_Buttons(self):
        # Handle File download Buttons
        self.download.clicked.connect(self.handel_Download)
        self.browse.clicked.connect(self.handel_Browse)

        # Handle Videos download Buttons
        self.download_2.clicked.connect(self.download_video)
        self.browse_2.clicked.connect(self.video_browse)
        self.submit.clicked.connect(self.get_video)

        # Handle Playlist download Buttons
        self.browse_3.clicked.connect(self.playlist_browse)
        self.download_3.clicked.connect(self.download_playtlist)
        self.submit_3.clicked.connect(self.get_playlist)

        # End prog
        self.cancel.clicked.connect(self.exit_btn_clicked)
        self.cancel_2.clicked.connect(self.exit_btn_clicked)
        self.cancel_3.clicked.connect(self.exit_btn_clicked)

    def exit_btn_clicked(self):
        self.sys.exit()

    def handel_Download(self):
        self.download.setEnabled(False)
        url = self.url.text()
        location = self.location.text()
        header = urlopen(url)
        fsize = int(header.headers['Content-Length'])
        # call thread
        self.Ddownloader_1 = Download_worker_1(self, url, location)
        time.sleep(1)
        self.Ddownloader_1.update_progress_1.connect(self.progUpdate)
        self.Ddownloader_1.success.connect(self.downloadFinished)

    def downloadFinished(self):
        self.download.setEnabled(True)
        QMessageBox.information(self, 'Download Completed !', 'Your Download Finished (❁´◡`❁)')
        del self.Ddownloader_1

    def progUpdate(self, val):
        self.progressBar.setValue(val)

    def handel_Browse(self):
        save_location = QFileDialog.getExistingDirectory(self, caption="Save As", directory=".")
        self.location.setText(save_location)


    def video_browse(self):
        save_path2,ext = QFileDialog.getSaveFileName(self, 'Save', '', '') #return file name and extension
        self.location_2.setText(save_path2)

    def playlist_browse(self):
        save_path3, ext = QFileDialog.getSaveFileName(self, "Save", '', '')
        self.location_3.setText(save_path3)


    def text_Lines_Validator(self, text, pos):
        if text == '':
            QMessageBox.warning(self, "URL Not Found ", "Please Enter Video URL !")
        return pos


    def youtube_url_validation(self, url):
        youtube_regex = (
            r'(https?://)?(www\.)?'
            '(youtube|youtu|youtube-nocookie)\.(com|be)/'
            '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        you_regex = ('^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube(-nocookie)'
                     '?\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|live\/|v\/)?)([\w\-]+)(\S+)?$')
        youtube_regex_match = re.match(you_regex, url)
        # print(youtube_regex_match)
        if youtube_regex_match:
            return youtube_regex_match
        return youtube_regex_match



    def is_Playlist(self, url):
        playlist_regex = ('[?&]list=([^#\&\?]+)')
        playlist_regex_match = re.search(playlist_regex, url)
        # print(playlist_regex_match)
        if playlist_regex_match:
            return playlist_regex_match
        return playlist_regex_match



    def get_video(self):
        video_link = self.url_2.text()
        if video_link == '':
            QMessageBox.warning(self, "URL Not Found ", "Please Enter Video URL !")
        else:
            check_url = self.youtube_url_validation(video_link)
            check_playlist = self.is_Playlist(video_link)

            if check_url and not check_playlist:
                yt = YouTube(video_link)
                st = yt.streams.filter(type="video", progressive=True, file_extension='mp4')
                for s in st:
                    data = 'Quality: {} | {} mb'.format(s.resolution, s.filesize_mb)
                    self.qualityBox.addItem(data)
                vid_title = yt.title
                self.video_browse()
                self.titleLabel.setHidden(False)
                self.titleLabel.setText(vid_title)
            else:
                QMessageBox.warning(self, "Invalid Video URL ", "Please Enter video URL !")



    def download_video(self):
        self.download_2.setEnabled(False)
        video_link = self.url_2.text()
        save_path = self.location_2.text()
        yt = YouTube(video_link)
        # st = yt.streams.filter(type="video", progressive=True, file_extension='mp4')
        choosed_Quality = self.qualityBox.currentIndex()
        quality = choosed_Quality

        self.downloader_2 = Download_worker_2(self, video_link, save_path, quality)
        time.sleep(1.5)
        self.downloader_2.update_progress_2.connect(self.update_pr_2)
        self.downloader_2.done.connect(self.downloadFinished_2)
        self.downloader_2.wrong.connect(self.downloadWrong)


    def downloadWrong(self):
        QMessageBox.warning(self, "Video Download failed !", 'Something went wrong!')

    def update_pr_2(self, val):
        self.progressBar_2.setValue(val)

    def downloadFinished_2(self):
        self.download_2.setEnabled(True)
        QMessageBox.information(self, 'Download Completed !', 'Your Download Finished (❁´◡`❁)')
        del self.downloader_2


    def get_playlist(self):
        playlist_url = self.url_3.text()
        if playlist_url == '':
            QMessageBox.warning(self, "URL Not Found ", "Please Enter Playlist URL !")
        else:
            check_url = self.youtube_url_validation(playlist_url)
            check_playlist = self.is_Playlist(playlist_url)
            if check_url and check_playlist:
                # save_path = self.location_3.text()
                down_playlist = Playlist(playlist_url)
                # print(len(down_playlist.video_urls))
                vid_title = down_playlist.title
                playlist_name = re.sub(r'\W+', '-', vid_title)
                # if not os.path.exists(playlist_name):
                #     os.mkdir(playlist_name)

                self.radioButton.toggled.connect(lambda: self.onClicked1_high(self.radioButton))
                self.radioButton_2.toggled.connect(lambda: self.onClicked2_low(self.radioButton_2))
                self.titleLabel_2.setHidden(False)
                self.titleLabel_2.setText("Playlist Title : "+vid_title)
                self.label.setText("Playlist videos : "+str(len(down_playlist.video_urls)) + " video")
            else:
                QMessageBox.warning(self, "Invalid URL ", "Please Enter Correct Playlist URL !")

    def onClicked1_high(self, b):
        if b.isChecked():
            q = 1
            return q

    def onClicked2_low(self, c):
        if c.isChecked():
            q = 2
            return q

    def download_playtlist(self):
        playlist_url = self.url_3.text()
        save_path = self.location_3.text()
        down_playlist = Playlist(playlist_url)
        quality_high = self.onClicked1_high(self.radioButton)
        quality_low = self.onClicked2_low(self.radioButton_2)
        print(" quality_high" , quality_high ,"|||" , "qq low", quality_low)

        if quality_high == 1:
            self.downloader_3 = Download_worker_3(self, playlist_url, save_path, quality_high)
            print("th 1")
        elif quality_low == 2:
            self.downloader_3 = Download_worker_3(self, playlist_url, save_path, quality_low)
            print("th 2")
        else:
            self.downloader_3 = Download_worker_3(self, playlist_url, save_path, quality_high)
            print("th 3")
        time.sleep(1)
        self.downloader_3.update_progress_3.connect(self.update_pr_3)
        self.downloader_3.done_2.connect(self.downloadFinished_3)
        self.downloader_3.wrong_2.connect(self.downloadWrong_3)
        self.downloader_3.whole_down_fin.connect(self.pl_down_done)
        self.downloader_3.remain_vid.connect(self.show_rem_vid)

    def show_rem_vid(self, v):
        self.label_10.setText("No.Remaining Video: " + str(v))

    def update_pr_3(self, val):
        self.progressBar_3.setValue(val)

    def downloadFinished_3(self):
        self.label_10.setText("Done!")

    def downloadWrong_3(self):
        QMessageBox.warning(self, "Download failed !", 'Something went wrong!')

    def pl_down_done(self):
        self.download_3.setEnabled(True)
        QMessageBox.information(self, 'Playlist Downloaded !', 'Your Download Finished ')
        del self.downloader_3

def main():
    app = QApplication(sys.argv)
    win = MainApp()
    win.show()
    app.exec_() # infinity loop

if __name__ == '__main__':
    main()