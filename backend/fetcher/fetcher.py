# import necessary libraries
import requests
import datetime
import redis, json
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

# lat and lon for Mumbai
LAT = 18.9766
LON = 72.8338

# load environment variables
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")

# check for required environment variables
if not OPENWEATHER_API_KEY or not REDIS_URL:
    raise RuntimeError("Missing required environment variables")

REDIS_KEY = "air_quality_history"
MAX_HOURS = 3

# connect to redis
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# function to fetch data and store in redis
def fetch_and_store():
    try:
        dataaqi = requests.get(
            f"http://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={OPENWEATHER_API_KEY}",
            timeout=10
        ).json()

        # Weather API
        dataweather = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={OPENWEATHER_API_KEY}",
            timeout=10
        ).json()


        pm2_5=dataaqi['list'][0]['components']['pm2_5']
        pm10=dataaqi['list'][0]['components']['pm10']

        timestamp=dataaqi['list'][0]['dt']
        timestamp=datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        temp=dataweather['main']['temp']-273
        humidity=dataweather['main']['humidity']
        windS=dataweather['wind']['speed']
        windD=dataweather['wind']['deg']

        record={
            "pm2_5":pm2_5,
            "pm10":pm10,
            "time":timestamp,
            "temp":round(temp,2),
            "humidity":humidity,
            "windS":windS,
            "windD":windD
        }

        # push new reading
        r.rpush(REDIS_KEY, json.dumps(record))

        # keep only last 3 readings
        r.ltrim(REDIS_KEY, -MAX_HOURS, -1)

        print("fetching data at:", datetime.datetime.now())
    except Exception as e:
        print("Error fetching or storing data:", e)
    
# setup scheduler
scheduler = BackgroundScheduler(timezone=timezone("Asia/Kolkata"))

# run every hour
scheduler.add_job(fetch_and_store, "cron", minute=0)

# start scheduler
scheduler.start()
print("Hourly scheduler started")

# keep process alive
while True:
    time.sleep(60)


