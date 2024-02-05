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
# Klasse für Kanäle, Messwertverarbeitung  ---------------------------------
#
# Changelog
# 08.02.2017 jsi
# - Ersterstellung
# 25.03.2017 jsi
# - Fehlermeldung Abbruch wg. geladener Kapazität verbessert
# 26.03.2017 jsi
# - Fehlerbehandlung verbessert
# 31.03.2017 jsi
# - Kanalstatus wird jetzt richtig verarbeitet
# 28.05.2017 jsi
# - Update Tabelle/Plot per Signal
# 06.11.2018 jsi
# - delay bei Messung implementiert
# 24.02.2019 jsi
# - Zwangsabschaltung falls der gemessene Lade- oder Entladestrom die
#   voreingestellten Werte um mehr als 20% übersteigt. Gilt nicht
#   für das Programm "Auffrischen".
# 30.11.2022 jsi
# - PySide6 Migration
# 05.02.2024 jsi
# - removed deprecation warnings
#

import datetime
import os
import time
from .alccore import *
if QTBINDINGS=="PySide6":
   from PySide6 import QtCore, QtWidgets
if QTBINDINGS=="PyQt5":
   from PyQt5 import QtCore,  QtWidgets

from .alcwidgets import cls_KanalWidget, cls_KanalConfigWindow, cls_AlcMessageBox
from .alcconfig import ALCCONFIG
from .alcplot import cls_PlotDialog
from .alcrs232 import Rs232Error

#
# Objektklasse für die Kanäle -----------------------------------------------------
#
class cls_kanal(QtCore.QObject):

   if QTBINDINGS=="PySide6":
      sig_refresh= QtCore.Signal()
   if QTBINDINGS=="PyQt5":
      sig_refresh= QtCore.pyqtSignal()

   def __init__(self, alc7t, kanalnr):
      super().__init__()
      self.kanalnummer = kanalnr
      self.ui= alc7t.ui
      self.alc7t= alc7t
      self.delay=0
      self.rs232=None
#
#     Menü erzeugen
#
      self.kmenu= self.ui.kmenus[self.kanalnummer]
      self.actionConfig= self.kmenu.addAction("Konfigurieren")
      self.actionConfig.triggered.connect(self.do_config_kanal)

      self.actionStart= self.kmenu.addAction("Starten")
      self.actionStart.triggered.connect(self.do_start)

      self.actionStop= self.kmenu.addAction("Beenden")
      self.actionStop.triggered.connect(self.do_stop)
      self.kmenu.addSeparator()

      self.actionCharge= self.kmenu.addAction("Laden")
      self.actionCharge.setCheckable(True)
      self.actionCharge.triggered.connect(lambda: self.do_config_program(PROG_LADEN))

      self.actionDischargeCharge= self.kmenu.addAction("Entl./Laden")
      self.actionDischargeCharge.setCheckable(True)
      self.actionDischargeCharge.triggered.connect(lambda: self.do_config_program(PROG_ENTLADEN_LADEN))

      self.actionDischarge= self.kmenu.addAction("Entladen")
      self.actionDischarge.setCheckable(True)
      self.actionDischarge.triggered.connect(lambda: self.do_config_program(PROG_ENTLADEN))

      self.actionTest= self.kmenu.addAction("Test")
      self.actionTest.setCheckable(True)
      self.actionTest.triggered.connect(lambda: self.do_config_program(PROG_TEST))
  
      self.actionRefresh= self.kmenu.addAction("Auffrischen")
      self.actionRefresh.setCheckable(True)
      self.actionRefresh.triggered.connect(lambda:self.do_config_program(PROG_REFRESH))
  
      self.actionZyklisch= self.kmenu.addAction("Zyklisch")
      self.actionZyklisch.setCheckable(True)
      self.actionZyklisch.triggered.connect(lambda: self.do_config_program(PROG_ZYKLISCH))
      self.kmenu.addSeparator()

      self.actionMeasurement= self.kmenu.addAction("Messwerte")
      self.actionMeasurement.triggered.connect(self.do_messwerte)
