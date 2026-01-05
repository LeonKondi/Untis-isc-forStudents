📅 Untis für Schüler: Der automatische Kalender-Server
Dein Stundenplan endlich im iPhone/Android Kalender – live, intelligent und automatisch.

😫 Das Problem
Kennt ihr das? Ihr wollt euren Tag planen, aber WebUntis bietet für Schüler einfach keine Kalender-Abonnements an (nur für Lehrer). Man muss ständig die App öffnen, Screenshots machen oder alles manuell abtippen.

💡 Die Lösung
Dieses Projekt ist ein "Set-it-and-forget-it" Server für deinen Raspberry Pi (oder jeden Linux-PC). Er loggt sich für dich bei WebUntis ein, holt den Stundenplan und erstellt einen Live-Kalenderlink, den du auf deinem Handy abonnieren kannst.

✨ Die Features
🔄 Live-Sync: Prüft alle 15 Minuten auf Änderungen (Raumwechsel, Entfall).

🧠 Intelligente Lücken-Erkennung:

  -Erkennt echte freie Tage und markiert sie als "🟢 Frei heute".

  -Unterscheidet zwischen "Frei" und "Schule hat den Plan noch nicht veröffentlicht". Wenn Untis die nächste Woche noch blockt, zeigt der Kalender: "🔄 Schultag Update kommt noch".

🌍 Überall verfügbar: Läuft 24/7 zu Hause und synchronisiert sich über das Internet mit deinem Handy.

⚡ Blitzschnell: Umgeht typische WebUntis-Sperren durch intelligentes Caching.

🚀 Schritt-für-Schritt Installation (Tutorial)
Dieses Tutorial ist so geschrieben, dass du es auch ohne Vorkenntnisse in Linux oder Programmieren schaffst.

Vorraussetzungen
  -Einen Raspberry Pi (oder einen anderen Linux Computer/Server).

  -Internetverbindung.

  -Deine WebUntis Zugangsdaten.

Schritt 1: Den Code herunterladen
Öffne das Terminal auf deinem Pi und führe folgende Befehle aus, um den Code zu holen und in den Ordner zu wechseln:

cd Desktop
git clone https://github.com/LeonKondi/Untis-isc-forStudents.git
cd Untis-isc-forStudents

Schritt 2: Software-Pakete installieren
Der Server benötigt Python-Module. Installiere sie hiermit:

pip3 install -r requirements.txt
(Hinweis: Falls ein Fehler auftritt ("externally-managed environment"), benutze stattdessen: pip3 install -r requirements.txt --break-system-packages) 

Schritt 3: Konfiguration erstellen
Jetzt müssen wir dem Server sagen, wer du bist.

  1.Erstelle die Konfigurationsdatei:
  nano config.json

  2.Kopiere den folgenden Text, füge ihn ein und ändere die Daten zu deinen eigenen:
  {
    "server_url": "deine-schule.webuntis.com",
    "school": "deine-schule",
    "username": "DeinBenutzername",
    "password": "DeinPasswort",
    "class_name": "10a",
    "interval_seconds": 900,
    "port": 80
}
  -Wie finde ich die Schul-URL? Logge dich am PC im Browser bei Untis ein. Die Adresse oben ist z.B. https://heine-gymnasium.webuntis.com/...

  server_url = heine-gymnasium.webuntis.com

  school = heine-gymnasium

  interval_seconds: Lass es auf 900 (15 Min). Wenn du es zu niedrig stellst, sperrt WebUntis deinen Account.

  Speichere die Datei mit STRG + O (Enter) und beende mit STRG + X.

  🌍 Schritt 4: Zugriff über das Internet (Dataplicity)
