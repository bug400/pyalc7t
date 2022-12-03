pyALC7T Installationsanleitung
==============================

Index
-----

* [Allgemeines](#allgemeines)
* [Installation mit der Anaconda Plattform](#installation-mit-der-anaconda-plattform)
* [Installation von GNUPLOT](#installation-von-gnuplot)
* [Einrichtung von pyALC7T](#einrichtung-von-pyalc7t)
* [Bedienung](#bedienung)
* [Installation ohne die ANACONDA Plattform](#installation-ohne-die-anaconda-plattform)
* [Installation mit Qt6 und PIP](#installation-mit-qt6-und-pip)
* [Installation von Entwicklungsversionen](#installation-von-entwicklungsversionen)


Allgemeines
----------

Für den Einsatz von pyALC7T müssen installiert sein:

* Python 3.4 oder neuere Versionen
* QT 5.6 oder neuere Versionen
* PyQt in einer zur Python und Qt Version kompatiblen Fassung
* die Python Bindings entweder für Qt Webkit oder Qt Webengine. Dies wird nur für
  die Anzeige des Online-Manuals benötigt.
* pyserial  2.7 
* GNUPLOT. Das Programm wird nur für die grafische Anzeige von Messwerten benötigt.

Es wird die Verwendung der [ANACONDA Plattform](https://www.continuum.io)  empfohlen um
pyALC7T und die notwendige Laufzeitumgebung zu installieren und auf aktuellem Stand
zu halten. GNUPLOT kann jedoch nicht über die ANACONDA Plattform bezogen werden.

Der Rechner muss mit einer RS232 Schnittstelle ausgestattet sein. Diese kann bei modernen
Rechnersystemen über einen USB-RS232 Adapter nachgerüstet werden. 


Installation mit der ANACONDA Plattform
---------------------------------------

Für die Installation von pyALC7T und der Python Laufzeitumgebung werden rund
700 MB freier Speicherplatz benötigt. Die Installation kann lokal erfolgen und 
benötigt dann keine Administrator Rechte.

Für die ANACONDA Plattform existiert pyALC7T nur für die Python Version 3.9.

Laden Sie [Miniconda](https://docs.conda.io/en/latest/miniconda.html) herunter und installieren Sie die Software gemäß [Installationsanleitung](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

Wenn Sie Miniconda das erste Mal installieren, dann müssen Sie das Installationsprogramm
die PATH Variable Ihrer Benutzerumgebung modifizieren lassen.

Nach der Installation von Miniconda öffnen Sie ein Terminal oder Konsole Fenster und geben:

     conda update conda
     conda config --add channels bug400
     conda install pyalc7t

ein. Dies installiert pyALC7T und alle benötigen Bestandteile der Python Laufzeitumgebung.

Um pyALC7T und die Python Laufzeitumgebung zu aktualisieren geben Sie:

     conda update --all

ein.

Sie starten pyALC7T aus einem Terminal- bzw. Konsolefenster mit:

     pyalc7t


Führen Sie ab und zu den Befehl:

     conda clean --all

um den Zwischenspeicher heruntergeladener Anaconda Softwarepakete zu löschen und
Plattenplatz frei zu geben.

pyALC7t benötigt Python 3.9. Sie können die aktuell installierte Python Version mit

     conda list

überprüfen. Wenn eine ältere Python Version installiert ist können Sie mit dem
folgenden Befehl die Version 3.9 installieren:

     conda install python=3.9


Installation von GNUPLOT
------------------------
Laden Sie GNUPLOT von der [GNUPLOT Website](http://www.gnuplot.info) herunter und
installieren das Programm gemäß Installationsanleitung.

Bei LINUX Betriebssystemen kann GNUPLOT über die dort vorhandenen Softwarepaket
Managementsysteme installiert werden.


Einrichtung von pyALC7T
-----------------------

Beim ersten Programmstart muss die korrekte serielle Schnittstelle angegeben
werden, an der das Ladegerät ALC7000 angeschlossen ist. Außerdem muss das
Arbeitsverzeichnis eingerichtet werden, in dem die Arbeits- und Logdateien von
pyALC7T abgelegt werden.  Dies geschieht über den Menüpunkt "pyALC7T Konfiguration" 
im Menü "Datei".

Bei der Eingabe der seriellen Schnittstelle versucht pyALC7T geeignete Vorschläge
für den Namen der seriellen Schnittstelle zu machen, sofern ein USB-RS232 
Adapter angeschlossen ist.

Unter LINUX ist der Name der Schnittstelle üblicherweise /dev/ttyUSBn. Überprüfen
Sie bitte, ob Sie Lese- und Schreibrechte für das Gerät haben! Bei manchen
LINUX Distributionen ist dazu die Zugehörigkeit zu einer bestimmten Benutzergruppe
erforderlich.

Unter Windows ist das Gerät COMn. Wenn Sie unsicher sind, dann überprüfen Sie bitte die
seriellen Schnittstellen im Gerätemanager.

Unter Mac OS ist der Gerätename üblicherweise /dev/tty.usbserial-XXXX.

pyALC7T speichert alle LOG-Dateien und Arbeitsdateien in einem Arbeitsverzeichnis.
Dies ist standardmäßig das HOME-Verzeichnis des Benutzers. Sie sollten hierfür ein
geeignetes Unterverzeichnis einrichten und einstellen.

Wenn die Verbindung zwischen Programm und dem ALC 7000 Expert erfolgreich ist dann
beginnt pyALC7T die Konfiguration der 4 Kanäle auszulesen und anzuzeigen und beginnt
dann mit der kontinuierlichen Abfrage und Anzeige der Messwerte der 4 Kanäle.


Bedienung
---------

Die Bedienung von pyALC7T ist im Online Manual beschrieben.


Installation ohne die ANACONDA Plattform
----------------------------------------

Die oben genannte Python Laufzeitumgebung muss auf dem Rechner installiert sein.

Bei LINUX Systemen, die auf Debian basieren kann die .deb Datei von pyALC7T installiert
werden.

Bei allen anderen Systemen entpacken Sie den pyALC7T Quellcode, gehen in das
pyalc7t Verzeichnis und geben folgenden Befehl 

     python3 setup.py install

in einem Terminal- oder Konsolefenster ein.

Installation mit Qt6 und PIP
----------------------------

Ab Version 1.1.0 unterstützt pyALC7T sowohl das PyQt5 Interface für QT5 als auch das neue PySide6 Interface für Qt6.

Zur Zeit ist PySide6 für die ANACONDA Plattform noch nicht verfügbar. Daher müssen Python, Qt6 und PySide6 aus anderen Quellen installiert werden.

Zunächst benötigt man eine aktuelle Python Version:

* Windows: Python kann aus dem Microsoft Store heruntergeladen werden
* macOS: Ein Universal Binary kann von der [www.python.org](https://www.python.org) Website heruntergeladen werden
* Linux: Python kann aus den Repositories der betreffenden Linux-Distribution herunter geladen werden, sofern es nicht sowieso schon installiert ist.

Nun erstellt man eine virtuelle Python Umgebung für pyALC7T. Diese Umgebung wird
in einem Unterverzeichnis angelegt und enthält alle Software, die für das
Ausführen von pyALC7T benötigt wird. Dieses Verzeichnis kann problemlos gelöscht werden, falls man die betreffende virtuelle Umgebung nicht mehr benötigt.

Um nun eine virtuelle Umgebung "pyalc7t" anzulegen, öffnet man ein Terminalfenster (oder eine Windows Eingabeaufforderung), positioniert sich an einer geeigneten Stelle im Dateisystems und gibt ein:

        python -m venv pyalc7t

Dies erzeugt ein Verzeichnis "pyalc7t" im aktuellen Arbeitsverzeichnis.

Nun aktiviert man die neue Umgebun mit:

        source pyalc7t/bin/activate (Linux, macOS)
oder

        pyalc7t\Scripts\activate (Windows)

Wenn der Name der virtuellen Umgebung in der Eingabeaufforderung erscheint, dann ist die virtuelle Umgebung aktiv.

Nun installiert man die zur Ausführung von pyALC7T benötigte zusätzliche Software:

        python -m pip install PySide6 pyserial

Dann installiert man pyALC7T, wie im folgenden Kapitel beschrieben.

Die virtuelle Umgebung kann man mit dem Befehl:

        deactivate

deaktivieren.

Man kann pyALC7T auch ohne Aktivierung der Umgebung ausführen:
       
        <abs. Pfad Environment Verzeichnis>/bin/python3 <abs. Pfad pyALC7T Verzeichnis>start.py

oder unter Windows:

        <abs. Pfad Environment Verzeichnis>\Scripts\python3 <abs. Pfad pyALC7T Verzeichnis>\start.py



Installation von Entwicklungsversionen
--------------------------------------

Laden Sie die Datei pyalc7t-master von der GitHub Seite von pyALC7T ("Download ZIP" button) herunter und entpacken diese Datei.

Sie können die Entwicklungsversion nun mit:

      Python <Pfad zum pyalc7t-Verzeichnis>/start.py

ausführen.

Bitte beachten Sie:
* Entwicklungsversionen sind ein "Schnappschuss" laufender Entwicklungsarbeiten. Sie sind
  nicht durchgreifend getestet, können abstürzen und schlimmstenfalls zu Datenverlusten führen
* Entwicklungsversionen verwenden nicht die Programmkonfiguration von Produktionsversionen und können daher parallel zu diesen verwendet werden.