#
#     Kanalwidget erzeugen
#
      self.ui.hbox.addSpacing(50)
      self.kwidget= cls_KanalWidget(self.kanalnummer)
      self.ui.hbox.addWidget(self.kwidget)
      self.kwidget.reset()

#
#     Kanalkonfiguration
#
      self.Progr= PROG_UNKNOWN
      self.AnzZellen=0
      self.UNenn=0.0
      self.ILad=0.0
      self.IEntl=0.0
      self.CNenn=0.0
      self.AKTyp= AKKU_TYP_NICD_NIMH
      self.Beschreibung=""
#
#     Status
#
      self.status= STAT_DISABLED
      self.KanStatus= KSTAT_UNKNOWN
      self.AkStatus= AKSTAT_KEIN_AKKU
#
#     Log Datei
#    
      self.logfile= None
      self.logfilename="0_kanal%d.amw" % kanalnr
#
#     Messwertspeicher
#
      self.messwerte = []
      self.anz_messwerte=0
#
#     Variablen initialisieren
#
      self.reset_vars()
#
#     Menü initialisieren
#
      self.config_menu()
#
#     Messwertanzeige
# 
      self.PlotDialog= None 
#
#     Kanalmenü konfigurieren
#
   def config_menu(self):
#
#     Load/Edit/Save enablen/disablen
#
      if self.status == STAT_DISABLED or self.KanStatus== KSTAT_AKTIV:
         self.actionConfig.setEnabled(False)
         pass
      else:
         self.actionConfig.setEnabled(True)
#
#     Start/Stop disablen/enablen
#
      if self.KanStatus== KSTAT_AKTIV:
         self.actionStop.setEnabled(True)
         self.actionStart.setEnabled(False)
      else:
         if self.status == STAT_DISABLED:
            self.actionStart.setEnabled(False)
         else:
            self.actionStart.setEnabled(True)
         self.actionStop.setEnabled(False)
#
#     Programm einstellen
#
      self.actionCharge.setChecked(False)
      self.actionDischargeCharge.setChecked(False)
      self.actionDischarge.setChecked(False)
      self.actionTest.setChecked(False)
      self.actionRefresh.setChecked(False)
      self.actionZyklisch.setChecked(False)
      if self.Progr== PROG_LADEN:
         self.actionCharge.setChecked(True)
      if self.Progr== PROG_ENTLADEN_LADEN:
         self.actionDischargeCharge.setChecked(True)
      if self.Progr== PROG_ENTLADEN:
         self.actionDischarge.setChecked(True)
      if self.Progr== PROG_TEST:
         self.actionTest.setChecked(True)
      if self.Progr== PROG_ZYKLISCH:
         self.actionZyklisch.setChecked(True)
      if self.Progr== PROG_REFRESH:
         self.actionRefresh.setChecked(True)
#
#     Programmeinstellungen enablen/disablen
#
      if self.status == STAT_DISABLED or self.KanStatus == KSTAT_AKTIV:
         self.actionCharge.setEnabled(False)
         self.actionDischargeCharge.setEnabled(False)
         self.actionDischarge.setEnabled(False)
         self.actionTest.setEnabled(False)
         self.actionRefresh.setEnabled(False)
         self.actionZyklisch.setEnabled(False)
      else:
         self.actionCharge.setEnabled(True)
         self.actionDischargeCharge.setEnabled(True)
         self.actionDischarge.setEnabled(True)
         self.actionTest.setEnabled(True)
         self.actionRefresh.setEnabled(True)
         self.actionZyklisch.setEnabled(True)
