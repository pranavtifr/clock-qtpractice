#!/usr/bin/env python
from time import monotonic as timer # or time.time if it is not available
import math
import sys
from PyQt5.QtWidgets import *
import dbus
import threading

_session_bus = dbus.SessionBus()
_dbus_screensaver = _session_bus.get_object('org.freedesktop.ScreenSaver','/ScreenSaver')
simulate_activity = _dbus_screensaver.get_dbus_method('SimulateUserActivity','org.freedesktop.ScreenSaver')
simulate_activity()

class Widget(QWidget):
  def __init__(self):
    super().__init__()
    self.initUI()
  def initUI(self):               
    self.N = 0.5
    self.combo = QComboBox(self)
    self.combo.addItem("30 Mins")
    self.combo.addItem("1 Hour")
    self.combo.addItem("1.5 Hours")
    self.combo.addItem("2 Hours")
    self.combo.activated[str].connect(self.timechange)
    self.flag = threading.Event()
    self.label = QLabel('TIME',self)
    self.label.move(150,30)
    self.okButton = QPushButton("OK")
    self.cancelButton = QPushButton("Cancel")
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

    self.setGeometry(300, 300, 350, 150)
    self.setWindowTitle('Statusbar')    
    self.show()

  def run_clock(self):
    self.flag.set()
    self.endtime = timer() + (self.N * 3600)
    while timer() < self.endtime:
      time = self.endtime - timer()
      displaytime = to_humantime(time)
      print(" Time Remaining :",displaytime,'\r',end='')
      self.label.setText(displaytime)    
      simulate_activity()
      if not self.flag.is_set():
        break
    return

  def close_application(self):
    choice = QMessageBox.question(self, 'Running!!',
                                          "Timer Already running . You want to cancel ?",
                                          QMessageBox.Yes | QMessageBox.No)
    if choice == QMessageBox.Yes:
      self.Kill()
      sys.exit()
    else:
      pass

  def timechange(self,text):
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
    return
  def Kill(self):          
    self.flag.clear()
    try:
      self.p.join()
      self.interrupt()
    except AttributeError:
      pass
    quit()

  def Run(self):            
    self.p = threading.Thread(target=self.run_clock, name="_proc")
    self.p.start()

  def interrupt(self):
    time = self.endtime - timer()
    displaytime = to_humantime(time)
    print ("Interrupted with ",displaytime," time remaining" )
    sys.exit(0)

def to_humantime(time): # This time needs to be in secs as float
  sec = int(math.floor(time))
  micro = time - sec
  hrs = int(sec/3600)
  mins = int(sec/60) - hrs*60
  secs = int(sec)-hrs*3600 - mins*60
  displaytime = str(hrs) + ":" + str(mins).zfill(2) + ":"+str(secs).zfill(2)+":"+str(int(micro*100)).zfill(2)
  return displaytime



app = QApplication(sys.argv)
ex = Widget()
sys.exit(app.exec_())
