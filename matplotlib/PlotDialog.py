#
# GUI-Klasse Messwert/Plotfenster ---------------------------------------------
#

from PyQt4 import QtCore, QtGui
from pyqtgraph import GraphicsLayoutWidget
import os,time
import pyqtgraph as pg
import numpy as np

class cls_PlotDialog(QtGui.QDialog):

   def __init__(self,kanal, kanalnummer,parent=None):
      QtGui.QDialog.__init__(self,None)
      self.resize(700, 500)
      self.vlayout=QtGui.QVBoxLayout()
      self.vlayout.setMargin(20)
      self.vlayout.setSpacing(20)
      self.setLayout(self.vlayout)

      font = QtGui.QFont()
      font.setPointSize(14)
      self.label_Titel = QtGui.QLabel(self)
      self.label_Titel.setFont(font)
      self.label_Titel.setText("")
      self.label_Titel.setAlignment(QtCore.Qt.AlignCenter)
      self.vlayout.addWidget(self.label_Titel)

      self.hlayout=QtGui.QHBoxLayout()
      self.tableWidget_Messwerte = QtGui.QTableWidget(self)
      self.tableWidget_Messwerte.setColumnCount(0)
      self.tableWidget_Messwerte.setRowCount(0)
      self.hlayout.addWidget(self.tableWidget_Messwerte)

      self.plotView = GraphicsLayoutWidget(self)
      self.hlayout.addWidget(self.plotView)
      self.vlayout.addLayout(self.hlayout)
      self.hlayout2=QtGui.QHBoxLayout()

      self.button_Beenden = QtGui.QPushButton()
      self.button_Beenden.setText("Beenden")
      self.button_Beenden.setFixedWidth(80)

      self.hlayout2.addWidget(self.button_Beenden)
      self.vlayout.addLayout(self.hlayout2)

 
      self.kanalnr=kanalnummer
      self.kanal=kanal
      self.starttime=0
      self.anzmess=0
      self.fromfile= False
      self.messwertdatei="0_kanal%d.amw" % self.kanalnr

      self.button_Beenden.clicked.connect(self.do_exit)
      self.label_Titel.setText("Messwerte für Kanal "+str(self.kanalnr))
      self.tableWidget_Messwerte.setColumnCount(3)
      self.tableWidget_Messwerte.setColumnWidth(0,72)
      self.tableWidget_Messwerte.setColumnWidth(1,80)
      self.tableWidget_Messwerte.setColumnWidth(2,80)
      self.tableWidget_Messwerte.setFixedWidth(254)
      self.tableWidget_Messwerte.setHorizontalHeaderLabels(('Zeit','Spannung','Strom'))
      self.tableWidget_Messwerte.setShowGrid(True)
      self.tableWidget_Messwerte.verticalHeader().setVisible(False)

      pg.setConfigOptions(antialias=True)

      self.p1=self.plotView.addPlot()
      self.p1.setLabel('bottom','Zeit (s)')
      self.p1.setLabel('left','Spannung (V)')
      self.plotView.nextRow()
      self.p2=self.plotView.addPlot()
      self.p2.setLabel('bottom','Zeit (s)')
      self.p2.setLabel('left','Strom (A)')

      self.timer = QtCore.QTimer()
      self.timer.timeout.connect(self.refresh)

#
#  Timer aktivieren für den Refresh von Messwertanzeige und Plot
#
   def start_timer(self):
      self.timer.start(5000)

#
#  Messwerte anzeigen, Plot erstellen
#
   def refresh(self):
      try:
         status=self.kanal.GetStatus()
         if status['Aufz'] :
            if self.fromfile:
               self.p1.clear()
               self.p2.clear()
               self.fromfile= False
            entries= self.kanal.GetMesswertArray()
            l=len(entries)
            t=self.kanal.GetStarttime()
            if t == self.starttime and l == self.anzmess:
               return
            self.starttime=t
            self.anzmess=l
         else:
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
         reply=QtGui.QMessageBox.critical(self,'Fehler',"Zugriff auf Messwertdatei fehlgeschlagen. "+e.strerror,QtGui.QMessageBox.Ok,QtGui.QMessageBox.Ok)
         self.do_exit()

      self.tableWidget_Messwerte.setRowCount(len(entries))

      for i, row in enumerate(entries):
         for j, col in enumerate(row):
            item=QtGui.QTableWidgetItem(col)
            item.setFlags(QtCore.Qt.NoItemFlags)
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tableWidget_Messwerte.setItem(i,j,item)

      self.label_Titel.setText("%d Messwerte für Kanal %d" % (len(entries),self.kanalnr))
      if len(entries) < 3 :
         return
      t=np.array([])
      v=np.array([])
      a=np.array([])
      for i, row in enumerate (entries):
         t=np.append(t,[float(row[0])])
         v=np.append(v,[float(row[1])])
         a=np.append(a,[float(row[2])])
      self.p1.plot(t,v,pen=(255,0,0))
      self.p2.plot(t,a,pen=(255,255,0))
#
#  Action Script: Fenster schließen ---
#
   def do_exit(self):
      self.timer.stop()
      self.close()

