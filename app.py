from flask import Flask, render_template_string, request, redirect, url_for
import os
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
      background: #0b1120;
      color: #e2e8f0;
      margin: 0;
      padding: 2.5rem 1rem;
    }
    .wrapper { max-width: 960px; margin: auto; }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 1.5rem;
      border-bottom: 1px solid #1e293b;
      margin-bottom: 2rem;
    }
    .header h1 { margin: 0; font-size: 1.6rem; color: #38bdf8; display: flex; align-items: center; gap: 0.5rem; }
    .badge-live {
      background: #022c22; color: #34d399; border: 1px solid #059669;
      padding: 0.35rem 0.8rem; border-radius: 9999px; font-size: 0.8rem; font-weight: 600;
    }
    .meta-bar {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
      margin-bottom: 2rem;
    }
    .meta-card {
      background: #111e38;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 1rem;
    }
    .meta-title { font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; }
    .meta-value { font-size: 1.1rem; font-weight: 600; color: #f8fafc; margin-top: 0.3rem; }
    .meta-code { font-family: monospace; color: #38bdf8; }
    
    .panel {
      background: #111e38;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 1.5rem;
      margin-bottom: 2rem;
    }
    .panel h2 { margin-top: 0; font-size: 1.1rem; color: #f8fafc; }
    
    .form-grid {
      display: grid;
      grid-template-columns: 1.5fr 2fr 1fr 1fr auto;
      gap: 0.75rem;
    }
    input, select, button {
      padding: 0.6rem 0.8rem;
      border-radius: 6px;
      font-size: 0.9rem;
      border: 1px solid #334155;
      background: #0b1120;
      color: #f8fafc;
    }
    button {
      background: #0284c7;
      color: white;
      font-weight: 600;
      border: none;
      cursor: pointer;
      transition: background 0.2s;
    }
    button:hover { background: #0369a1; }
    
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    th { text-align: left; padding: 0.75rem; border-bottom: 1px solid #334155; font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; }
    td { padding: 0.75rem; border-bottom: 1px solid #1e293b; font-size: 0.9rem; }
    
    .sev-critical { color: #f87171; font-weight: 600; }
    .sev-high { color: #fb923c; font-weight: 600; }
    .sev-normal { color: #34d399; font-weight: 600; }
    
    .status-tag {
      display: inline-block;
      padding: 0.2rem 0.55rem;
      border-radius: 4px;
      font-size: 0.75rem;
      font-weight: 600;
      background: #1e293b;
      color: #cbd5e1;
    }
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <div>
        <h1>⚡ AeroWeather Sentinel</h1>
        <small style="color: #64748b;">Aviation Meteorological Advisory & Micro-Climate Telemetry Dispatch</small>
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
        <div class="meta-value" style="color: #34d399;">Automated via Jenkins</div>
      </div>
    </div>

    <div class="panel">
      <h2>Broadcast New Airfield Observation</h2>
      <form class="form-grid" method="POST" action="/create">
        <input type="text" name="station" placeholder="Station (e.g. VIDP Delhi)" required>
        <input type="text" name="condition" placeholder="Condition (e.g. Dense Fog)" required>
        <input type="text" name="wind" placeholder="Wind (e.g. 15 kts)" required>
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
            <td class="meta-code">{{ item.station }}</td>
            <td>{{ item.condition }}</td>
            <td>{{ item.wind_speed }}</td>
            <td class="{% if item.severity == 'CRITICAL' %}sev-critical{% elif item.severity == 'HIGH' %}sev-high{% else %}sev-normal{% endif %}">
              {{ item.severity }}
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
    return render_template_string(
        TEMPLATE,
        advisories=ADVISORIES,
        hostname=os.uname()[1]
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