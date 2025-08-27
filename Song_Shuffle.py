import os, sys
import pygame
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QSlider, QListWidget, QLabel, QAbstractItemView, QFileDialog
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtCore import QSize, Qt, QTimer
from mutagen.mp3 import MP3

base_path = 'C:/CS/Python Projects/MP3 Player'

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP3 Player")
        self.setGeometry(0, 0, 500, 650)
        self.setWindowIcon(QIcon(os.path.join(base_path, "logo.png")))

        # Play/Pause button
        self.play = True
        self.playBttn = QPushButton(self) # Self so child moves with parent
        self.playBttn.setIcon(QIcon(os.path.join(base_path, "pause.png")))
        self.playBttn.setIconSize(QSize(64, 64))
        self.playBttn.setFixedSize(64, 64)
        self.playBttn.setGeometry(225, 500, 60, 60)

        self.playBttn.clicked.connect(self.playOnClick)

        # Next button
        self.ffBttn = QPushButton(self)
        self.ffBttn.setIcon(QIcon(os.path.join(base_path, "ff.png")))
        self.ffBttn.setIconSize(QSize(64, 64))
        self.ffBttn.setFixedSize(QSize(36, 36))
        self.ffBttn.setGeometry(300, 510, 60, 60)
        self.ffBttn.clicked.connect(self.nextSong)

        # Prev button
        self.fbBttn = QPushButton(self)
        self.fbBttn.setIcon(QIcon(os.path.join(base_path, "fb.png")))
        self.fbBttn.setIconSize(QSize(64, 64))
        self.fbBttn.setFixedSize(QSize(36, 36))
        self.fbBttn.setGeometry(177, 510, 60, 60)
        self.fbBttn.clicked.connect(self.prevSong)

        # Video Slider
        self.progressSlider = QSlider(Qt.Horizontal, self)
        self.progressSlider.setGeometry(50, 475, 400, 20)
        self.progressSlider.sliderReleased.connect(self.sliderSeek)

        # Song List
        self.idx = 0
        self.prev = -1
        self.prevAct = False
        self.song_path = 'C:/Users/edber/Videos/Gereja/Songs'
        self.songList = os.listdir(self.song_path)
        # self.songStart to make sure the slider handle doesn't go back to position 0:00 when dragged and place slider handle 
        # at 0 when moving to different songs
        self.songStart = 0
        self.listWidget = QListWidget(self)
        self.listWidget.setGeometry(50, 50, 400, 300)
        self.listWidget.itemClicked.connect(self.handleClick)

        self.listWidget.setDragDropMode(QAbstractItemView.InternalMove)
        self.listWidget.setDefaultDropAction(Qt.MoveAction)
        self.listWidget.setDragEnabled(True)
        self.listWidget.setAcceptDrops(True)
        self.listWidget.setDropIndicatorShown(True)
        self.listWidget.model().rowsMoved.connect(self.onRowsMoved) # Keep track of song idx when current song is dragged-and-dropped
        #self.listWidget.setDragDropMode(QAbstractItemView.InternalMove)

        # Volume Button
        self.prevVolume = 0
        self.muted = False
        self.volumeBttn = QPushButton(self)
        self.volumeBttn.setIcon(QIcon(os.path.join(base_path, "volume_on.png")))
        self.volumeBttn.setIconSize(QSize(36, 36))
        self.volumeBttn.setFixedSize(36, 36) # Make button smaller
        self.volumeBttn.setGeometry(51, 435, 60, 60)
        self.volumeBttn.clicked.connect(self.toggleMute)

        self.repeat = False
        self.rptBttn = QPushButton(self)
        self.rptBttn.setIcon(QIcon(os.path.join(base_path, "repeat.png")))
        self.rptBttn.setIconSize(QSize(36, 36))
        self.rptBttn.setFixedSize(36, 36) # Make button smaller
        self.rptBttn.setGeometry(415, 435, 60, 60)
        self.rptBttn.clicked.connect(self.repeatMode)

        # Volume Slider
        self.volumeSlider = QSlider(Qt.Horizontal, self)
        self.volumeSlider.setGeometry(100, 445, 150, 20)  # adjust position
        self.volumeSlider.setMinimum(0)
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setValue(100)  # start at full volume
        self.volumeSlider.valueChanged.connect(self.setVolume)

        # Folder Button
        self.folderBttn = QPushButton(self)
        self.folderBttn.clicked.connect(self.open_folder)
        self.folderBttn.setGeometry(370, 435, 60, 60)
        self.folderBttn.setIcon(QIcon(os.path.join(base_path, "folder.png")))
        self.folderBttn.setIconSize(QSize(36, 36))
        self.folderBttn.setFixedSize(36, 36)

        self.startTimeLabel = QLabel("00:00", self)
        self.startTimeLabel.setGeometry(50, 500, 100, 20)

        self.endTimeLabel = QLabel("00:00", self)
        self.endTimeLabel.setGeometry(425, 500, 150, 20)
        
        # CSS styling
        self.initUI()

        # Insert songs
        self.start()

        # Check if song has ended
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # check every second
        self.timer.timeout.connect(self.checkSongEnd)
        self.timer.timeout.connect(self.updateSlider)
        self.timer.start()

        # Duration of video
        self.duration = 0

    def initUI(self):
        self.playBttn.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 30px;  /* half of width/height */
                background-color: #ffffff;
            }
            QPushButton:hover {
                background-color: #e03a38;
            }
        """)

        self.rptBttn.setStyleSheet("""
            QPushButton {
                border-radius: 5px;
                background-color: white;  /* initial color */
                border-style: solid;
                border-color: black;
                border-width: 1px;
            }
        """)

        self.folderBttn.setStyleSheet("""
            QPushButton {
                border-radius: 5px;
                background-color: white;  /* initial color */
                border-style: solid;
                border-color: black;
                border-width: 1px;
            }
        """)


        self.progressSlider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                border-radius: 5px;                  
                height: 10px;               
            }                              
            
            QSlider::handle:horizontal {
                background-color: #fff; 
                width: 10px;
                margin: -1px -1px;    
                border-top-right-radius: 5px; 
                border-bottom-right-radius: 5px; 
                border: 1px solid #e03a38;                                             
            }
                                          
            QSlider::handle:horizontal:hover {
                background: #000;
                border-color: #000;                   
            }
                                          
            QSlider::sub-page:horizontal {
                background: #e03a38;
                border-radius: 5px;
            }

        """)

        self.ffBttn.setStyleSheet("""
            border: none;
        """)

        self.fbBttn.setStyleSheet("""
            border: none;
        """)

        self.volumeBttn.setStyleSheet("""
            border: none;
        """)

        self.volumeSlider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 10px;               
            }                              
            
            QSlider::handle:horizontal {
                background-color: #fff; 
                width: 10px;
                margin: -1px -1px;    
                border: 1px solid #e03a38;                                             
            }
                                          
            QSlider::handle:horizontal:hover {
                background: #000;
                border-color: #000;                   
            }
                                          
            QSlider::sub-page:horizontal {
                background: #e03a38;
            }

        """)

    def setVolume(self):
        volume = self.volumeSlider.value() / 100
        pygame.mixer.music.set_volume(volume) # Accepts value of 0.0 - 1.0

    def toggleMute(self):
        if self.muted == False:
            self.prevVolume = self.volumeSlider.value()/100
            pygame.mixer.music.set_volume(0)
            self.volumeSlider.setValue(0)
            #print(self.volume)
            self.volumeBttn.setIcon(QIcon(os.path.join(base_path, "volume_mute.png")))
            self.muted = True
        else:
            pygame.mixer.music.set_volume(self.prevVolume)
            self.volumeSlider.setValue(int(self.prevVolume*100))
            self.volumeBttn.setIcon(QIcon(os.path.join(base_path, "volume_on.png")))
            self.muted = False
    
    def playOnClick(self):
        #sprint(self.songList[self.idx])
        if self.play == True:
            self.playBttn.setIcon(QIcon(os.path.join(base_path, "play.png")))
            self.play = False
            pygame.mixer.music.pause()
        else:
            self.playBttn.setIcon(QIcon(os.path.join(base_path, "pause.png")))
            self.play = True
            pygame.mixer.music.unpause()

    def repeatMode(self):
        self.repeat = not self.repeat
        color = "#e03a38" if self.repeat else "white"
        self.rptBttn.setStyleSheet(f"""
            QPushButton {{
                border-radius: 5px;
                background-color: {color};
                border-style: solid;
                border-color: black;
                border-width: 1px;
            }}
        """)
    
    def nextSong(self):
        self.songStart = 0
        self.prev = self.idx
        pygame.mixer.music.stop()
        self.play = True
        self.repeat = False
        self.rptBttn.setStyleSheet(f"""
            QPushButton {{
                border-radius: 5px;
                background-color: white;
                border-style: solid;
                border-color: black;
                border-width: 1px;
            }}
        """)

    def prevSong(self):
        self.songStart = 0
        pygame.mixer.music.stop()
        self.prev = self.idx
        self.prevAct = True
        self.idx -= 2
        self.play = True
        self.repeat = False
        self.rptBttn.setStyleSheet(f"""
            QPushButton {{
                border-radius: 5px;
                background-color: white;
                border-style: solid;
                border-color: black;
                border-width: 1px;
            }}
        """)

    def shuffle(self):
        random.shuffle(self.songList)
        for song in self.songList:
            self.listWidget.addItem(song[0:-4]) # remove '.mp3' from the stsring
    
    def get_duration(self, file_path):
        audio = MP3(file_path)
        return audio.info.length
    
    def onRowsMoved(self, parent, start, end, destination, row):
    # Update the playlist after a drag/drop
        moved_item = self.songList[self.idx]

        # Rebuild the list after reordering
        self.songList = [self.listWidget.item(i).text() + ".mp3" for i in range(self.listWidget.count())]

        # Update self.idx to match the new position of the currently playing song
        for i in range(len(self.songList)):
            if self.songList[i] == moved_item:
                self.idx = i
                break
    
    # Move slider as the song plays
    def updateSlider(self):
        pos = pygame.mixer.music.get_pos() / 1000 # / 1000 to change it from miliseconds to seconds
        self.progressSlider.setValue(int(self.songStart + pos)) # Move slider handle accordingly
        mins = int(self.songStart + pos) // 60
        secs = int(self.songStart + pos) % 60
        self.startTimeLabel.setText(f"{mins:02}:{secs:02}")

    # Allow the user to drag the handle and jump to any part of the song
    def sliderSeek(self):
        self.songStart = self.progressSlider.value() # Keep track of actual progress
        pygame.mixer.music.play(start=self.songStart) # Play part of song where user jumped to using handle

    def handleClick(self, item):
        if self.listWidget.row(item) == self.idx:
            return
        pygame.mixer.music.stop()
        song = f"{item.text()}.mp3"
        full_path = os.path.join(self.song_path, song)
        #print(full_path)
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play()
        
        self.playBttn.setIcon(QIcon(os.path.join(base_path, "pause.png")))

        self.duration = self.get_duration(full_path)
        self.progressSlider.setMaximum(int(self.duration))

        mins = int(self.duration) // 60
        secs = int(self.duration) % 60
        self.endTimeLabel.setText(f"{mins:02}:{secs:02}")
        
        self.repeat = False
        self.songStart = 0
        self.play = True
        self.prev = self.idx
        self.idx = self.listWidget.row(item)
        self.highlightSong(self.idx, QColor("#e03a38"), Qt.white) 
        self.highlightSong(self.prev, QColor("#ffffff"), Qt.black)

    
    # Highlight selected song
    def highlightSong(self, index, bg, fg):
        item = self.listWidget.item(index)
        item.setBackground(bg)
        item.setForeground(fg)

    def start(self):
        self.shuffle()
        pygame.mixer.init()
        
        full_path = os.path.join(self.song_path, self.songList[self.idx])
        #print(full_path)
        pygame.mixer.music.load(full_path)

        # Reset timebase before playing
        self.songStart = 0
        pygame.mixer.music.play()
        self.duration = self.get_duration(full_path)

        self.progressSlider.setMaximum(int(self.duration))
        self.progressSlider.setValue(0)  # Reset progress slider to 0
        self.startTimeLabel.setText("00:00")
        mins = int(self.duration) // 60
        secs = int(self.duration) % 60
        self.endTimeLabel.setText(f"{mins:02}:{secs:02}")
        # Highlight which song is playing
        self.highlightSong(self.idx, QColor("#e03a38"), Qt.white)
    
    # Opening a folder
    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose music folder")
        if not folder: 
            return
        
        self.song_path = folder
        self.songList = os.listdir(self.song_path)
        self.listWidget.clear()
        self.idx = 0
        self.songStart = 0                      
        self.progressSlider.setValue(0)
        self.start()
    
    def checkSongEnd(self):
        if self.play and not pygame.mixer.music.get_busy():
            if self.prevAct:
                self.prevAct = False
            else:
                self.prev = self.idx
            if self.repeat:
                self.idx = self.prev
            else:
                self.idx += 1
            if self.idx == len(self.songList):
                self.idx = 0
            elif self.idx < 0:
                self.idx = len(self.songList) - 1
            self.songStart = 0
            full_path = os.path.join(self.song_path, self.songList[self.idx])
            pygame.mixer.music.load(full_path)
            pygame.mixer.music.play()
            self.duration = self.get_duration(full_path)
            self.progressSlider.setMaximum(int(self.duration))

            mins = int(self.duration) // 60
            secs = int(self.duration) % 60
            self.endTimeLabel.setText(f"{mins:02}:{secs:02}")
            # Highlight which song is playing
            if not self.repeat:
                self.highlightSong(self.idx, QColor("#e03a38"), Qt.white) 
                self.highlightSong(self.prev, QColor("#ffffff"), Qt.black)

            
def main():
    app = QApplication(sys.argv) # App or system ig?
    window = MainWindow() # Main Window
    window.show() # Show window (but only for a sec unless with line below)
    sys.exit(app.exec_()) # app.exec_() to keep app running, sys.exit() to know how program ended (0: program ended normally)

# For exporting files (I guess...)
if __name__ == "__main__":
    main()

