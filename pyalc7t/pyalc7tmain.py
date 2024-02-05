#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pyalc7t 1.0.0
#
# Steuerprogramm und Datenlogger für das Ladegerät ALC 7000 von ELV-Elektronik
# Das Kommunikationsprotokoll und die Messwertverarbeitung wurden aus dem
# Programm alc7t.bas von Frank Steinberg (www.FrankSteinberg.de) entnommen.
# (c) Frank Steinberg 2006
# (c) Joachim Siebold 2017
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
# Hauptprogramm -----------------------------------------------------------
#
# Changelog
# 06.02.17
# - erste Version
# 22.04.2017 jsi
# - Fehlermeldungen verbessert
# 14.05.2017 jsi
# - Fehlermeldungen eingedeutscht
# 28.05.2017 jsi
# - Diagrammgröße konfigurierbar
# 21.06.2017 jsi
# - negative Fensterpositionen werden auf 0 gesetzt
# 30.6.2017 jsi
# - minimale Fensterposition (50,50)
# 06.11.2018 jsi
# - Konfigurationsparameter delay eingeführt
# 30.11.2022 jsi
# - PySide6 Migration
# 05.02.2024 jsi
# - removed deprecation warnings
#
#
import os
import sys
import argparse
import signal
import traceback
from .alccore import *
if QTBINDINGS=="PySide6":
   from PySide6 import QtCore, QtWidgets
if QTBINDINGS=="PyQt5":
   from PyQt5 import QtCore, QtWidgets

from .alcrs232 import cls_rs232, Rs232Error
from .alcconfig import AlcConfigError, ALCCONFIG
from .alckanal import cls_kanal
from .alcthread import cls_AlcThread
from .alcwidgets import cls_ui, cls_AboutWindow, cls_HelpWindow, HelpError,cls_AlcConfigWindow

#
# Haupt-Objekt ALC7000 -----------------------------------------------------------
#
class cls_alc7t(QtCore.QObject):

   if QTBINDINGS=="PySide6":
      sig_show_message=QtCore.Signal(str)
      sig_crash=QtCore.Signal()
      sig_quit=QtCore.Signal()
   if QTBINDINGS=="PyQt5":
      sig_show_message=QtCore.pyqtSignal(str)
      sig_crash=QtCore.pyqtSignal()
      sig_quit=QtCore.pyqtSignal()


   def __init__(self,args):

      super().__init__()
      self.name= "pyalc7t"
      self.instance=""
      if args.instance:
         if args.instance.isalnum():
            self.instance=args.instance
      self.status= STAT_DISABLED
      self.commobject= None
      self.commthread= None
      self.helpwin= None
      self.aboutwin=None
      self.kanaele={ }
      self.message=""
      self.msgTimer= QtCore.QTimer()
      self.msgTimer.timeout.connect(self.show_refresh_message) 

#
#     Initialize Main Window, connect callbacks
#
      self.ui= cls_ui(self,VERSION)
      self.ui.actionConfig.triggered.connect(self.do_alc7tConfig)
      self.ui.actionReconnect.triggered.connect(self.do_Reconnect)
      self.ui.actionExit.triggered.connect(self.do_Exit)
      self.ui.actionAbout.triggered.connect(self.do_About)
      self.ui.actionHelp.triggered.connect(self.do_Help)

#
#     queued signal to show a status message. This is the only update of
#     the user interface that is issued by the thread process and must
#     be issued as a queued connection
#
      self.sig_show_message.connect(self.show_message, QtCore.Qt.QueuedConnection)
      self.sig_crash.connect(self.do_crash_cleanup, QtCore.Qt.QueuedConnection)
      self.sig_quit.connect(self.do_Exit, QtCore.Qt.QueuedConnection)