#
#  Kanal enablen, Konfiguration lesen, wird vom thread aufgerufen
#
   def enable(self):
      self.reset_vars()
      self.delay= ALCCONFIG.get("pyalc7t","delay")
      self.ui.emit_message("Lese Konfiguration für Kanal "+str(self.kanalnummer))
      self.readconfig() # throws KanalError
      self.status= STAT_ENABLED
      self.config_menu()
      self.show_conf()

   def disable(self):
      self.reset_vars()
      self.kwidget.reset()
      try:
         self.close_log()
      except:
         pass
      self.status= STAT_DISABLED
      
#
#
#  Reset des Kanals, z.B. bei Neustart ---
#
   def reset_vars(self):
#
#     Messwerte vom ALC 7000
#
      self.UMess=0.0
      self.IMess=0.0
      self.CMess=0.0
      self.CMessAlt=0.0
#
#     errechnete Messwerte
#
      self.UMin= UMIN_INIT
      self.UMax=0.0
      self.DPMax=0.0
      self.DP=0.0
      self.CLad=0.0
      self.CEntl=0.0
      self.CEntlAlt=0.0
#
#     Status
#
      self.IRichtg= STRR_UNDEF
      self.IRichtgAlt = STRR_UNDEF
#
#     Ablaufkontrolle
#
      self.IStart=0.009
      self.Aufz= False
      self.CFlag = False
      self.CGrFlag= False
      self.IGrFlag= False
#
#     Zeitmessung
#
      self.DeltaTime= None
      self.DeltaTimeAlt= None
      self.TStart= None
      self.TAlt= None
#
#     Messwertspeicher
#
      self.messwerte = []
      self.anz_messwerte=0
#
#
#  Kanalkonfiguration auslesen ---
#
   def readconfig(self):
#
#     Kanalkonfiguration abfragen
#
      kanalnr= self.kanalnummer
      try:
         self.Progr= self.alc7t.commobject.read_Progr(kanalnr)
         self.AnzZellen= self.alc7t.commobject.read_AnzZellen(kanalnr)
         self.ILad= self.alc7t.commobject.read_ILad(kanalnr)
         self.IEntl= self.alc7t.commobject.read_IEntl(kanalnr)
         self.CNenn= self.alc7t.commobject.read_CNenn(kanalnr)
         self.AKTyp= self.alc7t.commobject.read_AKTyp(kanalnr)
      except Rs232Error as e:
         raise KanalError('Kann Kanalkonfiguration nicht abfragen', e.value)

      self.UNenn= dict_akku_spannung[self.AKTyp]* self.AnzZellen
      self.CLadGr= self.CNenn* CGRENZ
      self.ILadGr= self.ILad* IGRENZ
      self.IEntlGr= self.IEntl* IGRENZ

#
#     Neuberechnung des Schwellenwertes, ab dem Aufzeichnung beginnt
#
      self.IStart= self.IEntl
      if self.ILad < self.IEntl:
         self.IStart= self.ILad
      self.IStart= self.IStart / 10.0
      if self.IStart == 0:
         self.IStart= 0.009
#
#  Konfiguration anzeigen
#  
   def show_conf(self):
      self.kwidget.display_conf(dict_programme[self.Progr], dict_akku_typ[self.AKTyp],str(self.AnzZellen), "%4.1f V" % self.UNenn, "%6.3f Ah" % self.CNenn, "%5.3f A" % self.ILad, "%5.3f A" %self.IEntl, self.Beschreibung)
