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
# High level Klasse für Programmkonfiguration  -----------------------------
#
# Changelog
# 28.02.2017 jsi:
# - von pyILPER übernommen
# 14.05.2017 jsi:
# - Fehlermeldung eingedeutscht
#
from .userconfig import cls_userconfig, ConfigError


class AlcConfigError(Exception):
   def __init__(self,msg,add_msg= None):
      self.msg= msg
      self.add_msg = add_msg


class cls_alcconfig:
#
#  initialize: read in the configuration file into the dictionary
#  if the configuration file does not exist, an empty file is created
#
   def __init__(self):
      self.__config__= { } 
      self.__userconfig__ = None
      return

#
#  open: read in the configuration file into the dictionary
#  if the configuration file does not exist, an empty file is created
#
   def open(self,name,version,instance):
      self.__userconfig__= cls_userconfig(name,name,version,instance)
      try:
         self.__config__= self.__userconfig__.read(self.__config__)
      except ConfigError as e:
         raise AlcConfigError(e.msg,e.add_msg)
#
#  Get a key from the configuration dictionary. To initialize a key a default 
#  value can be specified
#
   def get(self,name,param,default=None):
      pname= name+"_"+param
      try:
         p= self.__config__[pname]
      except KeyError:
         if default is None:
            raise AlcConfigError("Konfigurationsparameter nicht gefunden: "+pname)
         else:
            self.__config__[pname]= default
            p=default
      return(p)
#
#  Put a key into the configuration dictrionary
#
   def put(self,name,param,value):
      pname= name+"_"+param
      self.__config__[pname]= value 
       
#
#  Save the dictionary to the configuration file
#
   def save(self):
      try:
         self.__userconfig__.write(self.__config__)
      except ConfigError as e:
         raise AlcConfigError(e.msg,e.add_msg)
#
#  Get the keys of the configuration file
#
   def getkeys(self):
      return(self.__config__.keys())
#
#  remove an entry
#
   def remove(self,key):
      try:
         del(self.__config__[key])
      except KeyError:
         pass

ALCCONFIG=  cls_alcconfig()
