# import necessary libraries
from flask import Flask, jsonify, render_template
from supabase import create_client
import os
from datetime import datetime, timedelta, timezone

# for local testing only
# from dotenv import load_dotenv
# load_dotenv()

app = Flask(__name__)

# Initialize Supabase client
def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        raise RuntimeError("Supabase environment variables not set")

    return create_client(url, key)

# Dashboard route
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# Latest AQI record
@app.route("/api/current")
def current():
    supabase = get_supabase()

    res = (
        supabase.table("aqi_history")
        .select("*")
        .order("timestamp_utc", desc=True)
        .limit(1)
        .execute()
    )

    return jsonify(res.data[0])

# Past 24 hours AQI history
@app.route("/api/history")
def history():
    supabase = get_supabase()

    # Calculate UTC timestamp for 24 hours ago
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    res = (
        supabase.table("aqi_history")
        .select("timestamp_utc,pm2_5,pm10,current_aqi,predicted_aqi_3h")
        .gte("timestamp_utc", since)
        .order("timestamp_utc")
        .execute()
    )

    return jsonify(res.data)

# Local run (Railway ignores this and uses Gunicorn)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)