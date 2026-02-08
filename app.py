from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime
import os
from functools import wraps
from config import Config
import models
from games import sudoku_generator
from games import wordsearch_generator

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

models.init_db()

# Track active connections with their socket IDs
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


@app.route("/request-access", methods=["POST"])
def request_access():
    """Visitor requests access with name and email"""
    data = request.get_json()
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()

    if not name or not email:
        return jsonify({"error": "Name and email required"}), 400

    # Check if visitor already has a pending request
    if "visitor_session" in session:
        existing = models.get_visitor_by_session(session["visitor_session"])
        if existing and not existing["approved"] and not existing["rejected"]:
            # Already pending, just update name/email and redirect
            session["visitor_name"] = name
            session["visitor_email"] = email
            return jsonify({"success": True, "session_id": session["visitor_session"]})

    # Create new session
    session["visitor_session"] = os.urandom(16).hex()

    visitor_id = models.create_pending_visitor(name, email, session["visitor_session"])
    session["visitor_name"] = name
    session["visitor_email"] = email

    # Notify admin in real-time
    socketio.emit(
        "new_visitor_request",
        {
            "id": visitor_id,
            "name": name,
            "email": email,
            "requested_at": datetime.now().isoformat(),
        },
        room="admin",
    )

    return jsonify({"success": True, "session_id": session["visitor_session"]})


@app.route("/check-approval")
def check_approval():
    """Check if visitor has been approved"""
    session_id = session.get("visitor_session")
    if not session_id:
        return jsonify({"approved": False, "rejected": False})

    visitor = models.get_visitor_by_session(session_id)
    if not visitor:
        return jsonify({"approved": False, "rejected": False})

    return jsonify(
        {"approved": bool(visitor["approved"]), "rejected": bool(visitor["rejected"])}
    )


@app.route("/waiting-room")
def waiting_room():
    """Waiting room for visitors pending approval"""
    status = models.get_current_status()
    if status["status"] != "available":
        return redirect(url_for("index"))

    visitor_name = session.get("visitor_name", "Anonymous")
    return render_template("waiting_room.html", visitor_name=visitor_name)


@app.route("/choose")
def choose_connection():
    status = models.get_current_status()
    if status["status"] != "available":
        return redirect(url_for("index"))

    # Check if visitor is approved
    session_id = session.get("visitor_session")
    if session_id:
        visitor = models.get_visitor_by_session(session_id)
        if not visitor or not visitor["approved"]:
            return redirect(url_for("waiting_room"))
    else:
        return redirect(url_for("index"))

    visitor_name = session.get("visitor_name", "Anonymous")
    return render_template("choose.html", visitor_name=visitor_name)


@app.route("/room/chat")
def chat_room():
    status = models.get_current_status()
    if status["status"] != "available":
        return redirect(url_for("index"))

    # Check approval
    session_id = session.get("visitor_session")
    if session_id:
        visitor = models.get_visitor_by_session(session_id)
        if not visitor or not visitor["approved"]:
            return redirect(url_for("waiting_room"))
    else:
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

    # Check approval
    session_id = session.get("visitor_session")
    if session_id:
        visitor = models.get_visitor_by_session(session_id)
        if not visitor or not visitor["approved"]:
            return redirect(url_for("waiting_room"))
    else:
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


@app.route("/api/game/wordsearch")
def api_wordsearch():
    """Generate a new word search puzzle"""
    theme = request.args.get("theme", "general")
    size = int(request.args.get("size", 12))
    puzzle = wordsearch_generator.generate_wordsearch(theme, size)
    return jsonify(puzzle)


@app.route("/api/game/sudoku")
def api_sudoku():
    """Generate a new sudoku puzzle"""
    difficulty = request.args.get("difficulty", "medium")
    puzzle = sudoku_generator.generate_sudoku(difficulty)
    return jsonify(puzzle)


@app.route("/guestbook", methods=["POST"])
def add_guestbook_message():
    data = request.get_json()
    visitor_name = data.get("name", "Anonymous")
    message = data.get("message", "").strip()
    if not message or len(message) > app.config["MAX_MESSAGE_LENGTH"]:
        return jsonify({"error": "Invalid message"}), 400
    models.add_message(visitor_name, message)

    # Notify admin
    socketio.emit(
        "new_guestbook_message",
        {"name": visitor_name, "message": message},
        room="admin",
    )

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
    pending = models.get_pending_visitors()
    return render_template(
        "admin/dashboard.html",
        status=status,
        messages=messages,
        unread_count=unread_count,
        visits=visits,
        stats=stats,
        active_count=len(active_connections),
        pending_visitors=pending,
    )


@app.route("/admin/pending-visitors")
@admin_required
def get_pending_visitors_api():
    pending = models.get_pending_visitors()
    return jsonify(pending)


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


@app.route("/admin/visitor/<int:visitor_id>/approve", methods=["POST"])
@admin_required
def approve_visitor(visitor_id):
    models.approve_visitor(visitor_id)
    socketio.emit("approval_granted", {"visitor_id": visitor_id}, namespace="/")
    return jsonify({"success": True})


@app.route("/admin/visitor/<int:visitor_id>/reject", methods=["POST"])
@admin_required
def reject_visitor(visitor_id):
    models.reject_visitor(visitor_id)
    socketio.emit("approval_rejected", {"visitor_id": visitor_id}, namespace="/")
    return jsonify({"success": True})


