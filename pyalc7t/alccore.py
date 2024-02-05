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
# Konstanten und Hilfsfunktionen --------------------------------------------
#
# Changelog
# 05.02.17 jsi
# - erste Version
# 06.10.2018 jsi
# - Version 1.0.1
# 30.11.2018 jsi
# - PYTHON_REQUIRED_MAJOR, PYTHON_REQUIRED_MINOR eingefügt
# 24.02.2019 jsi
# - Version 1.0.2
# - Grenzwerte für max. Lade-/Entladestrom
# 24.02.2021 jsi
# - Version 1.0.3
# - Ladestrombegrenzung in den ersten 120 Sekunden des Ladevorgangs entfernt
# 30.11.2022 jsi
# - Qt Bindings ermitteln
# - Version 1.1.0
# 05.02.2024 jsi
# - Version 1.1.1
#
import platform
import sys
#
#  Plattform bestimmen
#
def isLINUX():
   return platform.system()=="Linux"
def isWINDOWS():
   return platform.system()=="Windows"
def isMACOS():
   return platform.system()=="Darwin"
#
# encode/decode version number 
#
def decode_version(version_number):
   version=str(version_number)
   major=int(version[0])
   minor=int(version[1:3])
   subversion=int(version[3:5])
   return "{:d}.{:d}.{:d}".format(major,minor,subversion)

def encode_version(version_string):
   v=version_string.split(".")
   major="".join(filter(lambda x: x.isdigit(),v[0]))
   minor="".join(filter(lambda x: x.isdigit(),v[1]))
   subversion="".join(filter(lambda x: x.isdigit(),v[2]))
   return int(major)*10000+ int(minor)*100 + int(subversion)


#
# Programmkonstanten ----------------------------------------------------------------
#
PRODUCION= True       # Production/Development Version
VERSION="1.1.1"       # pyalc7t version number
CONFIG_VERSION="1"    # Version number of alc7t config file, must be string
#
# Python minimum version
#
PYTHON_REQUIRED_MAJOR=3
PYTHON_REQUIRED_MINOR=4

#
# bei Entwicklungsversionen "(Development)" an Versionsnummer und "d" an config file anfügen
#
if not PRODUCION:
   VERSION=VERSION+" (Development)"
   CONFIG_VERSION= CONFIG_VERSION+"d"

# Programme
PROG_LADEN = 0
PROG_ENTLADEN = 1
PROG_ENTLADEN_LADEN = 2
PROG_TEST = 3
PROG_ZYKLISCH = 4
PROG_REFRESH = 5
PROG_UNKNOWN = 6
dict_programme = { PROG_LADEN : 'Laden', PROG_ENTLADEN_LADEN : 'Entl./Laden', PROG_ENTLADEN : 'Entladen', PROG_TEST : 'Test', PROG_REFRESH : 'Auffríschen', PROG_ZYKLISCH : 'Zyklisch', PROG_UNKNOWN: '----'}

# Kanäle
KANAL1 = 1
KANAL2 = 2
KANAL3 = 3
KANAL4 = 4

# Akkutypen
AKKU_TYP_NICD_NIMH = 0
AKKU_TYP_BLEI = 1
dict_akku_typ = { AKKU_TYP_NICD_NIMH: 'NiCd/NiMH', AKKU_TYP_BLEI: 'Blei'}
dict_akku_spannung = { AKKU_TYP_NICD_NIMH : 1.2, AKKU_TYP_BLEI: 2 }

# Kanalstatus
KSTAT_INAKTIV = 0
KSTAT_AKTIV = 1
KSTAT_UNKNOWN = 6
dict_kstat = { KSTAT_INAKTIV: 'inaktiv', KSTAT_AKTIV: 'aktiv', KSTAT_UNKNOWN: '-' }

# Akkustatus
AKSTAT_KEIN_AKKU = 0
AKSTAT_AKKU_ANG = 1
AKSTAT_AKKU_VOLL = 2
AKSTAT_AKKU_LEER = 3
dict_akku_status = { AKSTAT_KEIN_AKKU: 'kein Akku', AKSTAT_AKKU_ANG: 'Akku ang.', AKSTAT_AKKU_VOLL: 'Akku voll', AKSTAT_AKKU_LEER: 'Akku leer' }

# Stromrichtung
STRR_UNDEF = 0
STRR_LADEN = 1
STRR_ENTLADEN = 2
dict_strr= { STRR_UNDEF : '-', STRR_LADEN : 'laden', STRR_ENTLADEN : 'entladen' }

# Status Kanäle, Gerät
STAT_DISABLED = 0
STAT_ENABLED = 1
UMIN_INIT = 99.999

# Max Ladekapazität (120%)
CGRENZ=1.2
# Max Lade-/Entladestrom (120%)
IGRENZ=1.2
# Zeitdauer seit Beginn der Aufzeichnung, in dem die Lade-/Entladestromüberprüfung ausgesetzt wird (Sek)
TCHECKDELAY=120

class KanalError(Exception):
   def __init__(self,msg,add_msg= None):
      self.msg= msg
      self.add_msg = add_msg

#
# QT Bindings bestimmen
#
QTBINDINGS="None"
HAS_WEBENGINE=False
HAS_WEBKIT=False
# already loaded
for _b in('PyQt5','PySide6'):
   if _b+'.QtCore' in sys.modules:
      QTBINDINGS=_b
      break
else:
   try:
      import PySide6.QtCore
   except ImportError:
      if "PySide6" in sys.modules:
         del sys.modules["Pyside6"]
      try:
         import PyQt5.QtCore
      except ImportError:
         if "PyQt5" in sys.modules:
            del sys.modules["Pyside6"]
         raise ImportError("No Qt bindings found")
      else:
         QTBINDINGS="PyQt5"
         from PyQt5 import QtPrintSupport,QtGui
         QT_FORM_A4=QtPrintSupport.QPrinter.A4
         QT_FORM_LETTER=QtPrintSupport.QPrinter.Letter
         try:
            from PyQt5 import QtWebKitWidgets
            HAS_WEBKIT=True
         except:
            pass
         try:
            from PyQt5 import QtWebEngineWidgets
            HAS_WEBENGINE=True
         except:
            pass
         if HAS_WEBKIT and HAS_WEBENGINE:
           HAS_WEBENGINE=False
   else:
      QTBINDINGS="PySide6"
      from PySide6 import QtGui
      QT_FORM_A4=QtGui.QPageSize.A4
      QT_FORM_LETTER=QtGui.QPageSize.Letter
      try:
         from PySide6 import QtWebEngineWidgets
         HAS_WEBENGINE=True
      except:
         pass

#
# Fonts, wird in cls_ui initialisiert
#
FONT_NORMAL=QtGui.QFont()
FONT_BOLD=QtGui.QFont()
FONT_BOLD.setBold(True)
FONT_BIG=QtGui.QFont()
fontinfo= QtGui.QFontInfo(FONT_NORMAL)
FONT_BIG.setBold(True)
