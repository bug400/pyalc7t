#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pyalc7t 1.0.0 
#
# Steuerprogramm und Datenlogger für das Ladegerät ALC 7000 von ELV-Elektronik
# Das Kommunikationsprotokoll und die Messwertverarbeitung wurden aus dem
# Programm alc7t.bas von Frank Steinberg (www.FrankSteinberg.de) entnommen.
# (c) Frank Steinberg 2006
# (c) Joachim Siebold (Python version) 2017
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# alc7t GUI Klassen -------------------------------------------------------
#
# Changelog
# 06.02.2017 jsi
# - Ersterstellung
# 30.03.2017 jsi
# - Input Mask bei Kanalkonfiguration auf 2 Nachkommastellen begrenzt
# - Nennkapazität, Lade- und Entladestrom können nicht 0 sein
# 14.04.2017 jsi
# - Fehlermeldungen verbessert
# 14.05.2017 jsi
# - Fehlermeldungen eingedeutscht
# 20.05.2017 jsi:
# - fehlerhafter Aufruf von QMessagebox behoben
# 21.05.2017 jsi:
# - Save file dialog korrigiert, Feld Beschreibung entfernt
# 25.05.2017 jsi:
# - Bugfix Feld Beschreibung entfernt
# 21.06.2017 jsi:
# - Diagrammgröße konfigurierbar
# 06.11.2018 jsi:
# - Pause zwischen Messungen konfigurierbar
# 30.11.2022 jsi
# - PySide6 Migration
# 05.02.2024 jsi
# - removed deprecation warnings
#
import os
import glob
import sys
import re
import json
from .alcconfig import ALCCONFIG
from .alccore import *
if isWINDOWS():
   import winreg
if QTBINDINGS=="PySide6":
   from PySide6 import QtCore, QtWidgets
   if HAS_WEBENGINE:
      from PySide6 import QtWebEngineWidgets
if QTBINDINGS=="PyQt5":
   from PyQt5 import QtCore, QtWidgets
   if HAS_WEBKIT:
      from PyQt5 import QtWebKitWidgets
   if HAS_WEBENGINE:
      from PyQt5 import QtWebEngineWidgets

import pyalc7t

#

#
# About Dialog class --------------------------------------------------------
#
class cls_AboutWindow(QtWidgets.QDialog):

   def __init__(self,version):
      super().__init__()
      if QTBINDINGS=="PySide6":
         self.qtversion=QtCore.__version__
      if QTBINDINGS=="PyQt5":
         self.qtversion=QtCore.QT_VERSION_STR

      self.pyversion=str(sys.version_info.major)+"."+str(sys.version_info.minor)+"."+str(sys.version_info.micro)
      self.setWindowTitle('pyALC7T About ...')
      self.vlayout = QtWidgets.QVBoxLayout()
      self.setLayout(self.vlayout)
      self.view = QtWidgets.QLabel()
      self.view.setFixedWidth(300)
      self.view.setWordWrap(True)
      self.view.setText("pyALC7T "+version+ "\n\nDatenlogger für das Ladegerät ALC 7000 Expert. Abgeleitet von  Alc7t für DOS.\n\nCopyright (c) 2006 Frank Steinberg.\nPython Version (c) 2015-2017 Joachim Siebold.\n\nGNU General Public License Version 2.\n\nSie verwenden Python "+self.pyversion+" und Qt "+self.qtversion+".\n")


      self.button = QtWidgets.QPushButton('OK')
      self.button.setFixedWidth(60)
      self.button.clicked.connect(self.do_exit)
      self.vlayout.addWidget(self.view)
      self.hlayout = QtWidgets.QHBoxLayout()
      self.hlayout.addWidget(self.button)
      self.vlayout.addLayout(self.hlayout)

   def do_exit(self):
      self.hide()

#
# Help Dialog class ----------------------------------------------------------
#
class HelpError(Exception):
   def __init__(self,value):
      self.value=value
   def __str__(self):
      return repr(self.value)

class cls_HelpWindow(QtWidgets.QDialog):
   def __init__(self,parent=None):
#
      super().__init__()
      self.setWindowTitle('pyALC7T Manual')

      self.vlayout = QtWidgets.QVBoxLayout()
      self.setLayout(self.vlayout)
      if HAS_WEBKIT:
         self.view = QtWebKitWidgets.QWebView()
      if HAS_WEBENGINE:
         self.view = QtWebEngineWidgets.QWebEngineView()
      if not HAS_WEBENGINE and not HAS_WEBKIT:
         raise HelpError("Die Python bindings für QtWebKit oder QtWebEngine fehlen. Die Online-Hilfe kann nicht angezeitg werden.")
      self.view.setMinimumWidth(600)
      self.vlayout.addWidget(self.view)
      self.buttonExit = QtWidgets.QPushButton('Exit')
      self.buttonExit.setFixedWidth(60)
      self.buttonExit.clicked.connect(self.do_exit)
      self.buttonBack = QtWidgets.QPushButton('<')
      self.buttonBack.setFixedWidth(60)
      self.buttonForward = QtWidgets.QPushButton('>')
      self.buttonForward.setFixedWidth(60)
      self.hlayout = QtWidgets.QHBoxLayout()
      self.hlayout.addWidget(self.buttonBack)
      self.hlayout.addWidget(self.buttonExit)
      self.hlayout.addWidget(self.buttonForward)
      self.vlayout.addLayout(self.hlayout)
      if HAS_WEBKIT or HAS_WEBENGINE:
         self.buttonBack.clicked.connect(self.do_back)
         self.buttonForward.clicked.connect(self.do_forward)

   def do_exit(self):
      self.hide()

   def do_back(self):
      self.view.back()

   def do_forward(self):
      self.view.forward()

   def loadDocument(self,subdir,document):
      if subdir=="":
         docpath=os.path.join(os.path.dirname(pyalc7t.__file__),"Manual",document)
      else:
         docpath=os.path.join(os.path.dirname(pyalc7t.__file__),"Manual",subdir,document)
      docpath=re.sub("//","/",docpath,1)
      self.view.load(QtCore.QUrl.fromLocalFile(docpath))

