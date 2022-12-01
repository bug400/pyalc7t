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
#
# GUI-Klasse Messwert-/Plotfenster ---------------------------------------------
#
# Changelog
# 06.02.17 jsi
# - erste Version
# 20.03.17 jsi
# - tabellen/zellengröße verbessert
# 28.03.17 - jsi
# Layoutfehler beseitigt, Auffrischen Tabelle/Plot per Signal, Plotgröße konfigurierbar
# 30.11.22 jsi
# - PySide6 Migration
#
import os
import subprocess
import datetime

from .alccore import *
if QTBINDINGS=="PySide6":
   from PySide6 import QtCore, QtWidgets
if QTBINDINGS=="PyQt5":
   from PyQt5 import QtCore,  QtWidgets
from .alcconfig import ALCCONFIG


#
# Table modell für Messwerttabelle
#
class TableModel(QtGui.QStandardItemModel):
    _sort_order = QtCore.Qt.AscendingOrder

    def sortOrder(self):
        return self._sort_order

    def sort(self, column, order):
         self._sort_order = order
         super().sort(column, order)

#
# Messwert-/Plotfenster
#
class cls_PlotDialog(QtWidgets.QDialog):

   def __init__(self,kanal):
      self.gnuplot=ALCCONFIG.get("pyalc7t","gnuplot")
      self.plotsize=ALCCONFIG.get("pyalc7t","plotsize")
      super().__init__()
      self.vlayout=QtWidgets.QVBoxLayout()
      self.vlayout.setContentsMargins(20, 20, 20, 20)
      self.vlayout.setSpacing(20)
      self.setLayout(self.vlayout)
#
#     style für PushButton
#
      self.setStyleSheet("""
         .QPushButton {
         width: 90px;
         }
      """)
#
#     Titel
#
      self.label_Titel = QtWidgets.QLabel(self)
      self.label_Titel.setFont(FONT_BIG)
      self.label_Titel.setAlignment(QtCore.Qt.AlignCenter)
      self.vlayout.addWidget(self.label_Titel)
#
#     Tabelle 
#
      self.hlayout=QtWidgets.QHBoxLayout()
      self.table = QtWidgets.QTableView(self)
      self.table.setSortingEnabled(False)
      self.table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
      self.rows=0
      self.columns=3
      self.table.setFocusPolicy(QtCore.Qt.NoFocus)
      self.table.setShowGrid(False)
      self.model=TableModel(self.rows, self.columns, self.table)
#
#     Header beschriften
#
      self.model.setHeaderData(0,QtCore.Qt.Horizontal,"Zeit")
      self.model.setHeaderData(1,QtCore.Qt.Horizontal,"Spannung")
      self.model.setHeaderData(2,QtCore.Qt.Horizontal,"Strom")
      self.table.setModel(self.model)
      self.dataFont= QtGui.QFont()
      metrics= QtGui.QFontMetrics(self.dataFont)
      item_width= metrics.boundingRect(" 00:00:0000 ").width()
      self.table.horizontalHeader().setDefaultSectionSize(item_width+2)
      self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
#
#     kein Vertical Header
#
      self.table.verticalHeader().setVisible(False)
      self.table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
#
#     Zeilenhöhe anpassen
#
      item_height=metrics.height()
      self.table.verticalHeader().setDefaultSectionSize(item_height+2)
#     self.table.setFixedWidth(item_width*3)

      self.hlayout.addWidget(self.table)
#
#     Plot window
#
      if self.gnuplot != "":
         self.lblPlot = QtWidgets.QLabel(self)
         self.lblPlot.setFixedWidth(self.plotsize)
         self.hlayout.addWidget(self.lblPlot)
      self.vlayout.addLayout(self.hlayout)

      self.hlayout2=QtWidgets.QHBoxLayout()

      self.button_Beenden = QtWidgets.QPushButton()
      self.button_Beenden.setFixedWidth(60)
      self.button_Beenden.setText("OK")

      self.hlayout2.addWidget(self.button_Beenden)
      self.vlayout.addLayout(self.hlayout2)
      self.button_Beenden.clicked.connect(self.do_exit)

#
#     Variablen initialisieren
# 
      self.kanal=kanal
      self.kanalnr=kanal.kanalnummer
      self.setWindowTitle("Messwerte Kanal "+str(self.kanalnr))
      self.label_Titel.setText("Messwerte für Kanal "+str(self.kanalnr))
      self.starttime=0
      self.anzmess=0
      self.rowcount=0
      self.fromfile= False
      self.sig_refresh= kanal.sig_refresh
      self.sig_refresh.connect(self.refresh,QtCore.Qt.QueuedConnection)