#
#  Messwerte anzeigen
#
   def show_mess(self):

      kanalstatus= dict_kstat[self.KanStatus]
      akkustatus= dict_akku_status[self.AkStatus]
      if self.AkStatus== AKSTAT_KEIN_AKKU:
         aufzdauer="--:--:--"
         akt_spannung="-.--- V"
         maximalspannung="-.--- V"
         minimalspannung="-.--- V"
         delta_peak="-.--- V"
         akt_strom="-.--- A"
         stromrichtung="-"
         letzte_gel_kapazitaet="-.--- A"
         letzte_entl_kapazitaet="-.--- A"
         messwertdatei="-"
      else:
         akt_spannung= "%6.3f V" % self.UMess
         maximalspannung= "%6.3f V" % self.UMax
         if self.UMin== UMIN_INIT:
            minimalspannung="-.--- V"
         else:
            minimalspannung= "%6.3f V" % self.UMin
         delta_peak= "%5.3f V" % self.DP
         akt_strom= "%5.3f A" % self.IMess
         stromrichtung= dict_strr[self.IRichtg]
         letzte_gel_kapazitaet= "%5.3f A" % self.CLad
         letzte_entl_kapazitaet= "%5.3f A" % self.CEntl
         if self.Aufz:
            messwertdatei=self.logfilename
            intervall=self.DeltaTime.total_seconds()
            hours, remainder = divmod(intervall, 3600)
            minutes, seconds = divmod(remainder, 60)
            aufzdauer= '%02d:%02d:%02d' % (hours, minutes, seconds)
         else:
            aufzdauer="--:--:--"
            messwertdatei="-"

      self.kwidget.display_mess(kanalstatus,akkustatus,aufzdauer,akt_spannung,maximalspannung,minimalspannung,delta_peak,akt_strom,stromrichtung,letzte_gel_kapazitaet,letzte_entl_kapazitaet,messwertdatei)
#
#  Messung pro Kanal ausführen und Verarbeiten ---
#
   def messung(self):
      kanalnr=self.kanalnummer
      time.sleep(self.delay)
      self.ui.emit_message("Lese Messwerte für Kanal "+str(self.kanalnummer))
      try:    
#
#        Kanal- und Akkustatus lesen
#
         oldstatus=self.KanStatus
         self.KanStatus= self.alc7t.commobject.read_KanStatus(kanalnr)
         if oldstatus != self.KanStatus:
            self.config_menu()
         self.AkStatus = self.alc7t.commobject.read_AkStatus(kanalnr)
#
#        Stromrichtung lesen
#
         self.IRichtgAlt = self.IRichtg
         self.IRichtg= self.alc7t.commobject.read_IRichtg(kanalnr)
         if self.IRichtgAlt == STRR_UNDEF:
            self.IRichtgAlt= self.IRichtg
#
#        Messwerte lesen
#
         m= self.alc7t.commobject.read_Mess(kanalnr)
         self.UMess= m[0] / 1000
         self.IMess= m[1] / 1000
         self.CMess= m[2] / 100
      except Rs232Error as e:
         raise KanalError('Kann Messwerte nicht lesen', e.value)
#
#     Min Max Spannung
#
      if self.UMess > 0.0 :
         if self.UMess < self.UMin:
            self.UMin= self.UMess
      if self.UMess > self.UMax:
         self.UMax = self.UMess
      if self.UMess > self.DPMax:
         self.DPMax= self.UMess
#
#     Aufzeichnung beginnen wenn Akku geladen wird und Strom fliesst
#
      if not self.Aufz and self.AkStatus== AKSTAT_AKKU_ANG and self.KanStatus== KSTAT_AKTIV and self.IMess > self.IStart:
         self.IMess= self.IStart
         self.TStart= datetime.datetime.now()
         self.TAlt= None
         self.DeltaTimeAlt= datetime.timedelta(hours=0)
         self.Aufz= True
#
#        Dateikopf schreiben 
#
         try:
            self.open_log()
         except EnvironmentError as e:
            raise KanalError('Kann Logdatei nicht öffnen',e.strerror)

      if not self.Aufz:
         self.show_mess()
         return
#
#     Wenn Akku geladen wird, dann Delta-Peak berechnen
#
      if self.AkStatus == AKSTAT_AKKU_ANG and  self.IRichtg == STRR_LADEN and self.UMess <= self.DPMax:
         self.DP= self.DPMax - self.UMess

