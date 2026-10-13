
import requests
from datetime import datetime, timedelta
import calendar

def get_prayer_times_ics(city="Muscat", country="Oman", method=5, output_filename="prayer_times.ics"):
    # Using Aladhan API monthly calendar endpoint
    now = datetime.now()
    year = now.year
    month = now.month
    
    url = f"http://api.aladhan.com/v1/calendarByCity/{year}/{month}"
    params = {
        "city": city,
        "country": country,
        "method": method # 5 is Egyptian General Authority of Survey, 4 is Umm Al Qura
    }
    
    print(f"جاري جلب مواقيت الصلاة لمدينة {city}, {country} لشهر {month}/{year}...")
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("فشل في جلب البيانات من الـ API")
        return
    
    data = response.json().get("data", [])
    
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Prayer Times Generator//AR",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    
    prayers_to_include = {
        "Fajr": "الفجر",
        "Dhuhr": "الظهر",
        "Asr": "العصر",
        "Maghrib": "المغرب",
        "Isha": "العشاء"
    }
    
    event_count = 0
    for day_data in data:
        gregorian_date = day_data["date"]["gregorian"]["date"] # format: DD-MM-YYYY
        timings = day_data["timings"]
        
        d_obj = datetime.strptime(gregorian_date, "%d-%m-%Y")
        
        for p_key, p_name in prayers_to_include.items():
            if p_key in timings:
                # Timing string looks like "04:30 (+04)". We need to clean it up.
                time_str = timings[p_key].split(" ")[0] # "04:30"
                hour, minute = map(int, time_str.split(":"))
                
                start_dt = d_obj.replace(hour=hour, minute=minute)
                end_dt = start_dt + timedelta(minutes=15) # صلاة لمدة 15 دقيقة
                
                # Format for ICS: YYYYMMDDTHHMMSS
                dtstart = start_dt.strftime("%Y%m%dT%H%M00")
                dtend = end_dt.strftime("%Y%m%dT%H%M00")
                
                uid = f"prayer-{p_key}-{start_dt.strftime('%Y%m%d')}@prayertimes.local"
                
                ics_lines.extend([
                    "BEGIN:VEVENT",
                    f"UID:{uid}",
                    f"DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
                    f"DTSTART:{dtstart}",
                    f"DTEND:{dtend}",
                    f"SUMMARY:صلاة {p_name}",
                    f"DESCRIPTION:وقت أذان {p_name}",
                    "END:VEVENT"
                ])
                event_count += 1

    ics_lines.append("END:VCALENDAR")
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("\r\n".join(ics_lines))
        
    print(f"تم بنجاح إنشاء الملف: {output_filename} ويحتوي على {event_count} حدث!")

if __name__ == "__main__":
    # يمكنك تغيير المدينة والدولة حسب رغبتك (مثلاً "Muscat" و "Oman" أو "Cairo" و "Egypt")
    city_input = input("أدخل اسم المدينة (بالإنجليزية، مثل Muscat أو Cairo): ") or "Muscat"
    country_input = input("أدخل اسم الدولة (بالإنجليزية، مثل Oman أو Egypt): ") or "Oman"
    get_prayer_times_ics(city=city_input, country=country_input, output_filename="prayer_times.ics")