#
#     Default Konfiguration
#
      try:
         ALCCONFIG.open(self.name,CONFIG_VERSION,self.instance)
         ALCCONFIG.get(self.name,"tty","")
         ALCCONFIG.get(self.name,"workdir", os.path.expanduser('~'))
         ALCCONFIG.get(self.name,"gnuplot", "")
         ALCCONFIG.get(self.name,"plotsize", 400)
         ALCCONFIG.get(self.name,"version","0.0.0")
         ALCCONFIG.get(self.name,"position","")
         ALCCONFIG.get(self.name,"helpposition","")
         ALCCONFIG.get(self.name,"delay",2)
         ALCCONFIG.save()
      except AlcConfigError as e:
         reply=QtWidgets.QMessageBox.critical(self.ui,'Fehler',e.msg+': '+e.add_msg,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
         QtWidgets.QApplication.quit()
#
#     ermitteln ob wir eine Version von alc7t erstmalig ausführen
#
      oldversion=encode_version(ALCCONFIG.get(self.name,"version"))
      thisversion=encode_version(VERSION)
      ALCCONFIG.put(self.name,"version",VERSION)
#
#     Kanäle erzeugen
#
      
      for k in { KANAL1, KANAL2, KANAL3, KANAL4 } :
         self.kanaele[k]=cls_kanal(self,k)
#
#     Fenster an die letze gespeicherte Position verschieben
#
      position=ALCCONFIG.get(self.name,"position")
      if position !="":
         self.ui.move(QtCore.QPoint(position[0],position[1]))
#
#     GUI anzeigen
#
      self.ui.show()
      self.ui.raise_()

#
#     Gerät aktivieren
#
      self.enable()
      self.msgTimer.start(500)
#
#     wenn wir alc7t das allererste Mal ausführen, dann zeige Einführungsinfo an
#
      if ALCCONFIG.get(self.name,"position")=="":
         self.show_StartupInfo()
      else:
#
#     wenn wir eine neue Version von alc7t erstmalig ausführenn, dann zeige Releasenotes an
#
         if thisversion > oldversion:
            self.show_ReleaseInfo(VERSION)

#
#  alc7t enablen 
#
   def enable(self):
      if self.status== STAT_ENABLED:
         return
#
#     Arbeitsverzeichnis setzen
#
      try:
         os.chdir(ALCCONFIG.get(self.name,"workdir"))
      except EnvironmentError as e:
         reply=QtWidgets.QMessageBox.critical(self.ui,'Fehler',"Kann nicht auf Arbeitsverzeichnis wechseln ",QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
         return
      except TypeError as e:
         reply=QtWidgets.QMessageBox.critical(self.ui,'Fehler',"Kann nicht auf Arbeitsverzeichnis wechseln",QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
         return
#
#     Verbindung zu ALC7000 aufbauen
#
      try:
         self.commobject=cls_rs232(ALCCONFIG.get(self.name,'tty'))
         self.commobject.open()
         self.kennung= self.commobject.read_ident()
         self.version=self.commobject.read_version()
      except Rs232Error as e:
         reply=QtWidgets.QMessageBox.critical(self.ui,'Fehler',e.value,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
         return
      if not self.kennung == "ALC7000":
         reply=QtWidgets.QMessageBox.critical(self.ui,'Fehler',"Gerät nicht gefunden",QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
         return
#
#     Thread erzuegen
#
      self.commthread= cls_AlcThread(self.ui, self.kanaele)

#
#     start thread
#
      self.commthread.start()
      self.status= STAT_ENABLED
#
#   alc7t disablen
#
   def disable(self):
      if self.status== STAT_DISABLED:
         return
#
#     stop thread
#
      if self.commthread is not None:
         if self.commthread.isRunning:
            self.commthread.finish()
#
#     Kanäle disablen
#
      for k in { KANAL1, KANAL2, KANAL3, KANAL4 } :
         self.kanaele[k].disable()
#
#     Verbindung abbauen
#
      if self.commobject != None:
         try:
            self.commobject.close()
         except:
            pass
      self.commobject=None
      self.status= STAT_DISABLED
#
#     pause thread
#
   def pause_commthread(self):
      self.commthread.halt()
#
#     resume thread
#
   def resume_commthread(self):
      self.commthread.resume()
#
#     clean up from crash
#
   def do_crash_cleanup(self):
      self.commthread=None
      self.disable()
#
#     Status Meldung anzeigen
#
   def show_message(self,message):
      self.message=self.kennung+' '+self.version+': '+message
      self.ui.statusbar.showMessage(self.message)
#
#     Status Meldung aktualisieren
#
   def show_refresh_message(self):
      self.ui.statusbar.showMessage(self.message)
#
#     callback alc7t Konfiguration
#
   def do_alc7tConfig(self):
      if cls_AlcConfigWindow.getAlcConfig(self):
         self.disable()
         try:
            ALCCONFIG.save()
         except AlcConfigError as e:
            reply=QtWidgets.QMessageBox.critical(self.ui,'Fehler',e.msg+": "+e.add_msg,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
            return
         self.enable()
#
#      callback reconnect
#
   def do_Reconnect(self):
      self.disable()
      self.enable()
#
#      callback exit
#
   def do_Exit(self):
      self.disable()
      pos_x=self.ui.pos().x()
      pos_y=self.ui.pos().y()
      if pos_x < 50:
         pos_x=50
      if pos_y < 50:
         pos_y=50
      
      position=[pos_x, pos_y]
      ALCCONFIG.put(self.name,"position",position)
      if self.helpwin!= None:
         helpposition=[self.helpwin.pos().x(),self.helpwin.pos().y(),self.helpwin.width(),self.helpwin.height()]
         ALCCONFIG.put(self.name,"helpposition",helpposition)
      try:
         ALCCONFIG.save()
      except AlcConfigError as e:
         reply=QtWidgets.QMessageBox.critical(self.ui,'Fehler',e.msg+": "+e.add_msg,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
      QtWidgets.QApplication.quit()
#
#     callback show about window
#
   def do_About(self):
      if self.aboutwin== None:
         self.aboutwin= cls_AboutWindow(VERSION)
      self.aboutwin.show()
      self.aboutwin.raise_()
#
#     callback show help window
#
   def do_Help(self):
      self.show_Help("","index.html")
#
#  show release information window
#
   def show_ReleaseInfo(self, version):
      self.show_Help("","releasenotes.html")
#
#  show startup info
#
   def show_StartupInfo(self):
      self.show_Help("","startup.html")
#
#  show help windows for a certain document
#
   def show_Help(self,path,document):
      if self.helpwin == None:
         try:
            self.helpwin= cls_HelpWindow()
            self.helpwin.loadDocument(path,document)
         except HelpError as e:
            reply=QtWidgets.QMessageBox.warning(self.ui,'Warnung',e.value,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
            return
         helpposition=ALCCONFIG.get(self.name,"helpposition")
         if helpposition!= "":
            self.helpwin.move(QtCore.QPoint(helpposition[0],helpposition[1]))
            self.helpwin.resize(helpposition[2],helpposition[3])
         else:
            self.helpwin.resize(720,700)
      self.helpwin.show()
      self.helpwin.raise_()
#
# dump stack if signalled externally (for debugging)
#
def dumpstacks(signal, frame):
  for threadId, stack in sys._current_frames().items():
    print("Thread ID %x" % threadId)
    traceback.print_stack(f=stack)


#
# Hauptprogramm ---------------------------------------------------------------------
#
def main():
   parser=argparse.ArgumentParser(description='pyalc7t startup script')
   parser.add_argument('--instance', '-instance', default="", help="Start a pyalc7t instance INSTANCE")
   args=parser.parse_args()

   if not isWINDOWS():
      signal.signal(signal.SIGQUIT, dumpstacks)

   app = QtWidgets.QApplication(sys.argv)
   alc7t= cls_alc7t(args)
   sys.exit(app.exec())

if __name__ == "__main__":
   main()
