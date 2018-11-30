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
# Klasse für die Kommunikation mit ALC 7000 ---------------------------------
#
# Changelog
# 06.02.17 - jsi:
# - erste Version

import serial
import time

MAX_TIMEOUT_RETRY=6
TIMEOUT=2

class Rs232Error(Exception):
   def __init__(self,value):
      self.value=value
   def __str__(self):
      return repr(self.value)
#
# RS232 Klasse -----------------------------------------------------------------
#
class cls_rs232(object):

   def __init__(self,device,parent=None):
      self.__device__= device
      self.__isOpen__= False

   def isOpen(self):
      return self.__isOpen__
#
# Kommunikation aufbauen
#
   def open(self):
      try:
         self.__ser__= serial.Serial(port=self.__device__,baudrate=9600,parity=serial.PARITY_EVEN,timeout=TIMEOUT,rtscts=False,dsrdtr=False)
         self.__isOpen__= True
         time.sleep(0.5)
      except:
          self.__device__=""
          raise Rs232Error('Kann serielle Schnittstelle '+self.__device__+' nicht öffnen')
#
#  Kommunikation abbauen
#
   def close(self):
      try:
         self.__ser__.close()
         self.__isOpen__=False
      except:
         raise Rs232Error('Kann serielle Schnittstelle nicht schließen')
      self.__device__=""
#
#  Kommunikation für das Lesen von Strings (Kommando 'V' und 'v')
#
   def __com_string__(self,befehl):
      b=bytearray(3)
      b[0]=0x02
      b[1]=ord(befehl)
      b[2]=0x03

      try:
         self.__ser__.write(b)
      except:
         raise Rs232Error('Kann nicht auf serielle Schnittstelle schreiben')
      identifier=""
      count=0
      timeout_retry=0
      while True :
         try:
            c=self.__ser__.read(1)
         except:
            raise Rs232Error('Kann nicht von serieller Schnittstelle lesen')
         if c == b'' :
            timeout_retry= timeout_retry+1
            if timeout_retry > MAX_TIMEOUT_RETRY:
               raise Rs232Error('Timeout beim Lesen von serieller Schnittstelle')
            continue
         timeout_retry=0
         if c == b'\x03' :
            break
         if(ord(c) < 32) :
            continue
         identifier+=chr(ord(c))
         count=count+1
         if count > 20:
            raise Rs232Error('Konnte keinen String von serieller Schnittstelle lesen')
      return identifier 

#
#  Encode Befehl mit den Escape Sequencen für 0x02, 0x03 und 0x05
#

   def __encode__ (self,b):
      r=bytearray()
      if b == 2 or b == 3 or b == 5 :
         r.append(0x05)
         r.append(b+0x10)
      else:
         r.append(b)
      return r
#
#  Kommunikation mit ALC 7000 für alle anderen Befehle
#
   def __com_data__ (self,befehl, kanal, param, param_len,ack):
#
#  Befehl und ggf zusätzlichen 1-Byte oder 2-Byte Parameter hinzufügen
#
      try:
         self.__ser__.flushInput()
      except:
         raise Rs232Error('Flush input auf serieller Schnittstelle fehlgeschlagen')
      kanal=kanal-1
      b=bytearray()
      s=bytearray()
      b.append(0x02)
      b.append(ord(befehl))
      b=b+self.__encode__(kanal)
      if param_len == 0 :
         b.append(0x00)
         b.append(0x00)
      if param_len == 1:
         b=b+self.__encode__(param)
         b.append(0x00)
      if param_len == 2:
         hibyte= param >> 8
         lobyte= param % 256
         b=b+self.__encode__(hibyte)
         b=b+self.__encode__(lobyte)
      b.append(0x03)
      try:
         self.__ser__.write(b)
      except:
         raise Rs232Error('Kann nicht auf serielle Schnittstelle schreiben')

#
#     Kein Rückgabewert, nur ack
#
      if ack:
         retry=0
         timeout_retry=0
         while True:
            try:
               c=self.__ser__.read(1)
            except:
               raise Rs232Error('Kann nicht von serieller Schnittstelle lesen')
            if c == b'' :
               timeout_retry=timeout_retry+1
               if timeout_retry > MAX_TIMEOUT_RETRY:
                  raise Rs232Error('Timeout beim Lesen von serieller Schnittstelle')
               continue
            timeout_retry=0
            if c == b'\x02' :
               continue
            if c == b'\x03' :
               continue
            if c == b'\x06' :
               return 
            try:
               self.__ser__.write(b)
            except:
               raise Rs232Error('Kann nicht von serieller Schnittstelle lesen')
            retry=retry+1
            if retry > 3 :
               raise Rs232Error('Befehlsübermittlung fehlgeschlagen')
         return
