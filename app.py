from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import platform
import subprocess
import re
import speedtest
import psutil
import matplotlib.pyplot as plt
from models import db, WiFiNetwork  # only if you're using your models file

app = Flask(__name__)
app.secret_key = "wifi23"

# --- Database path ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)  # Uncomment if using SQLAlchemy models

# -------------------------------------------------------------------
# 🔹 Wi-Fi Helper Function: get connected SSID
# -------------------------------------------------------------------
def get_connected_wifi_ssid():
    """Detect the currently connected Wi-Fi SSID."""
    system_platform = platform.system().lower()

    try:
        if "windows" in system_platform:
            result = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                encoding="utf-8"
            )
            match = re.search(r"SSID\s*:\s*(.+)", result)
            return match.group(1).strip() if match else "Unknown"

        elif "linux" in system_platform:
            result = subprocess.check_output(
                ["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"],
                encoding="utf-8"
            )
            for line in result.splitlines():
                if line.startswith("yes:"):
                    return line.split(":", 1)[1]
            return "Unknown"

        else:
            return "Unsupported OS"
    except Exception as e:
        print("Wi-Fi SSID check error:", e)
        return "Unknown"

# -------------------------------------------------------------------
# 🔹 ROUTES
# -------------------------------------------------------------------

@app.route("/")
def about():
    """Landing page."""
    return render_template("about.html")

# ---------------- Register Wi-Fi ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        ssid = request.form.get("ssid")
        security = request.form.get("security")
        password = request.form.get("password")
        interval = request.form.get("interval")
        brand = request.form.get("brand")

        if ssid and security and brand:
            try:
                new_network = WiFiNetwork(
                    ssid=ssid,
                    security=security,
                    password=password,
                    interval=interval,
                    brand=brand
                )
                db.session.add(new_network)
                db.session.commit()
                flash("Wi-Fi Registered Successfully!", "success")
                return redirect(url_for("main"))
            except Exception as e:
                db.session.rollback()
                flash("Registration failed. Please try again.", "danger")
        else:
            flash("Please fill in all required fields.", "warning")

    ssid = request.args.get("ssid", "")
    return render_template("register.html", ssid=ssid)

# ---------------- MAIN DASHBOARD ----------------
@app.route("/main")
def main():
    """Main dashboard page showing network info and graphs."""
    # --- Speed Test ---
    try:
        st = speedtest.Speedtest()
        download_speed = round(st.download() / 1_000_000, 2)
        upload_speed = round(st.upload() / 1_000_000, 2)
    except Exception:
        download_speed = 0
        upload_speed = 0

    # --- Data Usage ---
    net_io = psutil.net_io_counters()
    total_used_gb = round((net_io.bytes_sent + net_io.bytes_recv) / (1024 ** 3), 2)

    # --- Generate Speed Graph ---
    time_stamps = [f"{i}s" for i in range(1, 6)]
    try:
        speeds = [round(st.download() / 1_000_000, 2) for _ in range(5)]
    except Exception:
        speeds = [0, 0, 0, 0, 0]

    plt.figure(figsize=(4, 2))
    plt.plot(time_stamps, speeds, marker='o')
    plt.title("Network Speed Over Time")
    plt.xlabel("Time")
    plt.ylabel("Speed (Mbps)")
    plt.tight_layout()
    graph_filename = "speed_plot.png"
    graph_path = os.path.join("static", graph_filename)
    plt.savefig(graph_path)
    plt.close()

    return render_template("main.html",
                           download_speed=download_speed,
                           upload_speed=upload_speed,
                           total_used=total_used_gb,
                           graph_image=graph_filename)

# ---------------- SPEED TEST ----------------
@app.route('/speedtest')
def run_speedtest():
    """Run speed test when called via JS fetch()."""
    try:
        st = speedtest.Speedtest()
        download = round(st.download() / 1_000_000, 2)
        upload = round(st.upload() / 1_000_000, 2)
        return jsonify({'download': download, 'upload': upload})
    except Exception:
        return jsonify({'download': 0, 'upload': 0})

# ---------------- LATENCY CHECK ----------------
@app.route('/get_latency')
def get_latency():
    """Ping Google DNS and return latency in ms."""
    try:
        if platform.system().lower() == "windows":
            ping_output = subprocess.check_output(["ping", "8.8.8.8", "-n", "1"], encoding='utf-8')
            match = re.search(r"Average = (\d+)ms", ping_output)
        else:
            ping_output = subprocess.check_output(["ping", "-c", "1", "8.8.8.8"], encoding='utf-8')
            match = re.search(r"time=(\d+\.\d+)", ping_output)

        latency = float(match.group(1)) if match else -1
        return jsonify({"latency": latency})
    except Exception:
        return jsonify({"latency": -1})

# ---------------- PASSWORD CHANGER ----------------
@app.route("/password_changer")
def password_changer():
    """Privacy popup and password changer setup."""
    return render_template("password_changer.html", data=None, success=False, message=None)

# ---------------- USER LIST ----------------
authorized_users = []  # In-memory list (no DB use)

@app.route("/user-list", methods=["GET", "POST"])
def user_list():
    """Add or check authorized Wi-Fi SSIDs."""
    message = None
    unauthorized = False

    if request.method == "POST":
        ssid = request.form.get("ssid")
        if ssid and ssid not in authorized_users:
            authorized_users.append(ssid)
            message = f"{ssid} added to authorized list."

    current_ssid = get_connected_wifi_ssid()
    if current_ssid not in authorized_users and authorized_users:
        unauthorized = True

    return render_template(
        "user_list.html",
        authorized_users=authorized_users,
        current_ssid=current_ssid,
        message=message,
        unauthorized=unauthorized
    )

@app.route("/remove-ssid", methods=["POST"])
def remove_ssid():
    ssid_to_remove = request.form.get("ssid_to_remove")
    if ssid_to_remove in authorized_users:
        authorized_users.remove(ssid_to_remove)
    return redirect("/user-list")

# ---------------- HELP PAGE ----------------
@app.route("/help")
def help_page():
    return render_template("help.html")

# ---------------- 404 HANDLER ----------------
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# ---------------- MAIN ENTRY ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
