from flask import Flask, render_template_string, request, redirect, url_for
import os
import socket
import datetime

app = Flask(__name__)

# Sample aviation weather advisory records
ADVISORIES = [
    {
        "station": "VOBL (Bengaluru Int)",
        "condition": "Severe Wind Shear",
        "wind_speed": "38 kts",
        "visibility": "3.2 km",
        "severity": "CRITICAL",
        "updated": "13:10 UTC"
    },
    {
        "station": "VOMM (Chennai Int)",
        "condition": "Coastal Convective Storm",
        "wind_speed": "22 kts",
        "visibility": "6.0 km",
        "severity": "HIGH",
        "updated": "13:14 UTC"
    },
    {
        "station": "VOHS (Hyderabad)",
        "condition": "Scattered Clouds / Clear",
        "wind_speed": "08 kts",
        "visibility": "10.0 km",
        "severity": "NORMAL",
        "updated": "13:20 UTC"
    }
]

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AeroWeather | Flight Meteorology Sentinel</title>
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #faf8f5;
      color: #292524;
      margin: 0;
      padding: 2.5rem 1rem;
    }
    .wrapper { max-width: 980px; margin: auto; }
    
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 1.5rem;
      border-bottom: 2px solid #fed7aa;
      margin-bottom: 2rem;
    }
    .header h1 { 
      margin: 0; 
      font-size: 1.85rem; 
      color: #c2410c;
      display: flex; 
      align-items: center; 
      gap: 0.6rem; 
      font-weight: 800;
    }
    .badge-live {
      background: #fef3c7; 
      color: #b45309; 
      border: 1px solid #f59e0b;
      padding: 0.35rem 0.9rem; 
      border-radius: 9999px; 
      font-size: 0.8rem; 
      font-weight: 700;
      letter-spacing: 0.04em;
    }
    
    .meta-bar {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.2rem;
      margin-bottom: 2rem;
    }
    .meta-card {
      background: #ffffff;
      border: 1px solid #fed7aa;
      border-radius: 12px;
      padding: 1.1rem;
      box-shadow: 0 4px 12px rgba(234, 88, 12, 0.06);
      position: relative;
      overflow: hidden;
    }
    .meta-card::before {
      content: "";
      position: absolute;
      top: 0; left: 0; right: 0; height: 4px;
      background: linear-gradient(90deg, #f59e0b, #ea580c);
    }
    .meta-title { font-size: 0.75rem; text-transform: uppercase; color: #9a3412; font-weight: 700; letter-spacing: 0.05em; }
    .meta-value { font-size: 1.15rem; font-weight: 700; color: #1c1917; margin-top: 0.35rem; }
    .meta-code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; color: #ea580c; }
    
    .panel {
      background: #ffffff;
      border: 1px solid #fed7aa;
      border-radius: 12px;
      padding: 1.6rem;
      margin-bottom: 2rem;
      box-shadow: 0 4px 15px rgba(234, 88, 12, 0.05);
    }
    .panel h2 { 
      margin-top: 0; 
      font-size: 1.2rem; 
      color: #9a3412;
      font-weight: 700;
    }
    
    .form-grid {
      display: grid;
      grid-template-columns: 1.5fr 2fr 1fr 1fr auto;
      gap: 0.8rem;
    }
    input, select {
      padding: 0.75rem 0.9rem;
      border-radius: 8px;
      font-size: 0.9rem;
      border: 1.5px solid #fed7aa;
      background: #fffcf9;
      color: #292524;
      outline: none;
      transition: border 0.2s, box-shadow 0.2s;
    }
    input:focus, select:focus {
      border-color: #f97316;
      box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.15);
    }
    button {
      padding: 0.75rem 1.4rem;
      border-radius: 8px;
      background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
      color: #ffffff;
      font-weight: 700;
      font-size: 0.9rem;
      border: none;
      cursor: pointer;
      box-shadow: 0 4px 12px rgba(234, 88, 12, 0.25);
      transition: transform 0.15s, opacity 0.2s;
    }
    button:hover { 
      opacity: 0.95;
      transform: translateY(-1px);
    }
    
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    th { 
      text-align: left; 
      padding: 0.85rem 1rem; 
      border-bottom: 2px solid #fed7aa; 
      font-size: 0.78rem; 
      color: #9a3412; 
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 700;
    }
    td { 
      padding: 0.95rem 1rem; 
      border-bottom: 1px solid #ffedd5; 
      font-size: 0.92rem; 
      color: #292524;
    }
    tr:hover td {
      background: #fff7ed;
    }
    
    .sev-critical { 
      background: #fee2e2;
      color: #b91c1c; 
      border: 1px solid #fca5a5;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 700;
      display: inline-block;
    }
    .sev-high { 
      background: #ffedd5;
      color: #c2410c; 
      border: 1px solid #fdba74;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 700;
      display: inline-block;
    }
    .sev-normal { 
      background: #fef9c3;
      color: #854d0e; 
      border: 1px solid #fde047;
      padding: 0.25rem 0.6rem;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 700;
      display: inline-block;
    }
    
    .status-tag {
      display: inline-block;
      padding: 0.25rem 0.65rem;
      border-radius: 6px;
      font-size: 0.78rem;
      font-weight: 600;
      background: #fff7ed;
      color: #9a3412;
      border: 1px solid #ffedd5;
    }
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <div>
        <h1>☀️ AeroWeather Sentinel</h1>
        <small style="color: #9a3412; font-weight: 500;">Aviation Meteorological Advisory & Micro-Climate Telemetry Dispatch</small>
      </div>
      <div>
        <span class="badge-live">Telemetry Engine v1.0 • ACTIVE</span>
      </div>
    </div>

    <div class="meta-bar">
      <div class="meta-card">
        <div class="meta-title">Serving Pod Replica</div>
        <div class="meta-value meta-code">{{ hostname }}</div>
      </div>
      <div class="meta-card">
        <div class="meta-title">Deployment Strategy</div>
        <div class="meta-value">Kubernetes Rolling Update</div>
      </div>
      <div class="meta-card">
        <div class="meta-title">Continuous Integration</div>
        <div class="meta-value" style="color: #ea580c;">Automated via Jenkins</div>
      </div>
    </div>

    <div class="panel">
      <h2>Broadcast New Airfield Observation</h2>
      <form class="form-grid" method="POST" action="/create">
        <input type="text" name="station" placeholder="Station (e.g. VIDP Delhi)" required>
        <input type="text" name="condition" placeholder="Condition (e.g. High Crosswind)" required>
        <input type="text" name="wind" placeholder="Wind (e.g. 18 kts)" required>
        <select name="severity">
          <option value="CRITICAL">CRITICAL</option>
          <option value="HIGH">HIGH</option>
          <option value="NORMAL">NORMAL</option>
        </select>
        <button type="submit">Publish</button>
      </form>
    </div>

    <div class="panel">
      <h2>Active Flight Advisory Feed</h2>
      <table>
        <thead>
          <tr>
            <th>Station / ICAO</th>
            <th>Atmospheric Condition</th>
            <th>Wind Velocity</th>
            <th>Severity Alert</th>
            <th>Dispatched</th>
          </tr>
        </thead>
        <tbody>
          {% for item in advisories %}
          <tr>
            <td class="meta-code" style="font-weight: 700; color: #c2410c;">{{ item.station }}</td>
            <td>{{ item.condition }}</td>
            <td>{{ item.wind_speed }}</td>
            <td>
              <span class="{% if item.severity == 'CRITICAL' %}sev-critical{% elif item.severity == 'HIGH' %}sev-high{% else %}sev-normal{% endif %}">
                {{ item.severity }}
              </span>
            </td>
            <td><span class="status-tag">{{ item.updated }}</span></td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""

@app.route("/")
def index():
    hostname = socket.gethostname()
    return render_template_string(
        TEMPLATE,
        advisories=ADVISORIES,
        hostname=hostname
    )

@app.route("/create", methods=["POST"])
def create_advisory():
    station = request.form.get("station")
    condition = request.form.get("condition")
    wind = request.form.get("wind")
    severity = request.form.get("severity")
    
    if station and condition:
        new_entry = {
            "station": station,
            "condition": condition,
            "wind_speed": wind,
            "visibility": "5.0 km",
            "severity": severity,
            "updated": datetime.datetime.utcnow().strftime("%H:%M UTC")
        }
        ADVISORIES.insert(0, new_entry)
    return redirect(url_for("index"))

@app.route("/health")
def health():
    return {"status": "UP", "service": "aeroweather-sentinel"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)