#
#     Rückgabewert, auf Anfangskennung warten
#

      retry=0
      timeout_retry=0
      while True:
         try:
            c=self.__ser__.read(1)
         except:
               raise Rs232Error('Kann nicht von serieller Schnittstelle lesen')
         if c == b'':
            timeout_retry=timeout_retry+1
            if timeout_retry > MAX_TIMEOUT_RETRY:
               raise Rs232Error('Timeout beim Lesen von serieller Schnittstelle')
            continue
         timeout_retry=0

         if c == b'\x02' :
            break
         retry=retry+1
         if retry > MAX_TIMEOUT_RETRY :
            raise Rs232Error('Befehlsübermittlung fehlgeschlagen')
#
#     Werte bis Endekennung lesen
#
      count=0
      timeout_retry=0
      escape= False
      while True:
         try:
            c=self.__ser__.read(1)
         except:
            raise Rs232Error('Kann nicht von serieller Schnittstelle lesen')
         if c == b'':
            timeout_retry=timeout_retry+1
            if timeout_retry > MAX_TIMEOUT_RETRY:
               raise Rs232Error('Timeout beim Lesen von serieller Schnittstelle')
            continue
         timeout_retry=0
         if escape:
            c= chr(ord(c)-0x10)
            escape = False
         if c == b'\x03' :
            break
         if c == b'\x05':
            escape= True
            continue
         s.append(ord(c)) 
         count=count+1
         if count > 6:
            raise Rs232Error('Befehlsübermittlung fehlgeschlagen')
#
#     Rückgabewerte erzeugen, 1 Byte, 2 Byte und 3* 2 Byte
#
      if count == 1:
         return(int(s[0]))
      elif count == 2:
         return(int(s[0])*256+ int(s[1]))
      elif count == 6:
         r=[]
         r.append(int(s[0])*256+ int(s[1]))
         r.append(int(s[2])*256+ int(s[3]))
         r.append(int(s[4])*256+ int(s[5]))
         return r
#
# high level funktionen
#
   def read_ident(self):
      return(self.__com_string__('v'))

   def read_version(self):
      return(self.__com_string__('V'))

   def read_Progr(self,kanal):
      return(self.__com_data__('f',kanal,0,0,0))

   def read_AnzZellen(self,kanal):
      return(self.__com_data__('u',kanal,0,0,0))

   def read_ILad(self,kanal):
      return(self.__com_data__('i',kanal,0,0,0)/1000)

   def read_IEntl(self,kanal):
      return(self.__com_data__('e',kanal,0,0,0)/1000)

   def read_CNenn(self,kanal):
      return(self.__com_data__('k',kanal,0,0,0)/100)

   def read_AKTyp(self,kanal):
      return(self.__com_data__('t',kanal,0,0,0))
      
   def read_Mess(self,kanal):
      return(self.__com_data__('w',kanal,0,0,0))
      
   def read_KanStatus(self,kanal):
      return(self.__com_data__('a',kanal,0,0,0))
      
   def read_AkStatus(self,kanal):
      return(self.__com_data__('s',kanal,0,0,0))
      
   def read_IRichtg(self,kanal):
      return(self.__com_data__('h',kanal,0,0,0))
      
   def write_Progr(self,kanal,programm):
      self.__com_data__('F',kanal,programm,1,1)

   def write_AnzZellen(self,kanal,AnzZellen):
      self.__com_data__('U',kanal,AnzZellen,1,1)

   def write_AKTyp(self,kanal,AkTyp):
      self.__com_data__('T',kanal,AkTyp,1,1)

   def write_KanAktivieren(self,kanal,aktion):
      self.__com_data__('A',kanal,aktion,1,1)

   def write_ILad(self,kanal,ILad):
      self.__com_data__('I',kanal,int(ILad*1000),2,1)

   def write_IEntl(self,kanal,IEntl):
      self.__com_data__('E',kanal,int(IEntl*1000),2,1)

   def write_CNenn(self,kanal,CNenn):
      self.__com_data__('K',kanal,int(CNenn*100),2,1)

