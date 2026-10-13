from flask import Flask, render_template_string
import os

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>CI/CD K8s Demo</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .card { background: #1e293b; padding: 2.5rem; border-radius: 12px; border: 1px solid #38bdf8; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.5); width: 420px; }
    h1 { color: #38bdf8; margin-bottom: 0.5rem; font-size: 1.6rem; }
    p { color: #94a3b8; font-size: 0.95rem; line-height: 1.5; }
    code { background: #0f172a; padding: 0.2rem 0.5rem; border-radius: 4px; color: #f43f5e; }
    .badge { display: inline-block; margin-top: 1rem; background: #10b981; color: #022c22; padding: 0.4rem 1rem; border-radius: 9999px; font-weight: bold; font-size: 0.85rem; }
  </style>
</head>
<body>
  <div class="card">
    <h1>🚀 CI/CD Pipeline Demo</h1>
    <p>Dockerized Web Application deployed automatically via <strong>Jenkins</strong> to a <strong>Kubernetes</strong> cluster.</p>
    <p>Served by Pod: <code>{{ hostname }}</code></p>
    <span class="badge">Version 1.0 — Running Live</span>
  </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(TEMPLATE, hostname=os.uname()[1])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)