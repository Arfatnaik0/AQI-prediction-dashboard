from flask import Flask, jsonify, render_template
from supabase import create_client
import os

app = Flask(__name__)

def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        raise RuntimeError("Supabase environment variables not set")

    return create_client(url, key)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

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

@app.route("/api/history")
def history():
    supabase = get_supabase()

    res = (
        supabase.table("aqi_history")
        .select(
            "timestamp_utc,pm2_5,pm10,current_aqi,predicted_aqi_3h"
        )
        .order("timestamp_utc")
        .execute()
    )

    return jsonify(res.data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
