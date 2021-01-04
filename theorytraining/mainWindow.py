import logging
import sys

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

import resources

from keytrainer.keytrainer import KeyTrainer
from util.util import initLogging



class MainWindow(QMainWindow):
    """
    Main window of the application. Used as gateway to the other application.
    Each application has its own subfolder.
    """
    
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Theory Training")

        self.layout = QVBoxLayout()
        # Button for the sub applications

        # Keytrainer
        self.key_trainer_widget = KeyTrainer(setSounds=[":sounds/primary_ping.wav",":sounds/secondary_ping.wav"])
        self.button_key_trainer = QPushButton("Show/Hide Key Trainer")
        self.button_key_trainer.clicked.connect(self.toggle_key_trainer)
        self.setCentralWidget(self.button_key_trainer)
        self.layout.addWidget(self.button_key_trainer)
        
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.layout)
        self.setCentralWidget(self.mainWidget)
        
    def toggle_key_trainer(self):
        if self.key_trainer_widget.isVisible():
            logging.info("Showing Key trainer widget")
            self.key_trainer_widget.hide()
        else:
            logging.info("Hiding Key trainer widget")
            self.key_trainer_widget.show()


if __name__ == "__main__":
    initLogging(10, 20)
    logging.info("Creating main window")
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
