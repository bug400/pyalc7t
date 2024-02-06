# pyALC7T Installationsanleitung

Index
-----

* [Voraussetzungen](#voraussetzungen)
* [Installationsvorgang](#installationsvorgang)
     * [Installation unter Windows](#installation-unter-windows)
     * [Installation unter macOS](#installation-unter-macos)
     * [Installation unter Linux](#installation-unter-macos)
* [Installation von Quellcode aus GitHub](#installation-von-quellcode-aus-github)
* [Installation von GNUPLOT](#installation-von-gnuplot)
* [Einrichtung von pyALC7T](#einrichtung-von-pyalc7t)
* [Bedienung](#bedienung)
* [Installation von Entwicklungsversionen](#installation-von-entwicklungsversionen)
* [Verwaltung virtueller Umgebungen](#verwaltung-virtueller-umgebungen)


## Voraussetzungen

Für den Einsatz von pyALC7T müssen installiert sein:

* Python 3.6 oder neuere Versionen. Python 3.11 wird ist die zur Zeit empfohlene Fassung.
* QT 5.9 oder neuere Versionen mit der PyQt5 Python/Qt-Schnittstelle oder Qt 6.3 oder neuer (empfohlen) mit der Pyside6 Pyton/Qt-Schnittstelle.
* die Python/Qt-Schnittstelle entweder für Qt Webkit (nur für Qt5)  oder Qt Webengine (empfohlen). Dies wird nur für
  die Anzeige des Online-Manuals benötigt.
* pySerial  ab 2.7 
* GNUPLOT. Das Programm wird nur für die grafische Anzeige von Messwerten benötigt.

Der Rechner muss mit einer RS232 Schnittstelle ausgestattet sein. Diese kann bei modernen
Rechnersystemen über einen USB-RS232 Adapter nachgerüstet werden. 

## Installationsvorgang

Die Installation von pyALC7T und der benötigten Laufzeitumgebung geschieht in den folgenden Schritten.

1. Installation des Python Interpreters

* Windows: der Interpreter kann aus dem Microsoft Store installiert werden (freie Software)
* macOS: den Python universal Installer von [www.python.org](https://www.python.org) herunterladen und installieren
* Linux: Python aus den Systemrepositories installieren, sofern dies noch nicht geschehen ist.

2. Erstellung einer virtuellen Python Umgebung für pyALC7T

Eine virtuelle Python Umgebung ist eine eigene Verzeichnisstruktur, die pyALC7T und die benötigten Laufzeitumgebung enthält. Um sie zu benutzen, muss diese Umgebung aktiviert werden (siehe unten) und sie läuft isoliert von der Python Installation des Betriebssystems oder von anderen virtuellen Umgebungen. Die Installation von pyALC7T in einer virtuellen Umgebung greift daher nicht in die Konfiguration ihres Systems ein.

Eine virtuelle Umgebung wird gelöscht, indem man ihren Verzeichnisbaum entfernt. Die pyALC7T Konfigurationsdateien bleiben dabei erhalten.

3. Aktivierung der virtuellen Python Umgebung für pyALC7T

Die virtuelle Umgebung wird in Betrieb gesetzt, indem ein Aktivierungsscript aufgerufen wird. Eine aktive Umgebung erkennt man daran, dass ihr Name in die Eingabeaufforderung (Prompt String) eingefügt wird.

4. Installation von pyALC7T und der zusätzlich benötigten Komponenten

Dieser Verarbeitungsschritt lädt pyALC7T und die notwendigen Laufzeitkomponenten (Qt6, PySide6, pySerial) vom [Python Package Index (PyPi)](https://pypi.org) herunter. PyPi ist das offizielle third party repository für Python. Sie können auch weitere Software in die virtuelle Umgebung von PyPi installieren.

<b>Achtung: rufen Sie den Python Interpreter immer mit "python3" auf, wenn Sie die virtuelle Umgebung erstellen. Wenn Sie die Umgebung aktiviert haben, verwenden sie immer den Aufruf "python".</b>

5. Verwaltung der Virtuellen Umgebung

Siehe [Verwaltung der virtuellen Umgebung](#verwaltung-der-virtuellen-umgebung)


### Installation unter Windows

Achtung: verwenden Sie immer die Anwendung "Kommandozeile" anstelle von "Terminal (PowerShell)" um die unten beschriebenen Befehle einzugeben.

Um den Python Interpreter zu installieren, öffnen Sie den Microsoft Store, suchen Sie nach dem Stichwort "Python" und installieren Sie die empfohlene Version (siehe oben). Die Python App wird dabei nur für den aktuellen Benutzer eingerichtet, so dass keine Administratoren Rechte erforderlich sind.

Beispiel:  Erstellung einer virtuellen Umgebung "py311" im Home-Verzeichnis des Benutzers, Installation und Aufruf von pyALC7T:


     C:\>cd %USERPROFILE%                                  (wechselt auf das Home Verzeichnis)
     
     C:\Users\bug400>python3 -m venv py311                 (erstellt die virtuelle Umgebung im Verzeichnis %USERPROFILE%\py311, verwenden Sie den Aufruf "python3" an dieser Stelle!!!)

     C:\Users\bug400>py311\scripts\activate                (Aktivierung der virtuellen Umgebung, der Name der aktiven Umgebung wird Teil des Prompt-Strings)
     
     (py311) C:\Users\bug400>python -m pip install pyalc7t (installert pyALC7T mit den benotigten Laufzeitkomponenten)
     Collecting pyalc7t
       Obtaining dependency information for pyalc7t from https://files.pythonhosted.org/packages/3e/
     
     ...
     
     Installing collected packages: pyserial, shiboken6, PySide6-Essentials, PySide6-Addons, pyside6, pyalc7t
     Successfully installed PySide6-Addons-6.6.1 PySide6-Essentials-6.6.1 pyalc7t-1.1.1 pyserial-3.5 pyside6-6.6.1 shiboken6-6.6.1
     
     [notice] A new release of pip is available: 23.2.1 -> 23.3.2
     [notice] To update, run: python.exe -m pip install --upgrade pip
     
     (py311) C:\Users\bug400>pyalc7t                        (start pyALC7T)

Die Windows Firewall blockiert standardmäßig den Netzwerkzugriff neuer Programme. Wenn ein Python Programm zum ersten Mal auf das Netzwerk zugreift, dann öffnet sich ein Fenster in dem eine Firewall Ausnahmeregel für den Python Interpreter eingerichtet werden kann. Für diesen Vorgang werden Administratorrechte benötigt.

Sie können pyALC7T auch ohne Aktivierung der virtuellen Umgebung aufrufen:

     %USERPROFILE%\py311\scripts\pyalc7t

Mit einer Desktop Verknüpfung von %USERPROFILE\py311\scripts\pyalc7t.exe können Sie pyALC7T aus der Windows Benutzeroberfläche starten.


### Installation unter macOS

Installieren Sie Python für macOS von der [Python website](https://www.python.org/). Wählen Sie die empfohlene Version aus (siehe oben), laden sie herunter und installieren Sie den macOS 64-bit Universal Installer. Hierfür benötigen Sie Administratorrechte.

Weiterführende Informationen zur Verwendung von Python unter macOS enthält die Webseite [Using Python on a Mac](https://docs.python.org/3/using/mac.html).

Beispiel:  Erstellung einer virtuellen Umgebung "py311" im Home-Verzeichnis des Benutzers, Installation und Aufruf von pyALC7T:

     node1-mac:~ bug400$ python3 -m venv py311                  (create virtual environment ~/py311)
     node1-mac:~ bug400$ source py311/bin/activate              (activate virtual environment ~/py311)
     (py311) node1-mac:~ bug400$ python -m pip install pyalc7t  (install pyALC7T and required runtime components)
     Collecting pyalc7t
       Obtaining dependency information for pyalc7t from https://files.pythonhosted.org/packages/3e

     ...

     Using cached shiboken6-6.6.1-cp38-abi3-macosx_11_0_universal2.whl (406 kB)
     Installing collected packages: pyserial, shiboken6, PySide6-Essentials, PySide6-Addons, pyside6, pyalc7t
     Successfully installed PySide6-Addons-6.6.1 PySide6-Essentials-6.6.1 pyalc7t-1.1.1 pyserial-3.5 pyside6-6.6.1 shiboken6-6.6.1
     
     [notice] A new release of pip is available: 23.2.1 -> 23.3.2
     [notice] To update, run: pip install --upgrade pip
     (py311) node1-mac:~ bug400$ pyalc7t                        (start pyALC7T)
     
Sie können pyALC7T auch ohne Aktivierung der virtuellen Umgebung aufrufen:

     node1-mac:~ bug400$ ~/py311/bin/pyalc7t

Sie können pyALC7T vom Desktop oder mit dem Finder aufrufen, indem Sie ein Startprogramm mit Automator erstellen. Dies ist in [diesem Blogbeitrag](https://www.hpmuseum.org/forum/thread-3824-post-150519.html#pid150519) beschrieben. Tragen Sie den oben genannten Aufruf in die „Shell Script“ box ein.


### Installation unter Linux

Es wird empfohlen, den Python3 Interpreter Ihres Linux Systems zu verwenden.

## Installation von Quellcode aus GitHub

Um pyALC7T auf diese Weise zu installieren müssen die oben genannten Softwarevoraussetzungen auf Ihrem Rechner installiert sein.

Laden Sie den aktuellsten pyALC7T Quellcode von der [pyALC7T Releases page](https://github.com/bug400/pyalc7t/releases/) und entpacken Sie die Zip-Datei. Sie erhalten das pyALC7T directory pyalc7t-x.y.z, wobei x.y.z die Versionsnummer ist.

Nun können Sie pyALC7T mit folgendem Befehl starten:

      python <Path to the pyALC7T directory>/start.py 

Hinweis: es hängt von Ihrer Linux Distribution und Konfiguration ab, ob der Python Interpreter mit "python" oder "python3" aufgerufen wird.

Sie können eine Desktop-Datei erstellen um pyALC7T von der Benutzeroberfläche aufzurufen. Tragen Sie in diesem Fall den Python Interpreter als Kommando und den Pfad zur Datei "start.py" als Argument ein.

Auf der [pyALC7T Releases page](https://github.com/bug400/pyalc7t/releases/) finden Sie auch ein Installationspaket für die aktuelle Debian Version. Bei der Installation dieses Pakets werden auch die benötigten Abhängigkeiten mit installiert. Dieses Installationspaket kann auch zur Installation auf Linux Distributionen verwendet werden, die aus der aktuellen Debian Version abgeleitet wurden (z.B. Ubuntu, Raspberry PI OS).

## Installation von GNUPLOT

Laden Sie GNUPLOT von der [GNUPLOT Website](http://www.gnuplot.info) herunter und installieren das Programm gemäß Installationsanleitung.

Bei LINUX Betriebssystemen kann GNUPLOT über die dort vorhandenen Softwarepaket
Managementsysteme installiert werden.


## Einrichtung von pyALC7T

Beim ersten Programmstart muss die korrekte serielle Schnittstelle angegeben
werden, an der das Ladegerät ALC7000 angeschlossen ist. Außerdem muss das
Arbeitsverzeichnis eingerichtet werden, in dem die Arbeits- und Log-Dateien von
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

Unter mac OS ist der Gerätename üblicherweise /dev/tty.usbserial-XXXX.

pyALC7T speichert alle LOG-Dateien und Arbeitsdateien in einem Arbeitsverzeichnis.
Dies ist standardmäßig das HOME-Verzeichnis des Benutzers. Sie sollten hierfür ein
geeignetes Unterverzeichnis einrichten und einstellen.

Wenn die Verbindung zwischen Programm und dem ALC 7000 Expert erfolgreich ist dann
beginnt pyALC7T die Konfiguration der 4 Kanäle auszulesen und anzuzeigen und beginnt
dann mit der kontinuierlichen Abfrage und Anzeige der Messwerte der 4 Kanäle.


## Bedienung

Die Bedienung von pyALC7T ist im Online Manual beschrieben.


## Installation von Entwicklungsversionen

Laden Sie die Datei pyalc7t-master von der GitHub Seite von pyALC7T ("Download ZIP" button) herunter und entpacken diese Datei.

Sie können die Entwicklungsversion nun mit:

      Python <Pfad zum pyalc7t-Verzeichnis>/start.py

ausführen.

Bitte beachten Sie:
* Entwicklungsversionen sind ein "Schnappschuss" laufender Entwicklungsarbeiten. Sie sind
  nicht durchgreifend getestet, können abstürzen und schlimmstenfalls zu Datenverlusten führen
* Entwicklungsversionen verwenden nicht die Programmkonfiguration von Produktionsversionen und können daher parallel zu diesen verwendet werden.

## Verwaltung virtueller Umgebungen

Es wird empfohlen gelegentlich zu prüfen, ob eine neue Version von pyALC7T existiert und nur dieses Paket zu aktualisieren.

Hinweis: um den Python Interpreter zu aktualisieren ist es am sichersten, den alten Interpreter und die virtuelle Umgebung zu löschen und dann mit dem neuen Interpreter die virtuelle Umgebung neu einzurichten.

Um eine virtuelle Python Umgebung zu verwalten, muss sie zunächst aktiviert werden:

     <path to venv directory>/scripts/activate (Windows)
     oder
     source <path to venv directory>/bin/activate (macOS, Linux)


Virtuelle Python Umgebung deaktivieren:

     deactivate

Prüfung, welche Pakete aktualisiert werden können:

     python -m pip list -o

Aktualisierung von pyALC7T:

     python -m pip upgrade pyalc7t


Weitere Kommandos zur Verwaltung virtueller Python Umgebungen:

Installierte Pakete anzeigen:

     python -m pip list

Ein Paket installieren:

     python -m pip install <packagename>

Detailinformationen zu einem Paket anzeigen:

     python -m pip show <packagename>

Ein Paket löschen:

     python -m pip uninstall <packagename>

Anzeige, ob neue Paketversionen vorliegen:

     python -m pip list -o

Neue Version eines Pakets installieren (pip kann mit pip aktualisiert werden)

     python -m pip upgrade pyalc7t

Paket Cache löschen (spart Plattenplatz):

     python -m pip cache  purge

Virtuelle Python Umgebung löschen

    Verzeichnisbaum der virtuellen Python Umgebung löschen