#
#     Messwertdatei: Logdatei des Kanals, plotdatei: von GNUPLOT erzeugte Grafik
#
      self.messwertdatei="0_kanal%d.amw" % self.kanalnr
      self.plotdatei="0_kanal%d.png" % self.kanalnr

#
#  Signal Routine: Messwerte anzeigen, Plot erstellen
#
   def refresh(self):
      if not self.isVisible():
         return
      entries=[ ]
      try:
#
#        alte Plotdatei löschen
#
         if os.path.isfile(self.plotdatei):
            os.remove(self.plotdatei)
#
#        wir lesen die Messwerte entweder aus der laufenden Aufzeichnung ...
#
         if self.kanal.Aufz :
            if self.fromfile:
               self.fromfile= False
            entries= self.kanal.messwerte
            l=len(entries)
            t=self.kanal.TStart
            if t == self.starttime and l == self.anzmess:
               return
            self.starttime=t
            self.anzmess=l
         else:
#
#        oder aus der Logdatei
#
            if self.fromfile:
               return
            self.fromfile= True
            entries=[ ]
            if not os.path.isfile(self.messwertdatei):
               return
            f= open(self.messwertdatei,"r")
            for line in f:
               values=line.split(None)
               if values[0] == "#" :
                  continue
               entries.append(values)
            f.close()
      except EnvironmentError as e:
         reply=QtWidgets.QMessageBox.critical(self,'Fehler',"Zugriff auf Messwertdatei fehlgeschlagen. "+e.strerror,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
         self.do_exit()
#
#     Tabelle leeren, wenn befüllt
#
      if self.rowcount > 0:
         self.model.removeRows(0,self.rowcount)
         self.rowcount=0
#
#     Tabelle befüllen
#
      for i, row in enumerate(entries):
         for j, col in enumerate(row):
            if j == 0 :
               item=QtGui.QStandardItem(str(datetime.timedelta(seconds=int(col))))
            else:
               item=QtGui.QStandardItem(col)
            item.setFont(self.dataFont)
            item.setTextAlignment(QtCore.Qt.AlignLeft)
            self.model.setItem(i,j,item)
         self.rowcount+=1

      self.label_Titel.setText("%d Messwerte für Kanal %d" % (len(entries),self.kanalnr))

      if self.gnuplot == "":
         return
      if len(entries) < 4 :
         self.lblPlot.setText("Plot wird ab 4 Messwerten angezeigt")
         return
#
#     Grafikdatei mit GNUPLOT erzeugen 
#
      try:
         proc = subprocess.Popen([self.gnuplot],
                        shell=True,
                        universal_newlines=True,
                        stdin=subprocess.PIPE,
                        )
         proc.stdin.write("set term png size %d,%d\n" % (self.plotsize,self.plotsize))
         proc.stdin.write("set output \"%s\"\n" %self.plotdatei)
         proc.stdin.write("set size 1.0,0.5\n")
         proc.stdin.write("set origin 0,0.5\n")
         proc.stdin.write("set xtics font \"Arial,8\"\n")
         proc.stdin.write("set ytics font \"Arial,8\"\n")
         proc.stdin.write("set multiplot\n")
         proc.stdin.write("plot \"-\" using 1:2 title \"Spannung V\" smooth csplines\n")
         for i, row in enumerate (entries):
            proc.stdin.write("%s %s\n" % (row[0], row[1]))
         proc.stdin.write("e\n")
         proc.stdin.write("set origin 0.0,0.0\n")
         proc.stdin.write("set size 1.0,0.5\n")
         proc.stdin.write("plot \"-\" using 1:2 title \"Strom A\" smooth csplines linecolor \"green\"\n")
         for i, row in enumerate (entries):
            proc.stdin.write("%s %s\n" % (row[0], row[2]))
         proc.stdin.write("e\n")
         proc.stdin.write("unset multiplot\n")
         proc.stdin.write("quit\n")
         proc.communicate()[0]
         proc.stdin.close()

         pixmap = QtGui.QPixmap(self.plotdatei)
         self.lblPlot.setPixmap(pixmap)
         self.adjustSize()
      except EnvironmentError as e:
         reply=QtWidgets.QMessageBox.critical(self,'Fehler',"Zugriff auf Messwertdatei fehlgeschlagen. "+e.strerror,QtWidgets.QMessageBox.Ok,QtWidgets.QMessageBox.Ok)
         self.do_exit()


#
#  Action Script: Fenster schließen ---
#
   def do_exit(self):
      self.close()