#
#  TTy  Dialog class ----------------------------------------------------------
#
class cls_TtyWindow(QtWidgets.QDialog):

   def __init__(self, parent=None):
      super().__init__()

      self.setWindowTitle("Serielle Schnittstelle")
      self.vlayout= QtWidgets.QVBoxLayout()
      self.setLayout(self.vlayout)

      self.label= QtWidgets.QLabel()
      self.label.setText("Serielle Schnittstelle auswählen oder eingeben")
      self.label.setAlignment(QtCore.Qt.AlignCenter)

      self.__ComboBox__ = QtWidgets.QComboBox()
      self.__ComboBox__.setEditable(True)

      if isWINDOWS():
#
#        Windows COM ports aus registry ermitteln
#
         try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"Hardware\DeviceMap\SerialComm",0,winreg.KEY_QUERY_VALUE|winreg.KEY_ENUMERATE_SUB_KEYS) as key:
               for i in range (0, winreg.QueryInfoKey(key)[1]):
                  port = winreg.EnumValue(key, i)[1]
                  self.__ComboBox__.addItem( port, port )
         except FileNotFoundError:
            pass
      elif isLINUX():
#
#        Linux /dev/ttyUSB?
#
         devlist=glob.glob("/dev/ttyUSB*")
         for port in devlist:
            self.__ComboBox__.addItem( port, port )
#
#        Mac OS X /dev/tty.usbserial-*
#
      elif isMACOS():
         devlist=glob.glob("/dev/tty.usbserial-*")
         for port in devlist:
            self.__ComboBox__.addItem( port, port )

      else:
#
#        Andere ...
#
         devlist=glob.glob("/dev/tty*")
         for port in devlist:
            self.__ComboBox__.addItem( port, port )

      self.__ComboBox__.activated[int].connect(self.combobox_choosen)
      self.__ComboBox__.editTextChanged.connect(self.combobox_textchanged)
      self.buttonBox = QtWidgets.QDialogButtonBox()
      self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
      self.buttonBox.setCenterButtons(True)
      self.buttonBox.accepted.connect(self.do_ok)
      self.buttonBox.rejected.connect(self.do_cancel)
      self.vlayout.addWidget(self.label)
      self.vlayout.addWidget(self.__ComboBox__)
      self.hlayout = QtWidgets.QHBoxLayout()
      self.hlayout.addWidget(self.buttonBox)
      self.vlayout.addWidget(self.buttonBox)
      self.__device__= ""

   def do_ok(self):
      if self.__device__=="":
         self.__device__= self.__ComboBox__.currentText()
         if self.__device__=="":
            return
      super().accept()

   def do_cancel(self):
      super().reject()


   def combobox_textchanged(self, device):
      self.__device__= device

   def combobox_choosen(self, device):
      self.__device__= device

   def getDevice(self):
      return self.__device__

   @staticmethod
   def getTtyDevice(parent=None):
      dialog= cls_TtyWindow(parent)
      result= dialog.exec()
      if result== QtWidgets.QDialog.Accepted:
         return dialog.getDevice()
      else:
         return ""
#
# alc7t Konfigurations dialog
#
class cls_AlcConfigWindow(QtWidgets.QDialog):

   def __init__(self, parent):
      super().__init__()
      self.__name__=parent.name
      self.__parent__=parent
      self.__tty__= ALCCONFIG.get(self.__name__,"tty")
      self.__workdir__= ALCCONFIG.get(self.__name__,"workdir")
      self.__gnuplot__= ALCCONFIG.get(self.__name__,"gnuplot")
      self.__plotsize__= ALCCONFIG.get(self.__name__,"plotsize")
      self.__delay__= ALCCONFIG.get(self.__name__,"delay")


      self.win = QtWidgets.QWidget()
      self.setWindowTitle("pyALC7T Konfiguration")
      self.vbox0= QtWidgets.QVBoxLayout()
      self.setLayout(self.vbox0)
#
#     serial device
#
      self.gboxtty= QtWidgets.QGroupBox()
      self.gboxtty.setFlat(True)
      self.gboxtty.setTitle("Serielle Schnittstelle: ")
      self.vboxgboxt= QtWidgets.QVBoxLayout()
      self.gboxtty.setLayout(self.vboxgboxt)
      self.hboxtty= QtWidgets.QHBoxLayout()
      self.lbltty=QtWidgets.QLabel()
      self.lbltty.setText(self.__tty__)
      self.hboxtty.addWidget(self.lbltty)
      self.hboxtty.setAlignment(self.lbltty,QtCore.Qt.AlignLeft)
      self.hboxtty.addStretch(1)
      self.buttty=QtWidgets.QPushButton()
      self.buttty.setText("Ändern")
      self.buttty.pressed.connect(self.do_config_Interface)
      self.hboxtty.addWidget(self.buttty)
      self.hboxtty.setAlignment(self.buttty,QtCore.Qt.AlignRight)
      self.vboxgboxt.addLayout(self.hboxtty)
      self.vbox0.addWidget(self.gboxtty)
