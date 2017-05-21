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
#
from PyQt5 import QtCore, QtGui
import platform
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
# Fonts, wird in cls_ui initialisiert
#
FONT_NORMAL= None
FONT_BOLD= None
FONT_BIG= None
FONT_NORMAL=QtGui.QFont()
FONT_BOLD=QtGui.QFont()
FONT_BOLD.setBold(True)
FONT_BIG=QtGui.QFont()
fontinfo= QtGui.QFontInfo(FONT_NORMAL)
FONT_BIG.setBold(True)

#
# Programmkonstanten ----------------------------------------------------------------
#
PRODUCION= False      # Production/Development Version
VERSION="1.0.0i~beta2"       # pyalc7t version number
CONFIG_VERSION="1"    # Version number of alc7t config file, must be string

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

class KanalError(Exception):
   def __init__(self,msg,add_msg= None):
      self.msg= msg;
      self.add_msg = add_msg

