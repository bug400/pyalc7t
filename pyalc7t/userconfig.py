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
# Low level Klasse für Programmkonfiguration --------------------------------
#
# Changelog
# 28.02.2017 jsi
# - von pyILPER übernommen
# 22.04.2017 jsi
# - Fehlermeldungen eingedeutscht

import json
import os
import platform

class ConfigError(Exception):
   def __init__(self,msg,add_msg= None):
      self.msg= msg
      self.add_msg = add_msg


class cls_userconfig:

   def __init__(self,progname,filename,version,instance):
#
#  determine config file name
#
      self.__configfilename__=filename+instance
      for i in range(0,len(version)):
         if version[i]!=".":
            self.__configfilename__+= version[i]
#
#  determine path (os dependend)
#
      self.__userhome__=os.path.expanduser("~")

      if platform.system()=="Linux":
#
#        LINUX
#        
         self.__configpath__=os.path.join(self.__userhome__,".config",progname)
      elif platform.system()=="Windows":
#
#        Windows
#
         self.__configpath__=os.path.join(os.environ['APPDATA'],progname)
      elif platform.system()=="Darwin":
#
#        Mac OS X
#
         self.__configpath__=os.path.join(self.__userhome__,"Library","Application Support",progname)
#
      else:
#
#        Fallback
#
         self.__configpath__=os.path.join(self.__userhome__,progname)

      self.__configfile__=os.path.join(self.__configpath__,self.__configfilename__)

#
#  read configuration, if no configuration exists write default configuration
#
   def read(self,default):
      f=None
      if not os.path.isfile(self.__configfile__):
         if not os.path.exists(self.__configpath__):
            try:
               os.makedirs(self.__configpath__)
            except OSError as e:
               raise ConfigError("Kann das Verzeichnis für die Konfigurationsdatei nicht anlegen", e.strerror)
         try:
            self.write(default)
         except OSError as e:
            raise ConfigError("Kann die Konfigurationsdatei nicht anlegen", e.strerror)
         return default
      try:
         f=None
         f= open(self.__configfile__,"r")
         config= json.load(f)
      except json.JSONDecodeError as e:
         raise ConfigError("Kanalkonfiguration kann nicht dekodiert werden")
      except OSError as e:
         raise ConfigError("Konfigurationsdatei kann nicht gelesen werden", e.strerror)
      finally:
         if f is not None:
            f.close()

      return config
#
#  Store configuration, create file if it does not exist
#
   def write(self,config):
      f= None
      try:
         f= open(self.__configfile__,"w")
         json.dump(config,f,sort_keys=True,indent=3)
      except json.JSONDecodeError as e:
         raise ConfigError("Kann Konfiguration nicht in JSON umwandeln")
      except OSError as e:
         raise ConfigError("Konfigurationsdatei kann nicht geschrieben werden", e.strerror)
      finally:
         if f is not None:
            f.close()

