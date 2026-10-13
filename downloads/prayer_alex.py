import requests
from datetime import datetime, timedelta
import os

url = "http://api.aladhan.com/v1/calendarByCity/2026/10"
params = {"city": "Alexandria", "country": "Egypt", "method": 5}

response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json().get("data", [])
    ics = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Alexandria Prayer Times//AR"]
    
    for day in data:
        date_str = day["date"]["gregorian"]["date"]
        timings = day["timings"]
        d_obj = datetime.strptime(date_str, "%d-%m-%Y")
        
        for k, name in [("Fajr", "الفجر"), ("Dhuhr", "الظهر"), ("Asr", "العصر"), ("Maghrib", "المغرب"), ("Isha", "العشاء")]:
            if k in timings:
                t = timings[k].split(" ")[0]
                h, m = map(int, t.split(":"))
                start = d_obj.replace(hour=h, minute=m)
                end = start + timedelta(minutes=15)
                
                ics.extend([
                    "BEGIN:VEVENT",
                    f"UID:alex-{k}-{start.strftime('%Y%m%d')}@prayer",
                    f"DTSTART:{start.strftime('%Y%m%dT%H%M00')}",
                    f"DTEND:{end.strftime('%Y%m%dT%H%M00')}",
                    f"SUMMARY:صلاة {name}",
                    "END:VEVENT"
                ])
    
    ics.append("END:VCALENDAR")
    
    # حفظ الملف مباشرة في مجلد التنزيلات Downloads
    downloads_path = "/storage/emulated/0/Download"
    if os.path.exists(downloads_path):
        filepath = os.path.join(downloads_path, "alexandria_prayer_times.ics")
    else:
        filepath = "alexandria_prayer_times.ics"
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\r\n".join(ics))
    print(f"تم حفظ الملف بنجاح في: {filepath}")
else:
    print("فشل الاتصال بالإنترنت لجلب البيانات.")