#
#     Working Directory
#
      self.gboxw = QtWidgets.QGroupBox()
      self.gboxw.setFlat(True)
      self.gboxw.setTitle("Arbeitsverzeichnis")
      self.vboxgboxw= QtWidgets.QVBoxLayout()
      self.gboxw.setLayout(self.vboxgboxw)
      self.hboxwdir= QtWidgets.QHBoxLayout()
      self.lblwdir=QtWidgets.QLabel()
      self.lblwdir.setText(self.__workdir__)
      self.hboxwdir.addWidget(self.lblwdir)
      self.hboxwdir.setAlignment(self.lblwdir,QtCore.Qt.AlignLeft)
      self.hboxwdir.addStretch(1)
      self.butwdir=QtWidgets.QPushButton()
      self.butwdir.setText("Ändern")
      self.butwdir.pressed.connect(self.do_config_Workdir)
      self.hboxwdir.addWidget(self.butwdir)
      self.hboxwdir.setAlignment(self.butwdir,QtCore.Qt.AlignRight)
      self.vboxgboxw.addLayout(self.hboxwdir)
      self.vbox0.addWidget(self.gboxw)
#
#     Messwert delay
#
      self.gboxd = QtWidgets.QGroupBox()
      self.gboxd.setFlat(True)
      self.gboxd.setTitle("Wartezeit zwischen Messungen")
      self.spindelay=QtWidgets.QSpinBox()
      self.spindelay.setMinimum(0)
      self.spindelay.setMaximum(5)
      self.spindelay.setValue(self.__delay__)
      self.hboxd= QtWidgets.QHBoxLayout()
      self.hboxd.addStretch(1)
      self.hboxd.addWidget(self.spindelay)
      self.hboxd.addStretch(1)
      self.gboxd.setLayout(self.hboxd)
      self.vbox0.addWidget(self.gboxd)
#
#     Gnuplot Path
#
      self.gboxg = QtWidgets.QGroupBox()
      self.gboxg.setFlat(True)
      self.gboxg.setTitle("Gnuplot Pfad")
      self.vboxgboxg= QtWidgets.QVBoxLayout()
      self.gboxg.setLayout(self.vboxgboxg)
      self.hboxgdir= QtWidgets.QHBoxLayout()
      self.lblgdir=QtWidgets.QLabel()
      self.lblgdir.setText(self.__gnuplot__)
      self.hboxgdir.addWidget(self.lblgdir)
      self.hboxgdir.setAlignment(self.lblwdir,QtCore.Qt.AlignLeft)
      self.hboxgdir.addStretch(1)
      self.butgdir=QtWidgets.QPushButton()
      self.butgdir.setText("Ändern")
      self.butgdir.pressed.connect(self.do_config_Gnuplot)
      self.hboxgdir.addWidget(self.butgdir)
      self.hboxgdir.setAlignment(self.butwdir,QtCore.Qt.AlignRight)
      self.vboxgboxg.addLayout(self.hboxgdir)
      self.vbox0.addWidget(self.gboxg)
#
#     Plotsize
#
      self.gboxp = QtWidgets.QGroupBox()
      self.gboxp.setFlat(True)
      self.gboxp.setTitle("Diagrammgröße")
      self.spinplotsize=QtWidgets.QSpinBox()
      self.spinplotsize.setMinimum(300)
      self.spinplotsize.setMaximum(600)
      self.spinplotsize.setValue(self.__plotsize__)
      self.hboxp= QtWidgets.QHBoxLayout()
      self.hboxp.addStretch(1)
      self.hboxp.addWidget(self.spinplotsize)
      self.hboxp.addStretch(1)
      self.gboxp.setLayout(self.hboxp)
      self.vbox0.addWidget(self.gboxp)
#
#     ok/cancel buttons
#

      self.buttonBox = QtWidgets.QDialogButtonBox()
      self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
      self.buttonBox.setCenterButtons(True)
      self.buttonBox.accepted.connect(self.do_ok)
      self.buttonBox.rejected.connect(self.do_cancel)
      self.hlayout = QtWidgets.QHBoxLayout()
      self.hlayout.addWidget(self.buttonBox)
      self.vbox0.addLayout(self.hlayout)

   def do_config_Interface(self):
      interface= cls_TtyWindow.getTtyDevice()
      if interface == "" :
         return
      self.__tty__= interface
      self.lbltty.setText(self.__tty__)

   def getWorkDirName(self):
      dialog=QtWidgets.QFileDialog()
      dialog.setWindowTitle("pyALC7T Arbeitsverzeichnis auswählen")
      dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
      dialog.setFileMode(QtWidgets.QFileDialog.Directory)
      dialog.setOptions(QtWidgets.QFileDialog.DontUseNativeDialog)
      if dialog.exec():
         return dialog.selectedFiles()

   def do_config_Workdir(self):
      flist=self.getWorkDirName()
      if flist== None:
         return
      self.__workdir__= flist[0]
      self.lblwdir.setText(self.__workdir__)

   def getGnuplotFileName(self):
      dialog=QtWidgets.QFileDialog()
      dialog.setWindowTitle("Gnuplot Programm auswählen")
      dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
      dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
      dialog.setOptions(QtWidgets.QFileDialog.DontUseNativeDialog)
      if dialog.exec():
         return dialog.selectedFiles()

   def do_config_Gnuplot(self):
      flist=self.getGnuplotFileName()
      if flist== None:
         return
      self.__gnuplot__= flist[0]
      self.lblgdir.setText(self.__gnuplot__)

   def do_ok(self):
      ALCCONFIG.put(self.__name__,"tty", self.lbltty.text())
      ALCCONFIG.put(self.__name__,"workdir",self.lblwdir.text())
      ALCCONFIG.put(self.__name__,"gnuplot",self.lblgdir.text())
      ALCCONFIG.put(self.__name__,"plotsize",self.spinplotsize.value())
      ALCCONFIG.put(self.__name__,"delay",self.spindelay.value())
      super().accept()

   def do_cancel(self):
      super().reject()

   def getConfig(self):
      return self.__config__

   @staticmethod
   def getAlcConfig(parent):
      dialog= cls_AlcConfigWindow(parent)
      result= dialog.exec()
      if result== QtWidgets.QDialog.Accepted:
         return True
      else:
         return False
