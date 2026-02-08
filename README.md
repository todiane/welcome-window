Create this file:

**README.md**

```markdown
# The Welcome Window

A personal connection portal that signals availability and facilitates spontaneous online connections through text chat, games, and video calls.

## Overview

The Welcome Window is a Flask-based web application designed to address loneliness and facilitate community building by providing a "warm-up phase" before offline connections. It serves as a digital space where you can signal availability and allow people to connect spontaneously without the pressure of formal group events.

## Features

### For Visitors
- **Real-time availability status** - See when the host is available, busy, or away
- **Visitor approval system** - Request access with name and email
- **Two connection modes:**
  - **Chat & Games** (primary mode) - Text chat with Word Search and Sudoku
  - **Video Chat** - Jitsi Meet integration with chat sidebar
- **Guest book** - Leave messages when host is unavailable

### For Admins
- **Live chat interface** - Real-time communication with all visitors
- **Visitor management** - Approve/reject access requests, disconnect visitors
- **Availability controls** - Set status (available/busy/away) with custom messages
- **Analytics dashboard** - Track visits, duration, and engagement
- **Guest book management** - View and respond to visitor messages
- **Browser notifications** - Get notified of new visitor requests and messages

### Games
- **Word Search** - Multiple themes (general, Christmas) with customizable grid sizes
- **Sudoku** - Three difficulty levels (easy, medium, hard) with solution checking

## Tech Stack

- **Backend:** Flask 3.1.0, Flask-SocketIO 5.4.1
- **Frontend:** Tailwind CSS, Alpine.js
- **Real-time:** Socket.IO (WebSocket communication)
- **Database:** SQLite with WAL mode
- **Video:** Jitsi Meet (embedded)
- **Deployment:** Caddy (reverse proxy + SSL), systemd service
- **Server:** VPS with Ubuntu

## Installation

### Prerequisites
- Python 3.8+
- pip and venv

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/welcome-window.git
cd welcome-window
```

2. **Run the start script**
```bash
chmod +x start.sh
./start.sh
```

The script will:
- Create a virtual environment
- Install dependencies
- Initialize the database
- Start the application at http://localhost:5000

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "import models; models.init_db()"

# Run the application
python app.py
```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
SECRET_KEY=your-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
```

### Admin Credentials

Default credentials (change in production):
- **Username:** admin
- **Password:** changeme123

Access the admin panel at: http://localhost:5000/admin/login

## Project Structure

```
welcome-window/
├── app.py                      # Main Flask application
├── models.py                   # Database models and functions
├── config.py                   # Application configuration
├── requirements.txt            # Python dependencies
├── start.sh                    # Local development script
├── templates/
│   ├── base.html              # Base template
│   ├── index.html             # Landing page with availability status
│   ├── waiting_room.html      # Visitor approval waiting page
│   ├── choose.html            # Connection mode selection
│   ├── room_chat.html         # Chat & Games room
│   ├── room_video.html        # Video chat room
│   └── admin/
│       ├── login.html         # Admin login
│       └── dashboard.html     # Admin control panel
├── static/
│   └── js/
│       ├── wordsearch.js      # Word Search game implementation
│       └── sudoku.js          # Sudoku game implementation
├── games/
│   ├── wordsearch_generator.py
│   └── sudoku_generator.py
└── welcome_window.db          # SQLite database (auto-created)
```

## Usage

### For Visitors

1. Visit the site and check availability status
2. If available, click "Request Access" and enter your name and email
3. Wait for admin approval in the waiting room
4. Choose between "Chat & Games" or "Video Chat"
5. Start connecting!

### For Admins

1. Log in at `/admin/login`
2. Set your availability status (Available/Busy/Away)
3. Approve or reject visitor access requests
4. Chat with visitors in real-time
5. Monitor active connections and visitor history
6. Manage guest book messages

## Database Schema

- **availability** - Current status and custom message
- **messages** - Guest book messages
- **visits** - Visit logs with duration tracking
- **pending_visitors** - Access requests awaiting approval
- **chat_messages** - Persistent chat history

## Deployment

The application is designed to be deployed on a VPS with:
- Caddy for reverse proxy and automatic SSL
- systemd for process management
- SQLite in WAL mode for concurrent access

See deployment script in `deploy.sh` for production deployment steps.

## API Endpoints

### Public Endpoints
- `GET /` - Landing page
- `POST /request-access` - Submit access request
- `GET /waiting-room` - Approval waiting page
- `GET /choose` - Connection mode selection
- `GET /room/chat` - Chat & Games room
- `GET /room/video` - Video chat room
- `GET /api/game/wordsearch` - Generate Word Search puzzle
- `GET /api/game/sudoku` - Generate Sudoku puzzle
- `POST /guestbook` - Submit guest book message

### Admin Endpoints
- `POST /admin/login` - Admin authentication
- `GET /admin` - Admin dashboard
- `POST /admin/status/update` - Update availability status
- `POST /admin/visitor/{id}/approve` - Approve visitor
- `POST /admin/visitor/{id}/reject` - Reject visitor
- `POST /admin/visitor/{id}/disconnect` - Disconnect visitor
- `POST /admin/chat/message/{id}/delete` - Delete chat message
- `POST /admin/chat/clear` - Clear chat history

## Socket.IO Events

### Client → Server
- `send_message` - Send chat message
- `join_admin` - Join admin room
- `request_game` - Request to start a game

### Server → Client
- `connection_established` - Connection confirmed
- `new_message` - New chat message received
- `status_changed` - Availability status updated
- `visitor_joined` - New visitor connected (admin only)
- `visitor_left` - Visitor disconnected (admin only)
- `approval_granted` - Access request approved
- `approval_rejected` - Access request rejected
- `force_disconnect` - Admin disconnected visitor
- `message_deleted` - Message removed from chat
- `chat_cleared` - Chat history cleared

## Security Considerations

- Admin credentials should be changed from defaults
- Use environment variables for sensitive configuration
- HTTPS is required for production (handled by Caddy)
- Session-based authentication for admin panel
- Input validation and sanitization on all user inputs
- Rate limiting recommended for production

## Browser Support

- Modern browsers with WebSocket support
- Chrome, Firefox, Safari, Edge (latest versions)
- Mobile browsers supported

## Contributing

This is a personal project, but feedback and suggestions are welcome! Please open an issue to discuss proposed changes.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Built with Flask and Socket.IO
- Video chat powered by Jitsi Meet
- Styled with Tailwind CSS
- Interactive elements with Alpine.js

## Author

**Diane** - UK-based Django/Flask developer
- GitHub: [@djangify](https://github.com/djangify)
- Website: [todiane.com](https://todiane.com)

---

**The Welcome Window** - Because sometimes we all need a digital space to connect 
```

