import sys

import logging
import itertools
import random

from PySide2.QtWidgets import QWidget, QApplication, QPushButton, QGridLayout, QLineEdit, QLabel, QComboBox
from PySide2.QtCore import QTimer, Qt
from PySide2.QtMultimedia import QSound


class KeyTrainer(QWidget):
    """
    Application intendent to train finding certain keys on the fretboard.
    """
    
    def __init__(self, parent=None, setSounds=None):
        super(KeyTrainer, self).__init__(parent)
        
        self.title = "Key Trainer"
        self.width = 200
        self.height = 400
        
        self.bpm = 100
        self.sig = 4
        self.bars_count_in = 1
        
        self.countedIn = False
        self.is_paused = False
        
        self.step = 0

        if setSounds is None:
            path_primary = "data/primary_ping.wav"
            path_secondary =  "data/secondary_ping.wav"
        else:
            logging.info("Got external redefinition of sounds : %s", setSounds)
            if not isinstance(setSounds, list) and len(setSounds) == 2:
                logging.error("SetSounds is : %s", setSounds)
                logging.error("Should be type list (is: %s) and have exactly 2 (but has %s) elements pointing to sound files",
                              type(setSounds), len(setSounds))
                raise RuntimeError("Could not process passed setSounds")
            else:
                path_primary = setSounds[0]
                path_secondary = setSounds[1]
                
        self.sounds = {
            "Primary" : QSound(path_primary),
            "Secondary" : QSound(path_secondary),
        }
        
        self.current_key_displayed = ""
        self.next_key_displayed = ""
        
        self.setWindowTitle(self.title)
        
        self.current_key_text = "C"
        self.current_sig_step = "1 / %s"%self.sig
        
        self.keys = ["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]
        self.theseKeys = self.keys
        
        self.isRunning = False
        
        self.bpm_label = QLabel('BPM')
        self.signature_label = QLabel('Time signature')
        self.count_in_label = QLabel('Bars count in')
        
        self.order_type_label = QLabel('Key order')
        self.start_key_label = QLabel('Starting Key')
        self.show_next_key_label = QLabel('Show next key for')
        
        self.bpm_dialog = QLineEdit("100")
        self.signature_upper_dialog = QLineEdit("4")
        self.count_in_dialog = QLineEdit("1")
        
        self.button_set_bpm = QPushButton("Set")
        self.button_set_bpm.clicked.connect(self.setTempo)
        
        self.button_set_signature = QPushButton("Set")
        self.button_set_signature.clicked.connect(self.setSignature)
        
        self.button_count_in_bars = QPushButton("Set")
        self.button_count_in_bars.clicked.connect(self.setCountIn)
        
        self.button_start = QPushButton("Start")
        self.button_start.clicked.connect(self.start)
        self.button_start.setObjectName('StartButton')
        self.button_start.setEnabled(True)
        
        self.button_stop = QPushButton("Stop")
        self.button_stop.clicked.connect(self.stop)
        self.button_stop.setObjectName('StopButton')
        self.button_stop.setEnabled(False)
        
        self.button_pause = QPushButton("Pause")
        self.button_pause.clicked.connect(self.pause)
        self.button_pause.setObjectName('StopButton')
        self.button_pause.setEnabled(False)

        self.order_type_dropdown = QComboBox()
        self.order_type_dropdown.addItems(["Circle of 4th", "Circle of 5th", "Random"])
        self.order_type_dropdown.currentIndexChanged.connect(self.set_order)
        
        self.start_key_dropdown = QComboBox()
        self.start_key_dropdown.addItems(self.keys + ["Random"])
        self.start_key_dropdown.currentTextChanged.connect(self.set_start_key)
        
        self.show_next_key_dropdown = QComboBox()
        self.show_next_key_dropdown.addItems(["Half bar", "Full bar", "1 Step", "Off"])
        self.show_next_key_dropdown.currentIndexChanged.connect(self.set_next_key)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        
        self.current_key = QLabel(self.current_key_text)
        self.current_key.setObjectName('CurrentKey')
        
        self.next_key = QLabel("D")
        self.next_key.setObjectName('NextKey')
        
        self.current_sig_step_label = QLabel(self.current_sig_step)
        self.current_sig_step_label.setObjectName('Signature')
        
        self.set_order(0)
        self.set_next_key(0)
        self.set_start_key("C")
        
        self.init_grid_layout()

    def init_grid_layout(self):
        self.setStyleSheet(
            """
            QLabel#CurrentKey { font-size: 80px }
            QLabel#NextKey { font-size: 50px; margin-bottom : 5px; color : #FF4C4C }
            QLabel#Signature  { font-size: 50px }
            QPushButton#StartButton { font-size: 20px }
            QPushButton#StopButton { font-size: 20px }
            """
        )
        self.grid_layout = QGridLayout()
        
        #########################################################
        self.grid_layout.addWidget(self.bpm_label, 1, 0)
        self.grid_layout.addWidget(self.signature_label, 1, 2)
        self.grid_layout.addWidget(self.count_in_label, 1, 4)
        
        #########################################################
        self.grid_layout.addWidget(self.bpm_dialog, 2, 0)
        self.grid_layout.addWidget(self.button_set_bpm, 2, 1)
        
        self.grid_layout.addWidget(self.signature_upper_dialog, 2, 2)
        self.grid_layout.addWidget(self.button_set_signature, 2, 3)
        
        self.grid_layout.addWidget(self.count_in_dialog, 2, 4)
        self.grid_layout.addWidget(self.button_count_in_bars, 2, 5)
        
        #########################################################
        self.grid_layout.addWidget(self.order_type_label, 3, 0)
        self.grid_layout.addWidget(self.start_key_label, 3, 2)
        self.grid_layout.addWidget(self.show_next_key_label, 3, 4)
        
        #########################################################
        self.grid_layout.addWidget(self.order_type_dropdown, 4, 0)
        self.grid_layout.addWidget(self.start_key_dropdown, 4, 2)
        self.grid_layout.addWidget(self.show_next_key_dropdown, 4, 4)
        
        #########################################################
        self.grid_layout.addWidget(self.current_key,
                                   5, 0, 1, 2,
                                   alignment=(Qt.AlignBottom | Qt.AlignCenter))
        self.grid_layout.addWidget(self.next_key,
                                   5, 2, 1, 2,
                                   alignment=(Qt.AlignBottom | Qt.AlignCenter))
        self.grid_layout.addWidget(self.current_sig_step_label,
                                   5, 4, 1, 2,
                                   alignment=Qt.AlignCenter)
        
        #########################################################
        self.grid_layout.addWidget(self.button_start, 6, 0, 1, 2)
        self.grid_layout.addWidget(self.button_pause, 6, 2, 1, 2)
        self.grid_layout.addWidget(self.button_stop, 6, 4, 1, 2)

        self.grid_layout.setColumnMinimumWidth(0, 140)
        self.grid_layout.setColumnStretch(0, 1)
        
        self.grid_layout.setColumnMinimumWidth(1, 140)
        self.grid_layout.setColumnStretch(1, 1)

        self.grid_layout.setColumnMinimumWidth(2, 140)
        self.grid_layout.setColumnStretch(2, 1)

        self.grid_layout.setColumnMinimumWidth(3, 140)
        self.grid_layout.setColumnStretch(3, 1)

        self.grid_layout.setColumnMinimumWidth(4, 140)
        self.grid_layout.setColumnStretch(4, 1)

        self.grid_layout.setColumnMinimumWidth(5, 140)
        self.grid_layout.setColumnStretch(5, 1)

        self.setLayout(self.grid_layout)
        
    def setTempo(self):
        """
        Sets the bpm.
        """
        logging.info("Setting BPM to %s", self.bpm_dialog.text())
        
        self.bpm = int(self.bpm_dialog.text())

    def setSignature(self):
        """
        Sets the signature. This means, how many steps are taken before the key change is displayed.
        """
        logging.info("Setting time signature to %s", self.signature_upper_dialog.text())
        self.sig = int(self.signature_upper_dialog.text())
        self.current_sig_step_label.setText("1 / %s"%self.sig)

    def setCountIn(self):
        """
        Sets the count in bars
        """
        logging.debug("Setting number of bars for count in to: %s", self.count_in_dialog.text())
        self.bars_count_in = int(self.count_in_dialog.text())
        if self.bars_count_in == 0:
            self.countedIn = True
        
    def set_order(self, i):
        """
        Sets to order of the keys that will be looped over.
        """
        if i == 0:
            logging.debug("Setting order to circle of 4th")
            self.theseKeys = ["C", "F", "A#/Bb", "D#/Eb", "G#/Ab", "C#/Db", "F#/Gb", "B", "E", "A", "D", "G"]
        elif i == 1:
            logging.debug("Setting order to circle of 5th")
            self.theseKeys = ["C", "G", "D", "A", "E", "B", "F#/Gb", "C#/Db", "G#/Ab", "D#/Eb", "A#/Bb", "F"]
        else:
            logging.debug("Setting random order")
            random.shuffle(self.theseKeys)
        logging.debug("Set of keys: %s", self.theseKeys)
        
        self.set_start_key(self.start_key_dropdown.currentText())
        
    def set_start_key(self, startKey):
        """
        Set the starting key of the loop
        """
        logging.debug("Setting start key to %s", startKey)
        if startKey == "Random":
            startKey = random.choice(self.theseKeys)
            logging.debug("Choose: %s", startKey)
        if startKey not in self.theseKeys:
            raise KeyError("%s not in self.theseKeys list. This should not happen")
        indexKey = self.theseKeys.index(startKey)
        self.theseKeys = self.theseKeys[indexKey::]+self.theseKeys[0:indexKey]

    def set_next_key(self, i):
        """
        Set if and how long the next key will be shown
        """
        # Half bar
        if i == 0:
            self.steps_show_next_key = self.sig / 2
        # Full bar
        elif i == 1:
            self.steps_show_next_key = self.sig
        # 1 step
        elif i == 2:
            self.steps_show_next_key = 1
        # Off
        else:
            self.steps_show_next_key = 0

        logging.debug("The next key will be shown for %s steps", self.steps_show_next_key)
            
    def stop(self):
        """
        Stop the training loop. This will enable all buttons and disable the stop button.
        """
        logging.info("Stopping loop")
        self.timer.stop()
        
        self.change_button_state(True)
    
        # Reset steps
        self.step = 0
        # Reset count in
        self.countedIn = False
        self.is_paused = False
        
    def pause(self):
        """
        Pause loop but do not reset anything.
        """
        logging.debug("Pausing loop")
        self.is_paused = True
        
        self.timer.stop()
        self.button_start.setEnabled(True)
        self.button_pause.setEnabled(False)
        
    def start(self):
        """
        Start the training loop. This will disable all buttons and enable the stop button.
        """
        if not self.is_paused:
            logging.info("Starting training")
            self.cycleKeys = itertools.cycle(self.theseKeys)
            self.current_key_displayed = next(self.cycleKeys)
            self.next_key_displayed = next(self.cycleKeys)

        hold_time = (60000/self.bpm)
        logging.debug("BPM: %s -> Hold time: %s ms", self.bpm, hold_time)
        self.timer.start(hold_time)

        self.change_button_state(False)
        
    def update(self):
        """
        Update function that is expecuted for every time step, set with the bpm variable.
        For every step the signature lable will be updated
        For every self.sig step, the Key label will be updated
        """
        # Regular operation
        if self.countedIn:
            if self.step == self.sig:
                self.step = 0
            logging.debug("Step %s", self.step)

            # Update the Key label
            if self.step == 0:
                currentKey = self.next_key_displayed
                self.next_key_displayed = next(self.cycleKeys)
                logging.debug("Current key: %s", currentKey)
                logging.debug("Next key: %s", self.next_key_displayed)
                self.current_key.setText(currentKey)
                self.next_key.setText("")
                
            if self.step == self.sig - self.steps_show_next_key:
                self.next_key.setText(self.next_key_displayed)

            # Sounds:
            if self.step == 0:
                self.sounds["Primary"].play()
            else:
                self.sounds["Secondary"].play()
            
            self.step += 1
            # Update the signature label
            self.current_sig_step_label.setText("%s / %s"%(self.step, self.sig))
        # Count in operation
        else:
            logging.debug("Step %s", self.step)
            # Last step of the count in: Set the countedIn flag to True
            if self.step == (self.bars_count_in*self.sig)-1:
                logging.debug("Last step of count in")
                self.current_sig_step_label.setText("%s / %s"%(self.step+1, self.bars_count_in*self.sig))
                self.countedIn = True
                self.step = 0
            else:
                if self.step == 0:
                    self.current_key.setText("Count in")
                    self.next_key.setText(self.current_key_displayed)
                self.step += 1
                # Update the signature label
                self.current_sig_step_label.setText("%s / %s"%(self.step, self.bars_count_in*self.sig))
            # Sound
            self.sounds["Secondary"].play()
            
    def change_button_state(self, flag):
        """
        Method to enable/disable all buttons and drop down when pressing the start of stop.
        """
        # Dialogs
        self.bpm_dialog.setEnabled(flag)
        self.signature_upper_dialog.setEnabled(flag)
        self.count_in_dialog.setEnabled(flag)
        # Buttons
        self.button_start.setEnabled(flag)
        self.button_pause.setEnabled(not flag)
        self.button_stop.setEnabled(not flag)
        self.button_set_signature.setEnabled(flag)
        self.button_set_bpm.setEnabled(flag)
        self.button_count_in_bars.setEnabled(flag)
        # Dropdowns
        self.order_type_dropdown.setEnabled(flag)
        self.start_key_dropdown.setEnabled(flag)
        self.show_next_key_dropdown.setEnabled(flag)


if __name__ == "__main__":
    logging.basicConfig(encoding='utf-8', level=logging.DEBUG)
    logging.info("Starting application")
    
    app = QApplication(sys.argv)
    trainer = KeyTrainer()
    trainer.show()

    # TEMP Some debugging and testing code
    print("0", trainer.grid_layout.columnMinimumWidth(0), trainer.grid_layout.columnStretch(0))
    print("1", trainer.grid_layout.columnMinimumWidth(1), trainer.grid_layout.columnStretch(1))
    print("2", trainer.grid_layout.columnMinimumWidth(2), trainer.grid_layout.columnStretch(2))
    print("3", trainer.grid_layout.columnMinimumWidth(3), trainer.grid_layout.columnStretch(3))
    print("4", trainer.grid_layout.columnMinimumWidth(4), trainer.grid_layout.columnStretch(4))
    print("5", trainer.grid_layout.columnMinimumWidth(5), trainer.grid_layout.columnStretch(5))
    
    # Run the main Qt loop
    sys.exit(app.exec_())