#
# Kanal widget class --------------------------------------------------------
#
class cls_KanalWidget(QtWidgets.QFrame):

   def __init__(self, kanalnummer):
      super().__init__()
      self.conflabels= { }
      self.messlabels= { }

      self.setFont(FONT_NORMAL)

      self.vbox= QtWidgets.QVBoxLayout()
      self.setLayout(self.vbox)
      self.vbox.setAlignment(QtCore.Qt.AlignTop)

      self.lh=QtWidgets.QLabel("Kanal "+str(kanalnummer))
      self.lh.setFont(FONT_BOLD)
      self.lh.setAlignment(QtCore.Qt.AlignRight)
      self.vbox.addWidget(self.lh)
      self.vbox.addSpacing(10)

      for i in range(7):
         self.conflabels[i]= self.lp=QtWidgets.QLabel("")
         self.conflabels[i].setAlignment(QtCore.Qt.AlignRight)
         self.vbox.addWidget(self.conflabels[i])

      self.vbox.addSpacing(10)
      self.sp=QtWidgets.QLabel(" ")
      self.sp.setFont(FONT_BOLD)
      self.sp.setAlignment(QtCore.Qt.AlignRight)
      self.vbox.addWidget(self.sp)
      self.vbox.addSpacing(10)

      for i in range(12):
         self.messlabels[i]= self.lp=QtWidgets.QLabel("")
         self.messlabels[i].setAlignment(QtCore.Qt.AlignRight)
         self.vbox.addWidget(self.messlabels[i])
#
#  Alle Anzeigen zurücksetzen
#

   def reset(self):
      self.reset_conf()
      self.reset_mess()
#
#  Konfigurationsdaten im GUI zurücksetzen
#

   def reset_conf(self):
      self.conflabels[0].setText("-")
      self.conflabels[1].setText("-")
      self.conflabels[2].setText("-")
      self.conflabels[3].setText("-.- V")
      self.conflabels[4].setText("-.---- Ah")
      self.conflabels[5].setText("-.--- A")
      self.conflabels[6].setText("-.--- A")
#     self.conflabels[7].setText("-")
#
#  Konfiguration im GUI anzeigen
#
   def display_conf(self,progr,aktyp,anzzellen,unenn,cnenn,ilad,ientlad,beschreibung):
      self.conflabels[0].setText(progr)
      self.conflabels[1].setText(aktyp)
      self.conflabels[2].setText(anzzellen)
      self.conflabels[3].setText(unenn)
      self.conflabels[4].setText(cnenn)
      self.conflabels[5].setText(ilad)
      self.conflabels[6].setText(ientlad)
#     self.conflabels[7].setText(beschreibung)
#
#  Messwerte im GUI zurücksetzen
#
   def reset_mess(self):
      self.messlabels[0].setText("-")
      self.messlabels[1].setText("-")
      self.messlabels[2].setText("--:--:--")
      self.messlabels[3].setText("-.--- V")
      self.messlabels[4].setText("-.--- V")
      self.messlabels[5].setText("-.--- V")
      self.messlabels[6].setText("-.--- V")
      self.messlabels[7].setText("-.--- A")
      self.messlabels[8].setText("-")
      self.messlabels[9].setText("-.--- A")
      self.messlabels[10].setText("-.--- A")
      self.messlabels[11].setText("-")
#
#  Messwerte im GUI anzeigen
#
   def display_mess(self,kanstatus,akstatus,daufz,umess,umax,umin,dp,cmess,irichtg,clad_alt, centlad_alt, mwdatei):
      self.messlabels[0].setText(kanstatus)
      self.messlabels[1].setText(akstatus)
      self.messlabels[2].setText(daufz)
      self.messlabels[3].setText(umess)
      self.messlabels[4].setText(umax)
      self.messlabels[5].setText(umin)
      self.messlabels[6].setText(dp)
      self.messlabels[7].setText(cmess)
      self.messlabels[8].setText(irichtg)
      self.messlabels[9].setText(clad_alt)
      self.messlabels[10].setText(centlad_alt)
      self.messlabels[11].setText(mwdatei)

#
# Main Window user interface -----------------------------------------------
#
class cls_ui(QtWidgets.QMainWindow):

   def __init__(self,parent,version):
      super().__init__()
      self.kmenus= { }
      self.setWindowTitle("pyALC7T "+version)
#
#     signals
#
      self.sig_crash= parent.sig_crash
      self.sig_quit= parent.sig_quit
      self.sig_show_message= parent.sig_show_message
#
#     Fonts initialisieren 
#
      FONT_NORMAL=QtGui.QFont()
      FONT_BOLD=QtGui.QFont()
      FONT_BOLD.setBold(True)
      FONT_BIG=QtGui.QFont()
      fontinfo= QtGui.QFontInfo(FONT_NORMAL)
      pointsize=fontinfo.pointSize()
      FONT_BIG.setBold(True)
      FONT_BIG.setPointSize(pointsize+4)