Damit der Kalender auch funktioniert, wenn du nicht im heimischen WLAN bist (z.B. in der Schule mit 4G/5G), muss dein Pi aus dem Internet erreichbar sein. Wir nutzen dafür Dataplicity (kostenlos & sicher).

  1.Gehe am PC auf dataplicity.com und erstelle einen kostenlosen Account.

  2.Du bekommst einen Installations-Code angezeigt (startet mit curl...). Kopiere ihn.

  3.Füge diesen Code im Terminal deines Raspberry Pi ein und drücke Enter.

  4.Gehe zurück auf die Dataplicity-Webseite. Dein Pi sollte dort jetzt als "Online" erscheinen.

  5.Klicke auf deinen Pi und aktiviere oben den Schalter "Wormhole".

  6.Kopiere die grüne Adresse, die dort steht (z.B. https://dein-pi.dataplicity.io).

👉 Dein Kalender-Link ist: https://dein-pi.dataplicity.io/kalender.ics

  🤖 Schritt 5: Den Server 24/7 laufen lassen (Autostart)
Wir richten den Pi so ein, dass er den Server automatisch startet, sobald er Strom bekommt.

  1.Erstelle die Service-Datei:
  sudo nano /etc/systemd/system/untis.service

  2.Füge folgenden Inhalt ein (WICHTIG: Ersetze DEIN_USER durch deinen Pi-Benutzernamen, z.B. pi oder pi4. Prüfe mit whoami im Terminal):
  [Unit]
  Description=Untis Kalender Server
  After=network.target

  [Service]
  User=root
  Group=root
  WorkingDirectory=/home/DEIN_USER/Desktop/Untis-isc-forStudents
  ExecStart=/usr/bin/python3 /home/DEIN_USER/Desktop/Untis-isc-forStudents/untis-server.py
  Restart=always
  RestartSec=10

  [Install]
  WantedBy=multi-user.target

  3.Speichern (STRG + O) und Beenden (STRG + X).

  4.Autostart aktivieren:
  sudo systemctl enable untis.service
  sudo systemctl start untis.service
  
Der Server läuft jetzt immer!

📱 Einrichtung am Handy
Nimm den Link aus Schritt 4 (.../kalender.ics) und richte ihn ein:

  🍏 iPhone (iOS)
  1.Einstellungen -> Kalender -> Accounts.
  
  2."Account hinzufügen" -> "Andere".
  
  3."Kalenderabonnement hinzufügen".
  
  4.Link einfügen -> Weiter -> Sichern.
  
  🤖 Android
  ⚠️ Wichtig: Android aktualisiert normale Kalender-Abos oft nur alle 24 Stunden. Das ist für Stundenpläne zu langsam!
  
  1.Lade dir eine beliebige App herunter , die die Kalender-Abos ofter als nur alle 24H den Plan aktuallisiert .
  
  2.Füge dort deinen Link ein.
  
  3.Stelle das Sync-Intervall auf 15 Minuten.

🧠 Deep Dive: Wie der Code funktioniert
Für Entwickler und Interessierte – was passiert unter der Haube (untis-server.py)?

  1. Der Worker-Thread (Hintergrund-Arbeiter)
  Das Programm startet einen separaten Thread, der völlig unabhängig vom Webserver läuft. Dieser Thread wacht alle 15 Minuten auf und führt fetch_untis_data() aus.
  
  2. Das "Horizont"-Konzept
  WebUntis blockiert oft die Einsicht in die ferne Zukunft. Das Skript löst das so:
  
  -Es sucht den letzten Tag, an dem tatsächlich Unterricht stattfindet (z.B. in 2 Wochen). Das ist der "Horizont".
  
  -Vor dem Horizont: Wenn hier ein Tag leer ist, ist er sicher Frei (Grünes Event).
  
  -Hinter dem Horizont: Wenn hier ein Tag leer ist, bedeutet das nur, dass Untis die Daten noch nicht freigegeben hat (Oranges Event "Update kommt noch").
  
  3. Daten-Persistenz
  Die Daten werden in untis_history.json gespeichert.
  
  -Beim Neustart lädt der Server sofort den alten Stand (keine Wartezeit).
  
  -Alte Tage bleiben erhalten, auch wenn sie aus WebUntis verschwinden (Historie).
  
  4. ICS Generierung (Flask)
  Ein leichtgewichtiger Flask-Webserver lauscht auf Port 80. Wenn eine Anfrage an /kalender.ics kommt:
  
  -Lädt er die aktuellen Daten aus dem Speicher.
  
  -Wandelt JSON-Daten in das iCalendar-Format (RFC 5545).
  
  -Setzt korrekte Zeitzonen (Europe/Berlin), damit Sommer-/Winterzeit passen.
  
  -Sendet die Datei an das Handy.

Suuuper das war's! So einfach geht das, noch einfacher wurde es gehen ,wenn Untis die iCal Funktion auch für Schüler hinzufügen würde.

Leon :))