@app.route("/admin/visitor/<visitor_id>/disconnect", methods=["POST"])
@admin_required
def disconnect_visitor(visitor_id):
    """Disconnect a specific visitor"""
    for sid, conn in list(active_connections.items()):
        if conn["visitor_id"] == visitor_id:
            socketio.emit(
                "force_disconnect", {"reason": "Disconnected by admin"}, room=sid
            )
            # The actual disconnect will be handled by the client
            return jsonify({"success": True})
    return jsonify({"error": "Visitor not found"}), 404


@app.route("/admin/messages/<int:message_id>/read", methods=["POST"])
@admin_required
def mark_read(message_id):
    models.mark_message_read(message_id)
    return jsonify({"success": True})


@app.route("/admin/chat/message/<int:message_id>/delete", methods=["POST"])
@admin_required
def delete_chat_message(message_id):
    """Delete a specific chat message"""
    models.delete_chat_message(message_id)
    socketio.emit("message_deleted", {"message_id": message_id}, room="admin")
    socketio.emit("message_deleted", {"message_id": message_id}, broadcast=True)
    return jsonify({"success": True})


@app.route("/admin/chat/clear", methods=["POST"])
@admin_required
def clear_chat_history():
    """Clear all chat messages"""
    models.clear_all_chat_messages()
    socketio.emit("chat_cleared", {}, room="admin")
    socketio.emit("chat_cleared", {}, broadcast=True)
    return jsonify({"success": True})


@socketio.on("connect")
def handle_connect(auth=None):
    # Don't track admin connections as visitors
    if session.get("admin_logged_in"):
        return

    visitor_id = session.get("visitor_id", "unknown")
    visitor_name = session.get("visitor_name", "Anonymous")

    # Store connection info
    active_connections[request.sid] = {
        "visitor_id": visitor_id,
        "visitor_name": visitor_name,
        "connected_at": datetime.now().isoformat(),
        "sid": request.sid,
    }

    if app.config["LOG_VISITS"]:
        visit_id = models.log_visit(visitor_name, "chat")
        active_connections[request.sid]["visit_id"] = visit_id

    # Notify admin room about new visitor
    socketio.emit(
        "visitor_joined",
        {
            "sid": request.sid,
            "visitor_name": visitor_name,
            "visitor_id": visitor_id,
            "count": len(active_connections),
            "connected_at": datetime.now().isoformat(),
        },
        room="admin",
    )

    # Send connection confirmation WITHOUT chat history
    # Chat history should NOT be shared between visitors
    emit(
        "connection_established",
        {
            "message": "Connected to The Welcome Window",
            "visitor_name": visitor_name,
        },
    )


@socketio.on("disconnect")
def handle_disconnect():
    if request.sid in active_connections:
        connection = active_connections[request.sid]
        if "visit_id" in connection and app.config["LOG_VISITS"]:
            models.end_visit(connection["visit_id"])
        visitor_name = connection["visitor_name"]
        visitor_id = connection["visitor_id"]

        # Remove from active_connections
        del active_connections[request.sid]

        # Notify admin room with socket ID to remove
        socketio.emit(
            "visitor_left",
            {
                "visitor_name": visitor_name,
                "visitor_id": visitor_id,
                "sid": request.sid,
                "count": len(active_connections),
            },
            room="admin",
        )


@socketio.on("join_admin")
def handle_join_admin():
    """Admin joins the admin room to receive real-time updates"""
    join_room("admin")

    # Send current active connections to admin
    connections_list = [
        {
            "sid": sid,
            "visitor_id": conn["visitor_id"],
            "visitor_name": conn["visitor_name"],
            "connected_at": conn["connected_at"],
        }
        for sid, conn in active_connections.items()
    ]

    # Send chat history
    chat_history = models.get_chat_messages(limit=100)

    emit(
        "admin_joined",
        {"active_connections": connections_list, "chat_history": chat_history},
    )


@socketio.on("send_message")
def handle_message(data):
    message = data.get("message", "").strip()
    sender = data.get("sender", "visitor")

    if not message:
        return

    visitor_name = session.get("visitor_name", "Anonymous")
    visitor_id = session.get("visitor_id")
    timestamp = datetime.now().isoformat()

    if sender == "admin":
        # Admin sending message - broadcast to all visitors
        msg_data = {
            "message": message,
            "sender": "admin",
            "sender_name": "Diane",
            "timestamp": timestamp,
        }

        # Save to database
        msg_id = models.save_chat_message("admin", "Diane", message)
        msg_data["id"] = msg_id

        # Send to ALL connected sockets (including admin)
        socketio.emit("new_message", msg_data, namespace="/")

    else:
        # Visitor sending message
        msg_data = {
            "message": message,
            "sender": "visitor",
            "sender_name": visitor_name,
            "visitor_id": visitor_id,
            "timestamp": timestamp,
        }

        # Save to database
        msg_id = models.save_chat_message("visitor", visitor_name, message, visitor_id)
        msg_data["id"] = msg_id

        # Echo back to sender immediately
        emit("new_message", msg_data)

        # Send to admin room
        socketio.emit("new_message", msg_data, room="admin")


@socketio.on("request_game")
def handle_game_request(data):
    game_type = data.get("game_type")
    socketio.emit(
        "game_requested",
        {"game_type": game_type, "requester": session.get("visitor_name", "Anonymous")},
    )


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