#
#     Menu erzeugen
#
      self.menubar = self.menuBar()
      self.menubar.setNativeMenuBar(False)
      self.menuFile= self.menubar.addMenu('Datei')
      for k in { KANAL1, KANAL2, KANAL3, KANAL4 } :
         self.kmenus[k]= self.menubar.addMenu("Kanal "+str(k))
      self.menuHelp= self.menubar.addMenu('Hilfe')

      self.actionConfig=self.menuFile.addAction("pyALC7T Konfiguration")
      self.actionReconnect=self.menuFile.addAction("Neu verbinden")
      self.actionExit=self.menuFile.addAction("Beenden")

      self.actionAbout=self.menuHelp.addAction("Über")
      self.actionHelp=self.menuHelp.addAction("Handbuch")
#
#     Central widget 
#
      self.centralwidget= QtWidgets.QWidget()
      self.centralwidget.setContentsMargins(20,10,20,10)
      self.setCentralWidget(self.centralwidget)
      self.setFont(FONT_NORMAL)

      self.vbox= QtWidgets.QVBoxLayout()
      self.vbox.setAlignment(QtCore.Qt.AlignTop)
      self.centralwidget.setLayout(self.vbox)
#
#     Main Layout
#
      self.progname= QtWidgets.QLabel("ALC 7000")
      self.progname.setFont(FONT_BIG)
      self.progname.setContentsMargins(0,5,5,5)

      self.vbox.addWidget(self.progname)
      self.hbox= QtWidgets.QHBoxLayout()
      self.hbox.setAlignment( QtCore.Qt.AlignLeft)
      self.vbox.addLayout(self.hbox)
#
#     Labels Frame
#
      self.lframe=QtWidgets.QFrame()
      self.vlbox= QtWidgets.QVBoxLayout()
      self.lframe.setLayout(self.vlbox)
      self.vlbox.setAlignment(QtCore.Qt.AlignTop)
      self.lh=QtWidgets.QLabel("Einstallungen")
      self.lh.setFont(FONT_BOLD)
      self.vlbox.addWidget(self.lh)
 
      self.vlbox.addSpacing(10)

      self.vlbox.addWidget(QtWidgets.QLabel("Programm"))
      self.vlbox.addWidget(QtWidgets.QLabel("Akkutyp"))
      self.vlbox.addWidget(QtWidgets.QLabel("Zellenzahl"))
      self.vlbox.addWidget(QtWidgets.QLabel("Nennspannung"))
      self.vlbox.addWidget(QtWidgets.QLabel("Nennkapazität"))
      self.vlbox.addWidget(QtWidgets.QLabel("Ladestrom"))
      self.vlbox.addWidget(QtWidgets.QLabel("Entladestrom"))
      
      self.vlbox.addSpacing(10)
      self.mw=QtWidgets.QLabel("Messwerte")
      self.mw.setFont(FONT_BOLD)
      self.vlbox.addWidget(self.mw)
      self.vlbox.addSpacing(10)
     
      self.vlbox.addWidget(QtWidgets.QLabel("Kanalstatus"))
      self.vlbox.addWidget(QtWidgets.QLabel("Akkustatus"))
      self.vlbox.addWidget(QtWidgets.QLabel("Dauer der Aufzeichnung"))
      self.vlbox.addWidget(QtWidgets.QLabel("Aktuelle Spannung"))
      self.vlbox.addWidget(QtWidgets.QLabel("Maximalspannung"))
      self.vlbox.addWidget(QtWidgets.QLabel("Mininalspannung"))
      self.vlbox.addWidget(QtWidgets.QLabel("Delta-Peak des letzten Ladens"))
      self.vlbox.addWidget(QtWidgets.QLabel("Aktueller Strom"))
      self.vlbox.addWidget(QtWidgets.QLabel("Stromrichtung"))
      self.vlbox.addWidget(QtWidgets.QLabel("Letzte geladene Kapazität"))
      self.vlbox.addWidget(QtWidgets.QLabel("Letzte entladene Kapazität"))
      self.vlbox.addWidget(QtWidgets.QLabel("Messwertdatei"))
      self.hbox.addWidget(self.lframe)

#
#     Status bar
#
      self.statusbar=self.statusBar()
#
#     Size policy
#
      self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
      self.show()

#
#  queued signal emit für die Anzeige der Statusmeldung
#
   def emit_message(self,s):
      self.sig_show_message.emit(s)

#
#  queued signal emit um einen Crash anzuzeigen
#
   def emit_crash(self):
      self.sig_crash.emit()
#
#  close event abfangen
#
   def closeEvent(self,evnt):
      evnt.accept()
      self.sig_quit.emit()

#
# Kanalkonfiguration editieren
#

class cls_KanalConfigWindow(QtWidgets.QDialog):

   def __init__(self,kanal):

      super().__init__()
      self.kanal= kanal
      self.kanalnr= self.kanal.kanalnummer
      self.geprueft= False
      self.config= { 'AKTyp' : self.kanal.AKTyp, 'AnzZellen' : self.kanal.AnzZellen, 'CNenn' :  self.kanal.CNenn, 'ILad' : self.kanal.ILad, 'IEntl': self.kanal.IEntl, 'Beschreibung': self.kanal.Beschreibung }

      self.setWindowTitle("Kanal Konfiguration")
      self.vLayout0= QtWidgets.QVBoxLayout()
      self.setLayout(self.vLayout0)
      self.vLayout0.setContentsMargins(20,20,20,20)
#
#     Styles
#
      self.setStyleSheet("""
         .QPushButton {
         width: 90px;
         }
         .QLineEdit {
         width: 150px;
         }
         .QSpinBox {
         width: 150px;
         }
         .QComboBox {
         width: 150px;
         }
      """)