#
#     Laufzeit berechnen
#
      if self.KanStatus== KSTAT_AKTIV:
         self.DeltaTime= datetime.datetime.now() - self.TStart
#
#     eingeladene bzw. entladene Kapazität berechnen
#
      Intervall= self.DeltaTime.total_seconds() - self.DeltaTimeAlt.total_seconds()
      if self.IRichtg== STRR_ENTLADEN:
         self.CEntl= self.CEntl+ self.IMess* Intervall/3600 * 0.975
      if self.IRichtg== STRR_LADEN:
         self.CLad= self.CLad + self.IMess * Intervall/3600 * 0.975
      self.DeltaTimeAlt= self.DeltaTime
#
#     wenn Entladekapazität vom ALC7000 gelöscht wird (bei Überhitzung), dann soll die
#     berechnete Kapazität verwendet werden
#
      if self.IRichtg == STRR_ENTLADEN:
         if self.CMess < self.CMessAlt:
            self.CFlag= True
         self.CMessAlt= self.CMess

      if self.CFlag:
         self.CMess= self.CEntl
#
#     Lade- oder Entladestrom zu hoch (mehr als IGRENZ%)
#
      if self.Progr != PROG_REFRESH:
          Laufzeit= int(self.DeltaTime.total_seconds())
          if ((self.IRichtg== STRR_LADEN and (self.IMess > self.ILadGr)) or (self.IRichtg==STRR_ENTLADEN and (self.IMess > self.IEntlGr))) and Laufzeit > TCHECKDELAY:
            if (self.IRichtg== STRR_LADEN):
               self.write_log_msg("Ladestrom überschritten %1.3f A (Grenzwert %1.3f A)" % (self.IMess, self.ILadGr) )
            else:
               self.write_log_msg("Entladestrom überschritten %1.3f A (Grenzwert %1.3f A)" % (self.IMess, self.IEntldGr) )
            try:
               self.alc7t.commobject.write_KanAktivieren(kanalnr,KSTAT_INAKTIV)
               self.KanStatus= self.alc7t.commobject.read_KanStatus(kanalnr)

            except Rs232Error as e:
               raise KanalError('Kann Kanal nicht deaktivieren',e.value)

            self.IGrFlag= True
            self.AkStatus= AKSTAT_AKKU_VOLL

#
#     Kapazitätsgrenze überschritten?
#
      if self.IRichtg== STRR_LADEN and self.Progr != PROG_REFRESH and self.CLad > self.CLadGr:
         self.write_log_msg("Kapazitätsgrenze überschritten %6.3f Ah (Grenzwert %5.3f Ah)" % (self.CLad, self.CLadGr) )
         try:
            self.alc7t.commobject.write_KanAktivieren(kanalnr,KSTAT_INAKTIV)
            self.KanStatus= self.alc7t.commobject.read_KanStatus(kanalnr)

         except Rs232Error as e:
            raise KanalError('Kann Kanal nicht deaktivieren',e.value)

         self.CGrFlag= True
         self.AkStatus= AKSTAT_AKKU_VOLL
#
#        Änderung der Stromrichtung
#
      if self.IRichtg != self.IRichtgAlt:
         if self.IRichtgAlt== STRR_LADEN:
            self.CEntl= 0
            self.CEntlAlt=0
            self.CFlag= False
#
#           Ausgabe in Datei 
#
            try:
               self.write_log_msg("Umgeschaltet auf Entladen - geladene Kapazität %6.3f Ah - Delta-Peak %5.3f V" % (self.CLad, self.DP) )
            except EnvironmentError as e:
               raise KanalError('Kann nicht auf Logdatei schreiben',e.strerror)

         if self.IRichtgAlt== STRR_ENTLADEN:
            self.CLad=0
            self.DP=0
            self.DPMax=0
