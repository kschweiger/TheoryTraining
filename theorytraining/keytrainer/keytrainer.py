import sys

import time
import logging
import itertools
import random

from PySide6.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout, QLineEdit, QLabel, QComboBox
from PySide6.QtCore import QTimer
class KeyTrainer(QWidget):

    def __init__(self, parent=None):
        super(KeyTrainer, self).__init__(parent)

        self.bpm = 100
        self.sig = (4, 4)

        self.step = 0
        
        self.bpm_dialog = QLineEdit("100")
        self.signature_upper_dialog = QLineEdit("4")
        self.signature_lower_dialog = QLineEdit("4")

        self.current_key_text = "C"

        self.keys = ["C","C#/Db","D","D#/Eb","E","F","F#/Gb","G","G#/Ab","A","A#/Bb","B"]
        self.theseKeys = self.keys
        self.set_order(0)
        
        self.isRunning = False
         
        self.button_set_bpm = QPushButton("Set")
        self.button_set_bpm.clicked.connect(self.setTempo)
        
        self.button_set_signature = QPushButton("Set")
        self.button_set_signature.clicked.connect(self.setSignature)
        
        self.button_start = QPushButton("Start")
        self.button_start.clicked.connect(self.start)
        self.button_start.setEnabled(True)
        
        self.button_stop = QPushButton("Stop")
        self.button_stop.clicked.connect(self.stop)
        self.button_stop.setEnabled(False)
        
        self.order_type_dropdown = QComboBox()
        self.order_type_dropdown.addItems(["Circle of 4th","Circle of 5th", "Random"])
        self.order_type_dropdown.currentIndexChanged.connect( self.set_order )
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        
        self.current_key = QLabel(self.current_key_text)
        
        content_layout = QVBoxLayout()
        
        content_layout.addWidget(self.bpm_dialog)
        content_layout.addWidget(self.button_set_bpm)
        
        content_layout.addWidget(self.signature_upper_dialog)
        content_layout.addWidget(self.signature_lower_dialog)
        content_layout.addWidget(self.button_set_signature)
        
        content_layout.addWidget(self.button_start)
        content_layout.addWidget(self.button_stop)
        
        content_layout.addWidget(self.current_key)
        
        content_layout.addWidget(self.order_type_dropdown)
        
        self.setLayout(content_layout)
        
         
    def setTempo(self):
        logging.info("Setting BPM to %s", self.bpm_dialog.text())
        
        self.bpm = int(self.bpm_dialog.text())

    def setSignature(self):
        logging.info("Setting time signature to %s / %s",
                     self.signature_upper_dialog.text(),
                     self.signature_lower_dialog.text())
        self.sig = (int(self.signature_upper_dialog.text()), int(self.signature_lower_dialog.text()))

    def set_order(self, i):
        """
        Sets to order of the keys that will be looped over. 
        """
        if i == 0:
            logging.debug("Setting order to circle of 4th")
            self.theseKeys = ["C","F","Bb","Eb","Ab","Db","Gb/F#","B","E","A","D","G"]
        elif i == 1:
            logging.debug("Setting order to circle of 5th")
            self.theseKeys = ["C","G","D","A","E","B","Gb/F#","Db","Ab","Eb","Bb","F"]
        else:
            logging.debug("Setting random order")
            random.shuffle(self.theseKeys)
        logging.debug("Set of keys: %s", self.theseKeys)
            
    def stop(self):
        logging.info("Stopping loop")
        self.timer.stop()
        self.button_start.setEnabled(True)
        self.button_stop.setEnabled(False)
        self.button_set_signature.setEnabled(True)
        self.button_set_bpm.setEnabled(True)
        self.order_type_dropdown.setEnabled(True)

        # Reset steps
        self.step = 0
        
    def start(self):
        logging.info("Starting training")
        self.cycleKeys = itertools.cycle(self.theseKeys)
        hold_time = (60000/self.bpm)
        logging.debug("BPM: %s -> Hold time: %s ms", self.bpm, hold_time)
        self.timer.start(hold_time)
        self.button_start.setEnabled(False)
        self.button_stop.setEnabled(True)
        self.button_set_signature.setEnabled(False)
        self.button_set_bpm.setEnabled(False)
        self.order_type_dropdown.setEnabled(False)
        
    def update(self):
        if self.step == self.sig[0]:
            self.step = 0
        logging.debug("Step %s", self.step)
        
        if self.step == 0:
            currentKey = next(self.cycleKeys)
            logging.debug("Current key: %s", currentKey)
            self.current_key.setText(currentKey)

        self.step += 1
        
if __name__ == "__main__":
    logging.basicConfig( encoding='utf-8', level=logging.DEBUG)
    logging.info("Starting application")
    
    app = QApplication(sys.argv)
    trainer = KeyTrainer()
    trainer.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