#
#     Titel
#
      self.lbl_titel = QtWidgets.QLabel ("Konfiguration für Kanal "+str(self.kanalnr))
      self.lbl_titel.setFont(FONT_BOLD)
      self.vLayout0.addWidget(self.lbl_titel)
      self.vLayout0.setAlignment(self.lbl_titel,QtCore.Qt.AlignTop)
#
#     Grid mit den Konfigurationsparametern
#
      self.hLayout1=QtWidgets.QHBoxLayout()
      self.hLayout1.setContentsMargins(0,20,0,20)
      self.vLayout0.addLayout(self.hLayout1)
      self.vLayout0.setAlignment(self.vLayout0,QtCore.Qt.AlignTop)
      
      self.gridLayout2= QtWidgets.QGridLayout()
      self.hLayout1.addLayout(self.gridLayout2)
      self.gridLayout2.setSpacing(10)
      self.gridLayout2.addWidget(QtWidgets.QLabel("Akkutyp"),1,0)
      self.gridLayout2.addWidget(QtWidgets.QLabel("Zellenzahl"),2,0)
      self.gridLayout2.addWidget(QtWidgets.QLabel("Nennspannung (V)"),3,0)
      self.gridLayout2.addWidget(QtWidgets.QLabel("Nennkapazität (Ah)"),4,0)
      self.gridLayout2.addWidget(QtWidgets.QLabel("Ladestrom (A)"),5,0)
      self.gridLayout2.addWidget(QtWidgets.QLabel("Entladestrom (A)"),6,0)

      self.comboBox_akkutyp = QtWidgets.QComboBox()
      self.gridLayout2.addWidget(self.comboBox_akkutyp,1,1)

      self.spinBox_Zellenzahl = QtWidgets.QSpinBox()
      self.gridLayout2.addWidget(self.spinBox_Zellenzahl,2,1)

      self.lineEdit_Nennspannung = QtWidgets.QLineEdit()
      self.lineEdit_Nennspannung.setEnabled(False)
      self.gridLayout2.addWidget(self.lineEdit_Nennspannung,3,1)

      self.lineEdit_Nennkapazitaet = QtWidgets.QLineEdit()
      self.gridLayout2.addWidget(self.lineEdit_Nennkapazitaet,4,1)

      self.lineEdit_Ladestrom = QtWidgets.QLineEdit()
      self.gridLayout2.addWidget(self.lineEdit_Ladestrom,5,1)

      self.lineEdit_Entladestrom = QtWidgets.QLineEdit()
      self.gridLayout2.addWidget(self.lineEdit_Entladestrom,6,1)

#
#     Buttown Spalte
#

      self.vLayout3= QtWidgets.QVBoxLayout()
      self.vLayout3.setContentsMargins(20,0,0,0)
      self.hLayout1.addLayout(self.vLayout3)

      self.button_Neu = QtWidgets.QPushButton("Neu")
      self.button_Neu.setAutoDefault(False)
      self.vLayout3.addWidget(self.button_Neu)

      self.button_Laden = QtWidgets.QPushButton("Laden")
      self.button_Laden.setAutoDefault(False)
      self.vLayout3.addWidget(self.button_Laden)

      self.button_Pruefen = QtWidgets.QPushButton("Prüfen")
      self.button_Pruefen.setAutoDefault(False)
      self.vLayout3.addWidget(self.button_Pruefen)

      self.button_Speichern = QtWidgets.QPushButton("Speichern")
      self.button_Speichern.setAutoDefault(False)
      self.vLayout3.addWidget(self.button_Speichern)

      self.button_Programmieren = QtWidgets.QPushButton("Programmieren")
      self.button_Programmieren.setAutoDefault(False)
      self.vLayout3.addWidget(self.button_Programmieren)


      self.button_Abbruch = QtWidgets.QPushButton("Ende")
      self.button_Abbruch.setAutoDefault(False)
      self.vLayout3.addWidget(self.button_Abbruch)

      self.button_Neu.clicked.connect(self.do_neu)
      self.button_Laden.clicked.connect(self.do_laden)
      self.button_Pruefen.clicked.connect(self.do_pruefen)
      self.button_Speichern.clicked.connect(self.do_speichern)
      self.button_Programmieren.clicked.connect(self.do_programmieren)
      self.button_Abbruch.clicked.connect(self.do_exit)
      self.spinBox_Zellenzahl.setMinimum(1)
      self.spinBox_Zellenzahl.valueChanged.connect(self.do_spinBox_changed)
#
###
      self.UNenn= dict_akku_spannung[self.config['AKTyp']]* self.config['AnzZellen']
      self.comboBox_akkutyp.addItem("NiCd/NiMh")
      self.comboBox_akkutyp.addItem("Blei")
      self.comboBox_akkutyp.activated.connect(self.do_comboBox_akkutyp)

      self.lineEdit_Nennkapazitaet.setInputMask("00.00")
      self.lineEdit_Nennkapazitaet.editingFinished.connect(self.do_lineEdit_Nennkapazitaet)

      self.lineEdit_Ladestrom.setInputMask("0.00")
      self.lineEdit_Ladestrom.editingFinished.connect(self.do_lineEdit_Ladestrom)

      self.lineEdit_Entladestrom.setInputMask("0.00")
      self.lineEdit_Entladestrom.editingFinished.connect(self.do_lineEdit_Entladestrom)

      self.update_gui()
#
#  Action-Script: Spin Box Anzahl Zellen geändert ---
#
   def do_spinBox_changed(self):
      self.geprueft= False
      self.config['AnzZellen']= int(self.spinBox_Zellenzahl.value())
      self.update_gui()