#
#           Ausgabe in Datei 
#
            try:
               self.write_log_msg("Umgeschaltet auf Laden - entladene Kapazität %6.3f Ah" % self.CMess)
            except EnvironmentError as e:
               raise KanalError('Kann nicht auf Logdatei schreiben',e.strerror)

      if self.IRichtg == self.IRichtgAlt and self.AkStatus == AKSTAT_AKKU_ANG:
#
#        Ausgabe in Datei
#
         try:
            self.write_log_mess()
         except EnvironmentError as e:
            raise KanalError('Kann nicht auf Logdatei schreiben',e.strerror)

      self.show_mess()
      self.sig_refresh.emit()
#
#        Messprogrammende, Dateien schliessen
#
      if self.AkStatus > AKSTAT_AKKU_ANG or self.KanStatus == KSTAT_INAKTIV:
         try:
            self.close_log()
         except EnvironmentError as e:
            raise KanalError('Kann Logdatei nicht abschließen',e.strerror)

         self.Aufz= False        
#
#  Alte Logdateien sichern, neue Datei öffnen und Header schreiben ---
#  Fehlerbehandlung in Methode messung
#
   def open_log(self):
      kanalnr= self.kanalnummer
      if os.path.isfile(self.logfilename):
         j=3
         while True:
            name_old= "%d_kanal%d.amw" % (j, kanalnr)
            name_new= "%d_kanal%d.amw" % (j-1,kanalnr)
            if os.path.isfile(name_old):
               os.remove(name_old)
            if os.path.isfile(name_new):
               os.rename(name_new, name_old)
            j=j-1
            if j == 0 :
               break
      self.logfile=open(self.logfilename,"w")
      l= self.logfile
      dt=datetime.datetime.now()
      time=dt.strftime("%H:%M:%S")
      date=dt.strftime("%d-%m-%Y")
      try:
         l.write("# Messdatendatei des Programms pyalc7t angelegt "+date+" "+time+"\n")
         l.write("#\n")
         l.write("# Konfiguration des Kanals\n")
         l.write("#\n")
         l.write("# Einstellungen beim Start der Aufzeichnung:\n")
         l.write("# Kanal:         %6d         Programm:     %s\n" % (kanalnr, dict_programme[self.Progr]))
         l.write("# Zellenzahl:    %6d         Akkutyp:      %s\n" % (self.AnzZellen, dict_akku_typ[self.AKTyp]))
         l.write("# Nennspannung:  %6.2f V     Ladestrom:    %5.3f A\n" % (self.UNenn, self.ILad))
         l.write("# Nennkapazität: %6.3f Ah    Entladestrom: %5.3f A\n" % (self.CNenn, self.IEntl))
         l.write("#\n")
         l.write("# Messwerte\n")
         l.write("# Zeit [Sek] Spannung [V] Strom [A]\n")
      except EnvironmentError:
         l.close()
         raise
        
#
#  Messwerte in Logdatei schreiben und in Messwertspeicher für Messw.fenster ---
#  Fehlerbehandlung in Methode messung
#    
   def write_log_mess(self): 
      l=self.logfile
      Laufzeit= int(self.DeltaTime.total_seconds())
      try:
         l.write("  %06d        %2.3f      %1.3f\n" % ( Laufzeit, self.UMess, self.IMess ))
         l.flush()
      except EnvironmentError:
         l.close()
         raise
      self.messwerte.append(["%06d" % Laufzeit, "%6.3f" % self.UMess, "%5.3f" % self.IMess])
      self.anz_messwerte+=1

   def write_log_msg(self,msg):
      l=self.logfile
      Laufzeit= int(self.DeltaTime.total_seconds())
      try:
         l.write("# %06d %s\n" % (Laufzeit, msg))
         l.flush()
      except EnvironmentError:
         l.close()
         raise
