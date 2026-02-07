from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
import os
from functools import wraps
from config import Config
import models

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


models.init_db()

active_connections = {}


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    status = models.get_current_status()
    return render_template("index.html", status=status)


@app.route("/choose")
def choose_connection():
    status = models.get_current_status()
    if status["status"] != "available":
        return redirect(url_for("index"))
    visitor_name = request.args.get("name", "Anonymous")
    session["visitor_name"] = visitor_name
    return render_template("choose.html", visitor_name=visitor_name)


@app.route("/room/chat")
def chat_room():
    status = models.get_current_status()
    if status["status"] != "available":
        return redirect(url_for("index"))
    if "visitor_id" not in session:
        session["visitor_id"] = os.urandom(16).hex()
    visitor_name = session.get("visitor_name", "Anonymous")
    return render_template("room_chat.html", visitor_name=visitor_name)


@app.route("/room/video")
def video_room():
    status = models.get_current_status()
    if status["status"] != "available":
        return redirect(url_for("index"))
    if "visitor_id" not in session:
        session["visitor_id"] = os.urandom(16).hex()
    visitor_name = session.get("visitor_name", "Anonymous")
    room_name = f"DianeWelcomeWindow-{datetime.now().strftime('%Y%m%d')}"
    return render_template(
        "room_video.html", visitor_name=visitor_name, jitsi_room=room_name
    )


@app.route("/api/status")
def api_status():
    status = models.get_current_status()
    return jsonify(status)


@app.route("/guestbook", methods=["POST"])
def add_guestbook_message():
    data = request.get_json()
    visitor_name = data.get("name", "Anonymous")
    message = data.get("message", "").strip()
    if not message or len(message) > app.config["MAX_MESSAGE_LENGTH"]:
        return jsonify({"error": "Invalid message"}), 400
    models.add_message(visitor_name, message)
    return jsonify({"success": True})


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if (
            username == app.config["ADMIN_USERNAME"]
            and password == app.config["ADMIN_PASSWORD"]
        ):
            session["admin_logged_in"] = True
            session.permanent = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin/login.html", error="Invalid credentials")
    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    status = models.get_current_status()
    messages = models.get_messages(limit=20)
    unread_count = models.get_unread_count()
    visits = models.get_recent_visits(limit=10)
    stats = models.get_visit_stats()
    return render_template(
        "admin/dashboard.html",
        status=status,
        messages=messages,
        unread_count=unread_count,
        visits=visits,
        stats=stats,
        active_count=len(active_connections),
    )


@app.route("/admin/status/update", methods=["POST"])
@admin_required
def update_status():
    data = request.get_json()
    status = data.get("status", "away")
    message = data.get("message", "")
    models.update_status(status, message)
    socketio.emit(
        "status_changed", {"status": status, "message": message}, namespace="/"
    )
    return jsonify({"success": True})


@app.route("/admin/messages/<int:message_id>/read", methods=["POST"])
@admin_required
def mark_read(message_id):
    models.mark_message_read(message_id)
    return jsonify({"success": True})


@socketio.on("connect")
def handle_connect():
    visitor_id = session.get("visitor_id", "unknown")
    visitor_name = session.get("visitor_name", "Anonymous")
    active_connections[request.sid] = {
        "visitor_id": visitor_id,
        "visitor_name": visitor_name,
        "connected_at": datetime.now().isoformat(),
    }
    if app.config["LOG_VISITS"]:
        visit_id = models.log_visit(visitor_name, "chat")
        active_connections[request.sid]["visit_id"] = visit_id
    socketio.emit(
        "visitor_joined",
        {"visitor_name": visitor_name, "count": len(active_connections)},
        room="admin",
    )
    emit(
        "connection_established",
        {"message": "Connected to The Welcome Window", "visitor_name": visitor_name},
    )


@socketio.on("disconnect")
def handle_disconnect():
    if request.sid in active_connections:
        connection = active_connections[request.sid]
        if "visit_id" in connection and app.config["LOG_VISITS"]:
            models.end_visit(connection["visit_id"])
        visitor_name = connection["visitor_name"]
        del active_connections[request.sid]
        socketio.emit(
            "visitor_left",
            {"visitor_name": visitor_name, "count": len(active_connections)},
            room="admin",
        )


@socketio.on("join_admin")
def handle_admin_join():
    if session.get("admin_logged_in"):
        join_room("admin")
        emit("admin_joined", {"status": "success"})


@socketio.on("send_message")
def handle_message(data):
    message = data.get("message", "").strip()
    sender = data.get("sender", "visitor")
    if not message:
        return
    visitor_name = session.get("visitor_name", "Anonymous")
    socketio.emit(
        "new_message",
        {
            "message": message,
            "sender": sender,
            "sender_name": "Diane" if sender == "admin" else visitor_name,
            "timestamp": datetime.now().isoformat(),
        },
    )


@socketio.on("request_game")
def handle_game_request(data):
    game_type = data.get("game_type")
    socketio.emit(
        "game_requested",
        {"game_type": game_type, "requester": session.get("visitor_name", "Anonymous")},
    )


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