#
#  Action-Script: ComboBox Akkutyp geändert ---
#
   def do_comboBox_akkutyp(self,text):
      self.geprueft= False
      if text == 1:
         self.config['AKTyp']= AKKU_TYP_BLEI
      else:
         self.config['AKTyp']= AKKU_TYP_NICD_NIMH
      self.update_gui()

#
#  Action-Script: Feld Nennkapazität geändert ---
#
   def do_lineEdit_Nennkapazitaet(self):
      self.geprueft= False
      try:
         wert=float(self.lineEdit_Nennkapazitaet.text())
      except ValueError:
         pass
      else:
         self.config['CNenn']=wert
      finally:
         self.update_gui()
#
#  Action-Script: Feld Ladestrom geändert ---
#
   def do_lineEdit_Ladestrom(self):
      self.geprueft= False
      try:
         wert=float(self.lineEdit_Ladestrom.text())
      except ValueError:
         pass
      else:
         self.config['ILad']=wert
      finally:
         self.update_gui()
#
#  Action-Script: Feld Entladestrom geändert ---
#
   def do_lineEdit_Entladestrom(self):
      self.geprueft= False
      try:
         wert=float(self.lineEdit_Entladestrom.text())
      except ValueError:
         pass
      else:
         self.config['IEntl']=wert
      finally:
         self.update_gui()
#
#  Action Script: Feld Beschreibung geändert ---
#
   def do_lineEdit_Beschreibung(self):
      self.config['Beschreibung']=self.lineEdit_Beschreibung.text()
      self.update_gui()

#
# GUI-Script: Felder aktualisieren ---
#
   def update_gui(self):
      if self.config['AKTyp'] == AKKU_TYP_BLEI:
         self.comboBox_akkutyp.setCurrentIndex(1)
##
         if self.kanalnr <= KANAL2:
            self.spinBox_Zellenzahl.setMaximum(12)
         else:
            self.spinBox_Zellenzahl.setMaximum(6)
      else:
         self.comboBox_akkutyp.setCurrentIndex(0)
##
         if self.kanalnr <= KANAL2:
            self.spinBox_Zellenzahl.setMaximum(20)
         else:
            self.spinBox_Zellenzahl.setMaximum(10)
      if self.config['AnzZellen']== 0:
         self.config['AnzZellen']== 1
##
      self.UNenn=dict_akku_spannung[self.config['AKTyp']]* self.config['AnzZellen']
      self.lineEdit_Nennspannung.setText("%4.1f" % self.UNenn)
      self.lineEdit_Nennkapazitaet.setText("%5.3f" % self.config['CNenn'])
      self.lineEdit_Ladestrom.setText("%5.3f" % self.config['ILad'])
      self.lineEdit_Entladestrom.setText("%5.3f" % self.config['IEntl'])
      self.spinBox_Zellenzahl.setValue(self.config['AnzZellen'])
      self.lbl_titel.setText("Konfiguration für Kanal %d" % self.kanalnr)
      if self.geprueft :
         self.button_Programmieren.setEnabled(True)
      else:
         self.button_Programmieren.setEnabled(False)
#
#  Action Script: Fenster schließen ---
#
   def do_exit(self):
      self.config= None
      self.close()
#
#  Action-Script: Neue Konfiguration initialisieren ---
#
   def do_neu(self):
      self.config= { 'AKTyp' :AKKU_TYP_NICD_NIMH, 'AnzZellen' : 1, 'CNenn' :  0, 'ILad' : 0, 'IEntl': 0, 'Beschreibung': "" }
      self.UNenn= dict_akku_spannung[self.config['AKTyp']]* self.config['AnzZellen']
      self.geprueft= False
      self.update_gui()