#
#  Log Datei schließen, Trailer schreiben ---
#  Fehlerbehandlung in Methode messung
#
   def close_log(self):
      l=self.logfile
      try:
         if l is None:
            return
         if self.CGrFlag:
            self.write_log_msg("Abbruch: Ladekapazitätsgrenzwert (%6.3f Ah) erreicht." % self.CLadGr)
         elif self.IGrFlag:
            self.write_log_msg("Abbruch: Lade-/Entladestrom zu groß (%6.3f Ah) erreicht." % self.IMess)
         else:
            l.write("#\n")
            l.write("# Programmende\n")
            l.write("# Zuletzt geladen:     %6.3f Ah\n" % self.CLad)
            l.write("# Zuletzt entladen:    %6.3f Ah\n" % self.CEntl)
            l.write("# Maximalspannung:     %6.3f V \n" % self.UMax)
            l.write("# Minimalspannung:     %6.3f V \n" % self.UMin)
            l.write("# Delta-Peak Spannung: %6.3f V \n" % self.DP)
      except EnvironmentError:
         l.close()
         self.logfile= None
         raise
      l.close()
      self.logfile= None
#
#  Neue Konfiguration für Kanal einstellen ---
#
   def kanal_programmieren(self, config):
      self.reset_vars()
      self.Progr= PROG_LADEN
      self.KanStatus=KSTAT_INAKTIV
      self.alc7t.commthread.halt()
#     time.sleep(0.5)
      try:
         self.alc7t.commobject.write_AKTyp(self.kanalnummer,config['AKTyp'])
#        time.sleep(0.5)
         self.alc7t.commobject.write_AnzZellen(self.kanalnummer,config['AnzZellen'])
#        time.sleep(0.5)
         self.alc7t.commobject.write_CNenn(self.kanalnummer,config['CNenn'])
#        time.sleep(0.5)
         self.alc7t.commobject.write_ILad(self.kanalnummer,config['ILad'])
#        time.sleep(0.5)
         self.alc7t.commobject.write_IEntl(self.kanalnummer,config['IEntl'])
#        time.sleep(0.5)
         self.alc7t.commobject.write_Progr(self.kanalnummer,PROG_LADEN)
#        time.sleep(0.5)
         while True:
            p= self.alc7t.commobject.read_Progr(self.kanalnummer)
            if p == PROG_LADEN:
               break
         self.readconfig() # throws KanalError
      except Rs232Error as e:
         raise KanalError("Kann neue Kanaleinstellung nicht vornehmen",e.value)
      self.show_conf()
      self.config_menu()
      self.alc7t.commthread.resume()
#
#  Kanal konfigurieren
#
   def do_config_kanal(self):
      dummy= cls_KanalConfigWindow.getKanalConfig(self)

