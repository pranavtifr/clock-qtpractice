#!/usr/bin/env python
"""Stopclock using Qt."""

from time import monotonic as timer
import math
import sys
import threading
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QFont
import dbus

SIMULATEACTIVITY = (
    dbus.SessionBus()
    .get_object("org.freedesktop.ScreenSaver", "/ScreenSaver")
    .get_dbus_method("SimulateUserActivity", "org.freedesktop." "ScreenSaver")
)
SIMULATEACTIVITY()


class Widget(QWidget):
    """Widget.

    This creates the UI for usage
    """

    def __init__(self):
        """Init Func."""
        super().__init__()
        self.N = 0.5
        self.initUI()

    def initUI(self):
        """Construct the UI."""
        self.combo = QComboBox(self)
        self.combo.addItem("30 Mins")
        self.combo.addItem("1 Hour")
        self.combo.addItem("1.5 Hours")
        self.combo.addItem("2 Hours")
        self.combo.activated.connect(self.timechange)
        self.flag = threading.Event()
        font = QFont()
        # font.setFamily(_fromUtf8("FreeMono"))
        font.setBold(True)
        font.setPointSize(15)
        self.label = QLabel("TIME", self)
        self.label.move(150, 30)
        self.label.setFont(font)
        self.okButton = QPushButton("Start")
        self.cancelButton = QPushButton("Exit")
        self.okButton.clicked.connect(self.Run)
        self.cancelButton.clicked.connect(self.Kill)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setGeometry(300, 300, 400, 100)
        self.setWindowTitle("Statusbar")
        self.show()

    def run_clock(self):
        """Run the Clock."""
        if self.flag.is_set():
            self.flag.clear()
        self.flag.set()
        self.endtime = timer() + (self.N * 3600)
        while timer() < self.endtime:
            time = self.endtime - timer()
            displaytime = to_humantime(time)
            print(" Time Remaining :", displaytime, "\r", end="")
            self.label.setText(displaytime)
            SIMULATEACTIVITY()
            if not self.flag.is_set():
                break

    # return

    def close_application(self):
        """Close button."""
        choice = QMessageBox.question(
            self,
            "Running!!",
            "Timer Already running. " "You want to cancel ?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if choice == QMessageBox.Yes:
            self.Kill()
            sys.exit()
        else:
            pass

    def timechange(self, text):
        """Dropdown menu."""
        if self.flag.is_set():
            self.close_application()
        if text == "30 Mins":
            self.N = 0.5
        if text == "1 Hour":
            self.N = 1
        if text == "1.5 Hours":
            self.N = 1.5
        if text == "2 Hours":
            self.N = 2

    def Kill(self):
        """Handle kills."""
        self.flag.clear()
        try:
            self.p.join()
            self.interrupt()
        except AttributeError:
            sys.exit(0)

    def Run(self):
        """Call the run_clock function in a different thread."""
        self.p = threading.Thread(target=self.run_clock, name="_proc")
        self.p.start()

    def interrupt(self):
        """Message for interrupt."""
        time = self.endtime - timer()
        displaytime = to_humantime(time)
        print("Interrupted with ", displaytime, " time remaining")
        sys.exit(0)


def to_humantime(time):
    """Convert seconds to human readable format."""
    sec = int(math.floor(time))
    micro = time - sec
    hrs = int(sec / 3600)
    mins = int(sec / 60) - hrs * 60
    secs = int(sec) - hrs * 3600 - mins * 60
    displaytime = (
        str(hrs)
        + ":"
        + str(mins).zfill(2)
        + ":"
        + str(secs).zfill(2)
        + ":"
        + str(int(micro * 100)).zfill(2)
    )
    return displaytime


APP = QApplication(sys.argv)
ex = Widget()
sys.exit(APP.exec_())