#
# Action-Script: Kanalkonfiguration von Datei laden ---
#
   def getKanalConfigInputFileName(self):
      dialog=QtWidgets.QFileDialog()
      dialog.setWindowTitle("pyALC7T Kanalkonfigurationsdatei")
      dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
      dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
      dialog.setNameFilters(["Kanalkonfiguration (*.alc)"])
      dialog.setOptions(QtWidgets.QFileDialog.DontUseNativeDialog)
      if dialog.exec():
         return dialog.selectedFiles()

   def do_laden(self):
      self.geprueft= False
      flist= self.getKanalConfigInputFileName()
      if  flist == None:
         return
      s=flist[0]
      f= None
      try:
         f= open(s,"r")
         self.config= json.load(f)
      except json.JSONDecodeError as e:
         reply=QtWidgets.QMessageBox.critical(self,'Fehler',"Kanalkonfiguration kann nicht dekodiert werden. "+e.msg,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
      except OSError as e:
         reply=QtWidgets.QMessageBox.critical(self,'Fehler',"Kanalkonfiguration kann nicht geladen werden. "+e.strerror,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
      finally:
         if f is not None:
            f.close()
      self.update_gui()
#
#  Action-Script: Plausibilitätsprüfungen ---
#
   def do_pruefen(self):
      meldungen=""
#
#     Kapazität, Lade und Entladestrom muessen größer als 0.01 sein
#
      if self.config['ILad'] < 0.01:
         meldungen=meldungen+"Ladestrom < 0.01, Wert wurde korrigiert.\n"
         self.config['ILad']= 0.01

      if self.config['IEntl'] < 0.01:
         meldungen=meldungen+"Entladestrom < 0.01, Wert wurde korrigiert.\n"
         self.config['IEntl']= 0.01

      if self.config['CNenn'] < 0.01:
         meldungen=meldungen+"Nennkapazität < 0.01, Wert wurde korrigiert.\n"
         self.config['CNenn']= 0.01
#
#     Ladestrom maximal doppelte Nennkapazität
#
      if self.config['ILad'] > self.config['CNenn']*2 :
         meldungen=meldungen+"Ladestrom höher als doppelte Nennkapazität. Wert wurde korrigiert\n"
         self.config['ILad']= self.config['CNenn']*2
#
#     Zellenzahl an gemessene Spannung anpassen
#
      if self.config['AKTyp']== AKKU_TYP_BLEI:
         MaxZellenspannung=2.4
      else:
         MaxZellenspannung=1.6
      if self.kanal.UMess > MaxZellenspannung* self.config['AnzZellen']:
         self.config['AnzZellen']= self.kanal.UMess* (MaxZellenspannung - 0.4)
         meldungen=meldungen+"Akkuspannung zu hoch. Anzahl Zellen wurde korrigiert\n"
#
#     Ladestrom Kanal 1, Kanal 2 maximal je 28.8 Watt bzw. 3.5 A
#
      if self.kanalnr == KANAL1 or self.kanalnr == KANAL2:
         if self.UNenn > 0:
            IMax= (28.8 / self.UNenn) + 0.0004
            if IMax > 3.5:
               IMax = 3.5 
            if self.config['ILad']> IMax:
               self.config['ILad']= IMax
               meldungen=meldungen+"Ladestrom größer %4.2f A. Wert wurde korrigiert\n" % IMax
            if self.config['IEntl']> IMax:
               self.config['IEntl']= IMax
               meldungen=meldungen+"Entladestrom größer %4.2f A. Wert wurde korrigiert\n" % IMax
#
#      Ladestrom Kanal 3 oder Kanal 4 darf jeweils 1 A nicht überschreiten
#
      if self.kanalnr == KANAL3 or self.kanalnr == KANAL4:
         if self.config['ILad'] > 1.004:
            self.config['ILad']=1
            meldungen=meldungen+"Ladestrom größer 1 A. Wert wurde korrigiert\n"
         if self.config['IEntl'] > 1.004:
            self.config['IEntl']=1
            meldungen=meldungen+"Entladestrom größer 1 A. Wert wurde korrigiert\n"

#
#     Meldungen anzeigen
#
      if not meldungen == "" :
         mb = cls_AlcMessageBox()
         mb.setText("Fehler bei der Prüfung")
         mb.setDetailedText(meldungen)
         mb.exec()
      else:
         self.geprueft= True
      self.update_gui()
#
# Action Script: Kanalkonfiguration in Datei speichern ---
#
   def getKanalConfigOutputFileName(self):
      dialog=QtWidgets.QFileDialog()
      dialog.setWindowTitle("pyALC7T Kanalkonfigurationsdatei")
      dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
      dialog.setDefaultSuffix(".alc")
      dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
      dialog.setNameFilters(["Kanalkonfiguration (*.alc)"])
      dialog.setOptions(QtWidgets.QFileDialog.DontUseNativeDialog)
      if dialog.exec():
         return dialog.selectedFiles()

   def do_speichern(self):
      flist= self.getKanalConfigOutputFileName()
      if flist== None:
         return
      s=flist[0]
      if os.access(s,os.W_OK):
         reply=QtWidgets.QMessageBox.warning(self,'Warnung',"Möchten Sie folgende Datei überschfreiben: "+s,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Cancel)
         if reply== QtWidgets.QMessageBox.Cancel:
            return
      f= None
      try:
         f= open(s,"w")
         json.dump(self.config,f,sort_keys=True,indent=3)
      except json.JSONDecodeError as e:
         reply=QtWidgets.QMessageBox.critical(self,'Fehler',"Kanalkonfiguration kann nicht in JSON umgewandelt werden."+e.msg,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
      except OSError as e:
         reply=QtWidgets.QMessageBox.critical(self,'Fehler',"Kanalkonfiguration kann nicht gespeichert werden."+e.strerror,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
      finally:
         if f is not None:
            f.close()

#
# Action-Script: Konfiguration programmieren ---
#
   def do_programmieren(self):
      g=QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
      self.kanal.AKTyp= self.config['AKTyp']
      self.kanal.AnzZellen= self.config['AnzZellen']
      self.kanal.CNenn=self.config['CNenn']
      self.kanal.ILad= self.config['ILad']
      self.kanal.IEntl= self.config['IEntl']
      try:
         self.kanal.kanal_programmieren(self.config)
         g=QtWidgets.QApplication.restoreOverrideCursor()
      except KanalError as e:
         g=QtWidgets.QApplication.restoreOverrideCursor()
         reply=QtWidgets.QMessageBox.critical(self,'Fehler',"Kanalkonfiguration kann nicht eingestellt werden. "+e.msg,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)

   @staticmethod
   def getKanalConfig(kanal):
      dialog=  cls_KanalConfigWindow(kanal)
      result= dialog.exec()
      return
#
# GUI Klasse Fehlermeldung -----------------------------------------------------------
#
class cls_AlcMessageBox(QtWidgets.QMessageBox):
   def __init__(self):
      QtWidgets.QMessageBox.__init__(self)
      self.setSizeGripEnabled(True)

   def event(self, e):
      result = QtWidgets.QMessageBox.event(self, e)

      self.setMinimumHeight(0)
      self.setMaximumHeight(16777215)
      self.setMinimumWidth(0)
      self.setMaximumWidth(16777215)
      self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

      textEdit = self.findChild(QtWidgets.QTextEdit)
      if textEdit != None :
         textEdit.setMinimumHeight(0)
         textEdit.setMaximumHeight(16777215)
         textEdit.setMinimumWidth(0)
         textEdit.setMaximumWidth(16777215)
         textEdit.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

      return result

