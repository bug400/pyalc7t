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
# Thread Klasse  -----------------------------------------------------------
#
# Changelog
# 06.02.2017 jsi
# - Ersterstellung
# 30.11.2022 jsi
# - PySide6 Migration
#
from .alccore import *
if QTBINDINGS=="PySide6":
   from PySide6 import QtCore, QtWidgets
if QTBINDINGS=="PyQt5":
   from PyQt5 import QtCore, QtWidgets

from .alckanal import KanalError


class cls_AlcThread(QtCore.QThread):

   def __init__(self, parent, kanaele ):
      super().__init__()
      self.parent=parent
      self.kanaele= kanaele
      self.pause= False
      self.running=True
      self.cond=QtCore.QMutex()
      self.stop=QtCore.QMutex()
      self.pauseCond=QtCore.QWaitCondition()
      self.stoppedCond=QtCore.QWaitCondition()
      self.parent.emit_message("Keine Verbindung ALC 7000")

   def isRunning(self):
      return(self.running)
#
#  Thread anhalten
#   
   def halt(self):
      if self.pause:
         return
      self.cond.lock()
      self.pause= True
      self.cond.unlock()
      self.stop.lock()
      self.stoppedCond.wait(self.stop)
      self.stop.unlock()
      self.parent.emit_message("Verbindung zu ALC 7000 angehalten")
#
#  Angehaltenen Thread weiter laufen lassen
#
   def resume(self):
      if not self.pause:
         return
      self.cond.lock()
      self.pause= False
      self.cond.unlock()
      self.pauseCond.wakeAll()
      self.parent.emit_message("Verbindung zu ALC 7000 hergestellt")
#
#  Thread beenden
#
   def finish(self):
      if not self.running:
         return
      if self.pause:
         self.terminate()
      else:
         self.cond.lock()
         self.pause= True
         self.running= False
         self.cond.unlock()
         self.stop.lock()
         self.stoppedCond.wait(self.stop)
         self.stop.unlock()

#
#  Thread Ausführung
#         
   def run(self):
#
      
      try:
         for k in self.kanaele:
            self.kanaele[k].enable()

         self.parent.emit_message("Verbindung zu ALC 7000 hergestellt")
#
#        Hauptschleife
#
         self.kanalindex= KANAL1
         while True:
            self.cond.lock()
            if(self.pause):
               self.stop.lock()
               if not self.running:
                  self.stoppedCond.wakeAll()
                  self.stop.unlock()
                  break
               self.stoppedCond.wakeAll()
               self.stop.unlock()
               self.pauseCond.wait(self.cond)
            self.cond.unlock()
#
#           Messwerte verarbeiten
#
            self.kanaele[self.kanalindex].messung()
            self.kanalindex+=1
            if self.kanalindex > KANAL4:
               self.kanalindex = KANAL1

      except KanalError as e:
         self.parent.emit_message('Fehler: '+e.msg+': '+e.add_msg)
         self.parent.emit_crash()
      else:
         self.parent.emit_message('nicht mit ALC 7000 verbunden')
