import sys

import time
import logging
import itertools

from PySide6.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout, QLineEdit, QLabel

class KeyTrainer(QWidget):

    def __init__(self, parent=None):
         super(KeyTrainer, self).__init__(parent)

         self.bpm = 100
         self.sig = (4, 4)

         self.bpm_dialog = QLineEdit("100")
         self.signature_upper_dialog = QLineEdit("4")
         self.signature_lower_dialog = QLineEdit("4")

         self.current_key_text = "KEY"

         self.keys = ["A", "B", "C"]
         self.theseKeys = self.keys
         
         self.isRunning = False
         
         button_set_bpm = QPushButton("Set")
         button_set_bpm.clicked.connect(self.setTempo)

         button_set_signature = QPushButton("Set")
         button_set_signature.clicked.connect(self.setSignature)

         button_start = QPushButton("Start")
         button_start.clicked.connect(self.start)

         button_stop = QPushButton("Stop")
         button_stop.clicked.connect(self.stop)

         content_layout = QVBoxLayout()
         
         content_layout.addWidget(self.bpm_dialog)
         content_layout.addWidget(button_set_bpm)
         
         content_layout.addWidget(self.signature_upper_dialog)
         content_layout.addWidget(self.signature_lower_dialog)
         content_layout.addWidget(button_set_signature)

         content_layout.addWidget(button_start)
         content_layout.addWidget(button_stop)
         
         self.current_key = QLabel(self.current_key_text)

         content_layout.addWidget(self.current_key)
         
         self.setLayout(content_layout)
         
    def setTempo(self):
        logging.info("Setting BPM to %s", self.bpm_dialog.text())
        
        self.bpm = int(self.bpm_dialog.text())

    def setSignature(self):
        logging.info("Setting time signature to %s / %s",
                     self.signature_upper_dialog.text(),
                     self.signature_lower_dialog.text())
        self.sig = (int(self.signature_upper_dialog.text()), int(self.signature_lower_dialog.text()))

    def stop(self):
        logging.info("Stopping loop")
        self.isRunning = False
        
    def start(self):
        logging.info("Starting training")
        self.isRunning = True

        self.theseKeys = itertools.cycle(self.keys)
            
if __name__ == "__main__":
    logging.basicConfig( encoding='utf-8', level=logging.DEBUG)
    logging.info("Starting application")
    
    app = QApplication(sys.argv)
    trainer = KeyTrainer()
    trainer.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