#
#  Neues Programm für eine Kanal einstellen, Kanal bleibt inaktiv ---
#
   def do_config_program(self,programm):
      g=QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
      self.reset_vars()
      self.alc7t.commthread.halt()
      try:
         self.alc7t.commobject.write_Progr(self.kanalnummer,programm)
         while True:
            p= self.alc7t.commobject.read_Progr(self.kanalnummer)
            if p == programm:
               g=QtWidgets.QApplication.restoreOverrideCursor()
               break
      except Rs232Error as e:
         g=QtWidgets.QApplication.restoreOverrideCursor()
         self.alc7t.commthread.resume()
         reply=QtWidgets.QMessageBox.critical(self.ui,'Fehler',"Kann Ladeprogramm nicht einstellen: "+e.value,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
      self.Progr=programm
      self.show_conf()
      self.config_menu()
      self.alc7t.commthread.resume()
#
# Eingestelltes Programm des Kanals starten
#
   def do_start(self):
#
#     Plausibilitätsprüfungen  vor Programmstart durchführen
#
      meldungen=""
#
#     Ladestrom maximal doppelte Nennkapazität
#
      if self.ILad > self.CNenn*2 :
         meldungen=meldungen+"Ladestrom höher als doppelte Nennkapazität.\n"

#
#     Entspricht Zellenzahl der gemessenen Spannung 
#
      if self.AKTyp== AKKU_TYP_BLEI:
         MaxZellenspannung=2.4
      else:
         MaxZellenspannung=1.6
      if self.UMess > MaxZellenspannung* self.AnzZellen:
         meldungen=meldungen+"Akkuspannung zu hoch.\n"
#
#     Ladestrom Kanal 1, Kanal 2 maximal je 28.8 Watt bzw. 3.5 A
#
      if self.kanalnummer == KANAL1 or self.kanalnummer == KANAL2:
         if self.UNenn > 0:
            IMax= (28.8 / self.UNenn) + 0.0004
            if IMax > 3.5:
               IMax = 3.5
            if self.ILad> IMax:
               self.ILad= IMax
               meldungen=meldungen+"Ladestrom größer %4.2f A.\n" % IMax
            if self.IEntl> IMax:
               self.IEntl= IMax
               meldungen=meldungen+"Entladestrom größer %4.2f A.\n" % IMax
#
#      Ladestrom Kanal 3 oder Kanal 4 darf zusammen 1A nicht überschreiten
#
      if self.kanalnummer == KANAL3 or self.kanalnummer == KANAL4:
         if self.kanalnummer == KANAL3:
            ilad2= self.alc7t.kanaele[KANAL4].ILad
            ientl2= self.alc7t.kanaele[KANAL4].IEntl
         else:
            ilad2= self.alc7t.kanaele[KANAL3].ILad
            ientl2= self.alc7t.kanaele[KANAL3].IEntl
         if self.ILad+ilad2 > 1.004:
            meldungen=meldungen+"Ladestrom größer 1A.\n"
         if self.IEntl+ ientl2 > 1.004:
            meldungen=meldungen+"Entladestrom größer 1 A.\n"
#
#     Meldungen anzeigen, wenn Fehler vorliegt
#
      if not meldungen == "" :
         mb = cls_AlcMessageBox()
         mb.setText("Fehler bei der Prüfung")
         mb.setDetailedText(meldungen)
         mb.exec()
         return
      g=QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
      self.reset_vars()
      self.alc7t.commthread.halt()
      try:
         self.alc7t.commobject.write_KanAktivieren(self.kanalnummer,1)
         while True:
            p= self.alc7t.commobject.read_KanStatus(self.kanalnummer)
            if p == 1:
               g=QtWidgets.QApplication.restoreOverrideCursor()
               break
      except Rs232Error as e:
         g=QtWidgets.QApplication.restoreOverrideCursor()
         self.alc7t.commthread.resume()
         reply=QtWidgets.QMessageBox.critical(self.ui,'Fehler',"Kann Ladeprogramm nicht starten: "+e.value,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
         return
      self.KanStatus=p
      self.config_menu()
      self.alc7t.commthread.resume()
#
# laufendes Programm des Kanals stoppen ---
#
   def do_stop(self):
      g=QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
      self.alc7t.commthread.halt()
      try:
         self.alc7t.commobject.write_KanAktivieren(self.kanalnummer,0)
         while True:
            p= self.alc7t.commobject.read_KanStatus(self.kanalnummer)
            if p == 0:
               g=QtWidgets.QApplication.restoreOverrideCursor()
               break
      except Rs232Error as e:
         g=QtWidgets.QApplication.restoreOverrideCursor()
         self.alc7t.commthread.resume()
         reply=QtWidgets.QMessageBox.critical(self.ui,'Fehler',"Kann Ladeprogramm nicht beenden: "+e.value,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
         return
      self.KanStatus=p
      self.config_menu()
      self.alc7t.commthread.resume()
#
#  Messwertfenster für Kanal öffnen ---
#
   def do_messwerte(self):
      if self.PlotDialog== None:
         self.PlotDialog= cls_PlotDialog(self)
      self.PlotDialog.show()
      self.sig_refresh.emit()

