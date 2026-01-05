import time
import threading
import datetime
import json
import os
import sys
import webuntis
from ics import Calendar, Event
from flask import Flask, Response

try:
    from zoneinfo import ZoneInfo
    GERMAN_TIMEZONE = ZoneInfo("Europe/Berlin")
except ImportError:
    from datetime import timezone, timedelta
    GERMAN_TIMEZONE = timezone(timedelta(hours=1))

CONFIG_FILE = "config.json"
HISTORY_FILE = "untis_history.json"

app = Flask(__name__)
current_ics_data = ""
last_update_time = "N/A"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        sys.exit(1)
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_history():
    if not os.path.exists(HISTORY_FILE): return {}
    try:
        with open(HISTORY_FILE, 'r') as f: return json.load(f)
    except: return {}

def save_history(data):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)

def fetch_untis_data():
    global current_ics_data, last_update_time
    config = load_config()
    
    while True:
        history_db = load_history()
        fetch_start = datetime.date.today()
        fetch_end = fetch_start + datetime.timedelta(days=30)
        untis_horizon_date = fetch_start 
        new_lessons_found = []

        try:
            with webuntis.Session(
                username=config["username"],
                password=config["password"],
                server=config["server_url"],
                school=config["school"],
                useragent='PythonPiBooster'
            ) as s:
                s.login()
                
                klasse = None
                for k in s.klassen():
                    if k.name.upper() == config["class_name"].upper():
                        klasse = k
                        break
                
                if klasse:
                    timetable = s.timetable(start=fetch_start, end=fetch_end, klasse=klasse)
                    for lesson in timetable:
                        try:
                            if lesson.start.date() > untis_horizon_date:
                                untis_horizon_date = lesson.start.date()

                            d_str = lesson.start.strftime("%Y-%m-%d")
                            start_aware = lesson.start.replace(tzinfo=GERMAN_TIMEZONE)
                            end_aware = lesson.end.replace(tzinfo=GERMAN_TIMEZONE)

                            event_entry = {
                                "name": lesson.subjects[0].name if lesson.subjects else "Stunde",
                                "start": start_aware.isoformat(),
                                "end": end_aware.isoformat(),
                                "location": lesson.rooms[0].name if lesson.rooms else "",
                                "type": "lesson",
                                "status": lesson.code
                            }
                            new_lessons_found.append((d_str, event_entry))
                        except:
                            continue

        except Exception:
            pass
        
        curr = fetch_start
        while curr <= fetch_end:
            d_key = curr.strftime("%Y-%m-%d")
            if d_key in history_db: del history_db[d_key]
            curr += datetime.timedelta(days=1)
            
        days_with_lessons = set()
        for d_str, event_data in new_lessons_found:
            if d_str not in history_db: history_db[d_str] = []
            history_db[d_str].append(event_data)
            days_with_lessons.add(d_str)

        fill_end = datetime.date.today() + datetime.timedelta(days=14)
        curr = fetch_start
        while curr <= fill_end:
            if curr.weekday() < 5:
                d_str = curr.strftime("%Y-%m-%d")
                if d_str not in days_with_lessons:
                    titel = "🟢 Frei heute" if curr <= untis_horizon_date else "🔄 Schultag Update kommt noch"
                    
                    start_dt = datetime.datetime.combine(curr, datetime.time(7, 50)).replace(tzinfo=GERMAN_TIMEZONE)
                    end_dt = datetime.datetime.combine(curr, datetime.time(8, 0)).replace(tzinfo=GERMAN_TIMEZONE)

                    placeholder = {
                        "name": titel,
                        "start": start_dt.isoformat(),
                        "end": end_dt.isoformat(),
                        "location": "",
                        "type": "info",
                        "status": ""
                    }
                    history_db[d_str] = [placeholder]
            curr += datetime.timedelta(days=1)

        save_history(history_db)
        
        c = Calendar()
        for date_key, events in history_db.items():
            for ev in events:
                e = Event()
                titel = ev["name"]
                emoji = "❌ " if ev["status"] == "cancelled" else ("⚠️ " if ev["status"] == "irregular" else "")
                if ev["status"] == "cancelled": titel = f"Entfall: {titel}"
                
                e.name = f"{emoji}{titel}" + (f" ({ev['location']})" if ev["location"] else "")
                e.begin = ev["start"]
                e.end = ev["end"]
                e.location = ev["location"]
                c.events.add(e)
        
        current_ics_data = c.serialize()
        last_update_time = datetime.datetime.now().strftime('%d.%m. %H:%M')
        time.sleep(config.get("interval_seconds", 900))

@app.route('/')
def index():
    return f"Server Online. Last Update: {last_update_time}"

@app.route('/kalender.ics')
def serve_ics():
    r = Response(current_ics_data, mimetype='text/calendar')
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return r

if __name__ == "__main__":
    t = threading.Thread(target=fetch_untis_data)
    t.daemon = True
    t.start()
    conf = load_config()
    app.run(host='0.0.0.0', port=conf.get("port", 80))