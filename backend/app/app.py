#import necessary libraries
from flask import Flask, jsonify, render_template
from supabase import create_client
import os
# import dotenv
# dotenv.load_dotenv()

# initialize Flask app and Supabase client
app = Flask(__name__)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

# default route
@app.route("/")
def dashboard():
    return render_template("dashboard.html")

# API route to get current AQI data
@app.route("/api/current")
def current():
    res = (
        supabase.table("aqi_history")
        .select("*")
        .order("timestamp_utc", desc=True)
        .limit(1)
        .execute()
    )
    return jsonify(res.data[0])

# API route to get historical AQI data
@app.route("/api/history")
def history():
    res = (
        supabase.table("aqi_history")
        .select("timestamp_utc,pm2_5,pm10,current_aqi,predicted_aqi_3h")
        .order("timestamp_utc")
        .execute()
    )
    return jsonify(res.data)

if __name__ == "__main__":
    app.run(debug=True)
