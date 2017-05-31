## pyALC7T (Steuerprogramm und Datenlogger für ALC 7000 Expert)

Index
-----

* [Description](#description)
* [Beschreibung](#beschreibung)
* [Eigenschaften](#eigenschaften)
* [Kompatibilität](#kompatibilität)
* [Installation](#installation)
* [Lizenz](#lizenz)
* [Danksagung](#danksagung)

Description
-----------
pyALC7T is a controller and data logger for the ALC7000 Expert battery charger made by
the german company ELV Elektronik AG. The charger has four channels and can charge
NiCd, NIMH and Lead-Acid batteries. pyALC7T controls this device and logs measurement
over a serial RS232 connection. pyALC7T is entirely written in Python3 using the
Qt framework. It was tested on LINUX, Windows 10 and Mac OS.

Because I do not known whether the charger has been used outside of Germany, the 
software and the documentation is entirely in German.

pyALC7T is a reengineered version of the BASIC program 
[Alc7t](http://www.franksteinberg.de/alc7t.htm) (c) Frank Steinberg 2006.


Beschreibung
------------
pyALC7T ist ein Steuerprogramm und Datenlogger für das Ladegerät ALC7000 Expert
der Firma ELV Elektronik AG. Das Ladegerät ALC 7000 Expert verfügt über vier Kanäle,
mit denen NiCd, NiMh und Blei-Akkus geladen werden können. Das Gerät verfügt über eine
RS-232 Schnittstelle, über die das Ladegerät gesteuert wird und mit der die
Messwerte der vier Kanäle ausgelesen werden.

pyALC7T ist eine reengieerte Version des BASIC Programms
[Alc7t](http://www.franksteinberg.de/alc7t.htm) (c) Frank Steinberg 2006.


Eigenschaften
-------------

* Entwickelt mit Python 3 und dem Qt-Framework.
* Alle Funktionen des ALC 7000 Expert können über die Benutzeroberfläche gesteuert
  werden
* Anzeige und Aufzeichnung der Messwerte für alle Kanäle als Textdatei
* Verwaltung von Akkukonfigurationen (Typ, Anzahl Zellen, Ladestrom, Entladestrom,
  Nennspannung, Nennkapazität, Ladestrom, Entladestrom)
* Anzeige von Spannung und Strom als Liniengrafik während oder nach der Aufzeichnung
* Anzeige der Delta-Peak Spannung und geladener Kapazität
* Die Funktionen der Ladekontrolle und Messwertverarbeitung sind mit denen des BASIC
  Programms Alc7t identisch.


Kompatibilität
--------------

pyALC7T wurde erfolgreich unter LINUX, Windows 10 und Mac OS getestet. Es wird
eine serielle Schnittstelle benötigt, die auch als USB 232 Schnittstelle nachgerüstet
werden kann.


Installation
------------

pyALC7T setzt voraus, dass der Python Interpreter und das Qt Framework installiert sind.
Mit dem [Anaconda Python distribution system](https://www.continuum.io/) können
pyALC7T und die benötigten Laufzeitkomponenten sehr einfach unter Linux, Windows und 
Mac OS installiert werden.

Dies ist in der [Installationsanleitung](https://github.com/bug400/pyalc7t/blob/master/INSTALL.md) näher beschrieben.

Für die grafische Anzeige von Messwerten muss [GNUPLOT](http://www.gnuplot.info) installiert
werden. Ohne installiertes GNUPLOT werden die Messwerte lediglich tabellarisch
angezeigt.


Lizenz
------

pyALC7T wird unter der  GNU General Public License v2.0 veröffentlicht. 
(siehe Datei: LICENSE).


Danksagung
----------

pyALC7T ist eine reengieerte Version des BASIC Programms
[Alc7t](http://www.franksteinberg.de/alc7t.htm) (c) Frank Steinberg 2006.
